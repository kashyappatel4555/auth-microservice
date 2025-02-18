from django.views import generic
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, EmailVerificationSerializer,
    OTPLoginSerializer, OTPLoginVerifySerializer, PasswordResetRequestSerializer,
    PasswordResetSerializer, AccountUpdateSerializer
)
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .utils import generate_otp, send_otp_via_sms
from auth_service import settings

User = get_user_model()

class APITestView(generic.TemplateView):
    template_name = "authentication/api_test.html"

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
            if user.otp == otp:
                user.is_email_verified = True
                user.otp = None
                user.save()
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class OTPLoginRequestView(generics.GenericAPIView):
    serializer_class = OTPLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data["phone_number"]
            try:
                user = User.objects.get(phone_number=phone_number)
                otp = generate_otp()  # Generate OTP
                user.otp = otp
                user.save()

                send_otp_via_sms(phone_number, otp)  # Send OTP via Twilio

                return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPLoginVerifyView(generics.GenericAPIView):
    serializer_class = OTPLoginVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data["phone_number"]
            otp = serializer.validated_data["otp"]

            try:
                user = User.objects.get(phone_number=phone_number)
                if user.otp == otp:
                    user.otp = None
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    return Response(
                        {
                            "message": "OTP verified successfully!",
                            "access_token": access_token,
                            "refresh_token": str(refresh)
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                # Generate password reset token
                token = default_token_generator.make_token(user)
                reset_link = f"http://127.0.0.1:8000/api/auth/reset-password/{token}/"

                # Send email to user with password reset link
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_link}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(generics.GenericAPIView):
    """Reset the user's password using the token from the link"""

    serializer_class = PasswordResetSerializer

    def post(self, request, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            if not email:
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                # Verify the token
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountUpdateView(generics.UpdateAPIView):
    serializer_class = AccountUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response({"error": "A user with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)