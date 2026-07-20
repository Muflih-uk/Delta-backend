from django.urls import path

from .views import (
    DeleteAccountView,
    ForgotPasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
    StudentDashboardView,
    UpdateProfileView,
    VerifyTokenView,
)

app_name = "accounts"

urlpatterns = [
    # Authentication
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    # Token
    path(
        "verify-token/",
        VerifyTokenView.as_view(),
        name="verify-token",
    ),
    path(
        "refresh-token/",
        RefreshTokenView.as_view(),
        name="refresh-token",
    ),
    # Password
    path(
        "forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot-password",
    ),
    path(
        "reset-password/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
    # Profile
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),
    path(
        "profile/update/",
        UpdateProfileView.as_view(),
        name="update-profile",
    ),
    path(
        "profile/delete/",
        DeleteAccountView.as_view(),
        name="delete-account",
    ),
    # Dashboard
    path(
        "dashboard/",
        StudentDashboardView.as_view(),
        name="student-dashboard",
    ),
]
