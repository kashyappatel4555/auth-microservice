from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.core.mail import send_mail
from auth_service import settings

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'password']

    def validate(self, attrs):
        if 'password' in attrs:
            password = attrs['password']
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        otp = get_random_string(6, '0123456789')
        user.otp = otp
        user.otp_created_at = now()
        user.save()

        send_mail(
            'Verify Your Email',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return user

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class OTPLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class OTPLoginVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        """Ensure that new password and confirm password match"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

class AccountUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password']

    def validate_phone_number(self, value):
        """Ensure the phone number is unique, except for the current user"""
        if User.objects.exclude(id=self.instance.id).filter(phone_number=value).exists():
            raise ValidationError("A user with this phone number already exists.")
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)  # Encrypt password
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance