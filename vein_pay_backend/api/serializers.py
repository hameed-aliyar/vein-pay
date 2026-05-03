# api/serializers.py

import decimal
from rest_framework import serializers
from .models import Wallet, Transaction, User, Bill, BiometricData
from .face_utils import process_and_validate_face_for_registration  # <--- NEW IMPORT
from rest_framework.exceptions import ValidationError  # <--- NEW IMPORT
from .face_utils import (
    process_and_validate_face_for_registration,
    compare_faces,
    validate_face_present,
)

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

class WalletSerializer(serializers.ModelSerializer):
    # We add this to show the username instead of just the user's ID.
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'owner_username', 'balance', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__' # For now, we'll show all fields.

class AddMoneySerializer(serializers.Serializer):
    # This serializer is not based on a model. It's for validating the input
    # when the user wants to add money.
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=decimal.Decimal('0.01'))


# api/serializers.py

# serializers.py
from rest_framework import serializers
from .models import User, BiometricData

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    biometric_type = serializers.ChoiceField(choices=BiometricData.BIOMETRIC_CHOICES, write_only=True)
    face_template = serializers.ImageField(write_only=True, required=False)
    vein_image = serializers.ImageField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "biometric_type", "face_template", "vein_image"]
    

class BillCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['id', 'customer', 'amount', 'status']

# Add this new serializer at the end of the file
class PaymentSerializer(serializers.Serializer):
    bill_id = serializers.IntegerField()
    live_image = serializers.ImageField()


class CustomerRegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role"]