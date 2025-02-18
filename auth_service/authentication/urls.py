from django.urls import path
from . import views

urlpatterns = [
    path('', views.APITestView.as_view(), name='api_test'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('login/request-otp/', views.OTPLoginRequestView.as_view(), name='otp_login_request'),
    path('login/verify-otp/', views.OTPLoginVerifyView.as_view(), name='otp_login_verify'),
    path('reset-password-request/', views.PasswordResetRequestView.as_view(), name='reset-password-request'),
    path('reset-password/<str:token>/', views.PasswordResetView.as_view(), name='reset-password'),
    path('update-account/', views.AccountUpdateView.as_view(), name='account-update'),
]
