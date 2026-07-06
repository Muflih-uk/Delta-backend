from django.db import transaction
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from apps.accounts.services import AccountService
from core.storage import StorageService
from core.supabase import supabase


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AccountService.register(serializer.validated_data)

            return Response(
                {
                    "success": True,
                    "message": "Account created successfully.",
                    "user": UserSerializer(result["user"]).data,
                    "access_token": (
                        result["session"].access_token if result["session"] else None
                    ),
                    "refresh_token": (
                        result["session"].refresh_token if result["session"] else None
                    ),
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AccountService.login(
                serializer.validated_data["email"],
                serializer.validated_data["password"],
            )

            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "access_token": (result["session"].access_token),
                    "refresh_token": (result["session"].refresh_token),
                    "user": UserSerializer(result["user"]).data,
                }
            )

        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(APIView):
    """
    Get the authenticated user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            {
                "success": True,
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=False,
        )

        serializer.is_valid(raise_exception=True)

        try:
            user = AccountService.update_profile(
                request.user,
                serializer,
            )

            return Response(
                {
                    "success": True,
                    "message": "Profile updated successfully.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        try:
            user = AccountService.update_profile(
                request.user,
                serializer,
            )

            return Response(
                {
                    "success": True,
                    "message": "Profile updated successfully.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            AccountService.delete(user)

            return Response(
                {
                    "success": True,
                    "message": "Account deleted successfully.",
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "success": True,
                "message": (
                    "Logout successful. "
                    "Remove the access token and refresh token on the client."
                ),
            },
            status=status.HTTP_200_OK,
        )


class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "success": True,
                "user": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        email = request.data.get("email")

        if not email:
            return Response(
                {
                    "success": False,
                    "message": "Email is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            supabase.auth.reset_password_email(email)

            return Response(
                {
                    "success": True,
                    "message": "Password reset email sent.",
                }
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "refresh_token is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = supabase.auth.refresh_session(refresh_token)

            return Response(
                {
                    "success": True,
                    "access_token": session.session.access_token,
                    "refresh_token": session.session.refresh_token,
                }
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        new_password = request.data.get("password")

        if not new_password:
            return Response(
                {
                    "success": False,
                    "message": "password is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = request.headers.get("Authorization")

        if not token:
            return Response(
                {
                    "success": False,
                    "message": "Authorization header missing.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = token.split(" ")[1]

        try:
            client = supabase.auth

            client.set_session(
                access_token,
                request.data.get("refresh_token", ""),
            )

            client.update_user(
                {
                    "password": new_password,
                }
            )

            return Response(
                {
                    "success": True,
                    "message": "Password updated successfully.",
                }
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UploadAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):

        image = request.FILES["avatar"]

        url = StorageService.upload_avatar(
            request.user,
            image,
        )

        return Response(
            {
                "success": True,
                "avatar_url": url,
            }
        )
