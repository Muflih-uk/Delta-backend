from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import (
    IsInternOrAdmin,
)

from .models import (
    Announcement,
    Course,
    CourseMaterial,
)
from .serializers import (
    AnnouncementSerializer,
    CourseMaterialSerializer,
    CourseSerializer,
)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [
            IsAuthenticated(),
            IsInternOrAdmin(),
        ]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.filter(is_published=True)

        if user.role == user.Role.STUDENT:
            return Course.objects.filter(is_published=True)

        return Course.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()

    serializer_class = CourseMaterialSerializer

    permission_classes = [
        IsAuthenticated,
        IsInternOrAdmin,
    ]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()

    serializer_class = AnnouncementSerializer

    permission_classes = [
        IsAuthenticated,
        IsInternOrAdmin,
    ]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
