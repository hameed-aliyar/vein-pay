# api/views.py

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Wallet, Transaction, BiometricData, Bill, User
from .permissions import IsShopOwner
from .serializers import (
    WalletSerializer, TransactionSerializer, AddMoneySerializer,
    CustomerRegistrationSerializer, BillCreationSerializer, PaymentSerializer, 
    CustomerRegistrationResponseSerializer, UserListSerializer
)
from .vein_utils import enroll_vein_user, verify_vein_user
from rest_framework.permissions import IsAuthenticated
import requests

# -------------------------
# Wallet / Transactions
# -------------------------

class WalletDetailView(generics.RetrieveAPIView):
    """Endpoint for the logged-in user to see their wallet details."""
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(owner=self.request.user)
        return wallet


class AddMoneyView(generics.GenericAPIView):
    """Endpoint for the logged-in user to add money to their wallet."""
    serializer_class = AddMoneySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        wallet = request.user.wallet
        wallet.balance += amount
        wallet.save()

        return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)


class TransactionHistoryView(generics.ListAPIView):
    """Endpoint to view all transactions for the logged-in user."""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_wallet = self.request.user.wallet
        from django.db.models import Q
        return Transaction.objects.filter(
            Q(source_wallet=user_wallet) | Q(destination_wallet=user_wallet)
        ).order_by('-timestamp')


# -------------------------
# Customers / Bills
# -------------------------

from .vein_utils import enroll_vein_user  # import the Flask helper

# views.py

class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role='CUSTOMER')
    def get_serializer_class(self):
        # Use different serializers for GET vs POST
        if self.request.method == 'GET':
            return UserListSerializer
        return CustomerRegistrationSerializer
    permission_classes = [IsShopOwner]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()
            Wallet.objects.get_or_create(owner=user)

            biometric_type = serializer.validated_data.get('biometric_type')
            face_template = serializer.validated_data.get('face_template')
            vein_image = serializer.validated_data.get('vein_image')

            # Ensure only one BiometricData record per user
            bio, created = BiometricData.objects.get_or_create(owner=user)
            bio.biometric_type = biometric_type

            if biometric_type == 'FACE' and face_template:
                bio.face_template = face_template
            elif biometric_type == 'VEIN' and vein_image:
                embedding = enroll_vein_user(user.id, vein_image)
                bio.vein_embedding_json = embedding
            bio.save()

        response_data = {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        return Response(response_data, status=201)
    
    def perform_create(self, serializer):
        user = serializer.save(role='CUSTOMER') 


class BillListCreateView(generics.ListCreateAPIView):
    """Shop Owner can list all bills or create a new bill."""
    queryset = Bill.objects.all().order_by("-created_at")
    serializer_class = BillCreationSerializer
    permission_classes = [IsShopOwner]

    def perform_create(self, serializer):
        serializer.save(initiating_shop=self.request.user)


# -------------------------
# Payment / Cash
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Bill, Transaction, BiometricData
from .serializers import PaymentSerializer
from .vein_utils import verify_vein_user

class PaymentView(generics.GenericAPIView):
    """
    Process payment for a bill using wallet, VEIN-only.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bill_id = serializer.validated_data['bill_id']
        live_image = serializer.validated_data['live_image']

        # Fetch the bill
        bill = get_object_or_404(Bill, id=bill_id, status='PENDING')
        customer = bill.customer
        shop = bill.initiating_shop

        # --- VEIN Biometric Authentication ---
        try:
            bio = customer.biometric_data
        except BiometricData.DoesNotExist:
            return Response(
                {"live_image": ["No registered biometric data."]},
                status=400
            )

        if not bio.vein_embedding_json:
            return Response(
                {"live_image": ["No vein embedding stored for this user."]},
                status=400
            )

        # Verify vein with Flask service
        live_image.seek(0)
        try:
            is_authenticated = verify_vein_user(
                stored_embedding=bio.vein_embedding_json,
                live_image=live_image,
                threshold=0.3
            )
        except Exception as e:
            return Response(
                {"error": f"Vein verification failed: {str(e)}"},
                status=502
            )

        if not is_authenticated:
            return Response(
                {"error": "Biometric authentication failed."},
                status=400
            )

        # --- PROCESS PAYMENT ---
        customer_wallet, _ = Wallet.objects.get_or_create(owner=customer)
        shop_wallet, _ = Wallet.objects.get_or_create(owner=shop)
        amount = bill.amount

        if customer_wallet.balance < amount:
            return Response({"error": "Insufficient funds."}, status=400)

        with transaction.atomic():
            customer_wallet.balance -= amount
            shop_wallet.balance += amount
            bill.status = 'PAID_WALLET'

            # Record transaction
            Transaction.objects.create(
                bill=bill,
                source_wallet=customer_wallet,
                destination_wallet=shop_wallet,
                amount=amount
            )

            customer_wallet.save()
            shop_wallet.save()
            bill.save()

        return Response(
            {"success": f"Payment of {amount} for Bill #{bill.id} successful."},
            status=200
        )

# --- CASH PAYMENT ---
class BillPayCashView(generics.UpdateAPIView):
    """Mark a bill as paid in cash."""
    queryset = Bill.objects.all()
    permission_classes = [permissions.IsAuthenticated]  # replace with your IsShopOwner

    def update(self, request, *args, **kwargs):
        bill = self.get_object()
        if bill.status != 'PENDING':
            return Response({"error": "This bill is not pending."}, status=400)
        
        bill.status = 'PAID_CASH'
        bill.save()
        return Response({"success": f"Bill #{bill.id} has been marked as PAID_CASH."}, status=200)


# --- VEIN ENROLLMENT ---
class VeinEnrollmentView(generics.GenericAPIView):
    """
    Enroll a user's vein biometric.
    Accepts image, sends to Flask service, stores embedding in DB.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerRegistrationSerializer  # or minimal serializer

    def post(self, request, *args, **kwargs):
        user = request.user
        image_file = request.FILES.get("vein_image")

        if not image_file:
            return Response({"error": "No image provided."}, status=400)

        try:
            # Send image to Flask service to get embedding
            files = {"image": image_file}
            response = requests.post("http://127.0.0.1:5000/enroll", files=files, timeout=5)
            response.raise_for_status()

            embedding = response.json().get("embedding")
            if not embedding:
                return Response({"error": "No embedding returned from Flask."}, status=500)

            # Store in DB
            bio, _ = BiometricData.objects.get_or_create(owner=user)
            bio.biometric_type = "VEIN"
            bio.vein_embedding_json = embedding
            bio.save()

            return Response({"success": "Vein data enrolled."}, status=200)

        except requests.RequestException as e:
            return Response({"error": f"Flask service error: {str(e)}"}, status=502)