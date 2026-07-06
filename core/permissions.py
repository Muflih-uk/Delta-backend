from accounts.models import User
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStudent(BasePermission):
    message = "Only students can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STUDENT


class IsIntern(BasePermission):
    message = "Only interns can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.INTERN


class IsAdmin(BasePermission):
    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class IsStudentOrIntern(BasePermission):
    message = "Only students or interns can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.STUDENT,
            User.Role.INTERN,
        ]


class IsInternOrAdmin(BasePermission):
    message = "Only interns or admins can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.INTERN,
            User.Role.ADMIN,
        ]


class IsStudentOrAdmin(BasePermission):
    message = "Only students or admins can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.STUDENT,
            User.Role.ADMIN,
        ]


class IsAnyRole(BasePermission):
    """
    Allow any authenticated user.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated


class ReadOnly(BasePermission):
    """
    Read-only access.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Allow access if:
    - object belongs to the user
    - OR user is an admin
    """

    message = "You do not have permission."

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.user.role == User.Role.ADMIN:
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user

        if hasattr(obj, "owner"):
            return obj.owner == request.user

        return False


class IsOwner(BasePermission):
    """
    Object owner only.
    """

    message = "You are not the owner."

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if hasattr(obj, "user"):
            return obj.user == request.user

        if hasattr(obj, "owner"):
            return obj.owner == request.user

        return False


class IsAdminOrReadOnly(BasePermission):
    """
    Everyone can read.
    Only admins can modify.
    """

    def has_permission(
        self,
        request,
        view,
    ):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class IsStudentReadOnlyInternWrite(BasePermission):
    """
    Students:
        GET only

    Interns:
        Full access

    Admin:
        Full access
    """

    def has_permission(
        self,
        request,
        view,
    ):

        if not request.user.is_authenticated:
            return False

        if request.user.role == User.Role.ADMIN:
            return True

        if request.user.role == User.Role.INTERN:
            return True

        if request.user.role == User.Role.STUDENT:
            return request.method in SAFE_METHODS

        return False


class RolePermission(BasePermission):
    """
    Generic role permission.

    Example:

        class MyView(APIView):
            permission_classes = [RolePermission]
            allowed_roles = [
                User.Role.ADMIN,
                User.Role.INTERN,
            ]
    """

    message = "Permission denied."

    def has_permission(
        self,
        request,
        view,
    ):

        if not request.user.is_authenticated:
            return False

        allowed = getattr(
            view,
            "allowed_roles",
            [],
        )

        return request.user.role in allowed
