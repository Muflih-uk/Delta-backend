from django.db import transaction
from django.db.models import Count, Q
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
from apps.enrollments.models import Enrollment
from apps.workshops.models import WorkshopRegistration
from core.permissions import IsStudent
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


class StudentDashboardView(APIView):
    """
    GET /api/accounts/dashboard/

    Returns an aggregated dashboard summary for the authenticated student:
      - profile info
      - course enrollment counts (total + per-status breakdown)
      - workshop registration counts (total + per-status breakdown)
      - recent enrollments (last 5)
      - recent workshop registrations (last 5)
      - upcoming workshops the student is registered for
    """

    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user

        # ── Course Enrollment Stats ───────────────────────────────────────────
        enrollment_qs = Enrollment.objects.filter(student=user)

        enrollment_counts = enrollment_qs.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=Enrollment.Status.ACTIVE)),
            pending_payment=Count(
                "id", filter=Q(status=Enrollment.Status.PENDING_PAYMENT)
            ),
            payment_verification=Count(
                "id", filter=Q(status=Enrollment.Status.PAYMENT_VERIFICATION)
            ),
            pending_enrollment=Count(
                "id", filter=Q(status=Enrollment.Status.PENDING_ENROLLMENT)
            ),
            rejected=Count("id", filter=Q(status=Enrollment.Status.REJECTED)),
        )

        # ── Workshop Registration Stats ───────────────────────────────────────
        registration_qs = WorkshopRegistration.objects.filter(student=user)

        registration_counts = registration_qs.aggregate(
            total=Count("id"),
            registered=Count(
                "id", filter=Q(status=WorkshopRegistration.Status.REGISTERED)
            ),
            attended=Count(
                "id", filter=Q(status=WorkshopRegistration.Status.ATTENDED)
            ),
            cancelled=Count(
                "id", filter=Q(status=WorkshopRegistration.Status.CANCELLED)
            ),
        )

        # ── Recent Activity ───────────────────────────────────────────────────
        recent_enrollments = (
            enrollment_qs.select_related("course")
            .order_by("-created_at")[:5]
            .values(
                "id",
                "course__id",
                "course__title",
                "course__thumbnail_url",
                "course__level",
                "status",
                "purchased_at",
                "created_at",
            )
        )

        recent_workshop_registrations = (
            registration_qs.select_related("workshop")
            .order_by("-created_at")[:5]
            .values(
                "id",
                "workshop__id",
                "workshop__title",
                "workshop__image_url",
                "workshop__event_date",
                "workshop__location",
                "workshop__status",
                "status",
                "created_at",
            )
        )

        # ── Upcoming registered workshops ─────────────────────────────────────
        from django.utils import timezone

        upcoming_workshops = (
            registration_qs.select_related("workshop")
            .filter(
                workshop__event_date__gte=timezone.now(),
                status=WorkshopRegistration.Status.REGISTERED,
            )
            .order_by("workshop__event_date")[:5]
            .values(
                "id",
                "workshop__id",
                "workshop__title",
                "workshop__image_url",
                "workshop__event_date",
                "workshop__location",
                "workshop__status",
            )
        )

        return Response(
            {
                "success": True,
                "profile": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": user.get_full_name(),
                    "phone": user.phone,
                    "avatar_url": user.avatar_url,
                    "role": user.role,
                    "member_since": user.created_at,
                },
                "courses": {
                    "total_enrolled": enrollment_counts["total"],
                    "breakdown": {
                        "active": enrollment_counts["active"],
                        "pending_payment": enrollment_counts["pending_payment"],
                        "payment_verification": enrollment_counts[
                            "payment_verification"
                        ],
                        "pending_enrollment": enrollment_counts["pending_enrollment"],
                        "rejected": enrollment_counts["rejected"],
                    },
                },
                "workshops": {
                    "total_registered": registration_counts["total"],
                    "breakdown": {
                        "registered": registration_counts["registered"],
                        "attended": registration_counts["attended"],
                        "cancelled": registration_counts["cancelled"],
                    },
                },
                "recent_enrollments": list(recent_enrollments),
                "recent_workshop_registrations": list(
                    recent_workshop_registrations
                ),
                "upcoming_workshops": list(upcoming_workshops),
            },
            status=status.HTTP_200_OK,
        )
