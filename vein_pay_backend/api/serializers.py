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
    biometric_type = serializers.ChoiceField(
        choices=BiometricData.BIOMETRIC_CHOICES,
        write_only=True
    )

    face_template = serializers.ImageField(write_only=True, required=False)
    vein_image = serializers.ImageField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "biometric_type",
            "face_template",
            "vein_image"
        ]

    def create(self, validated_data):
        print("🔥 VALIDATED DATA:", validated_data)

        biometric_type = validated_data.pop("biometric_type")
        face_template = validated_data.pop("face_template", None)
        vein_image = validated_data.pop("vein_image", None)
        password = validated_data.pop("password")

        username = validated_data.get("username")

        try:
            # 1. Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                role="CUSTOMER"
            )

            # 2. Wallet
            Wallet.objects.create(owner=user)

            # 3. Biometric record
            bio = BiometricData.objects.create(
                owner=user,
                biometric_type=biometric_type
            )

            # 4. FACE
            if biometric_type == "FACE" and face_template:
                bio.face_template = face_template

            # 5. VEIN (SAFE WRAPPED)
            elif biometric_type == "VEIN" and vein_image:
                try:
                    from .vein_utils import enroll_vein_user
                    embedding = enroll_vein_user(user.id, vein_image)
                    bio.vein_embedding_json = embedding
                except Exception as e:
                    user.delete()
                    raise serializers.ValidationError({
                        "vein_image": f"Vein enrollment failed: {str(e)}"
                    })

            bio.save()
            return user

        except Exception as e:
            print("🔥 CREATE CUSTOMER ERROR:", str(e))
            raise
    

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