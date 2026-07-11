from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import (
    IsInternOrAdmin,
    IsStudent,
)

from .models import (
    GalleryImage,
    Workshop,
    WorkshopRegistration,
)
from .serializers import (
    GalleryImageSerializer,
    WorkshopSerializer,
    WorkshopRegistrationSerializer,
)


class WorkshopViewSet(viewsets.ModelViewSet):
    queryset = Workshop.objects.prefetch_related(
        "gallery_images",
        "registrations",
    )
    serializer_class = WorkshopSerializer
    permission_classes = [IsInternOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsInternOrAdmin],
    )
    def registrations(self, request, pk=None):
        workshop = self.get_object()

        registrations = WorkshopRegistration.objects.filter(
            workshop=workshop
        )

        serializer = WorkshopRegistrationSerializer(
            registrations,
            many=True,
        )

        return Response(serializer.data)


class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.select_related("workshop")
    serializer_class = GalleryImageSerializer
    permission_classes = [IsInternOrAdmin]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class StudentWorkshopRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = WorkshopRegistrationSerializer
    permission_classes = [IsStudent]

    def create(self, request):

        workshop_id = request.data.get("workshop")

        if not workshop_id:
            return Response(
                {"error": "workshop is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            workshop = Workshop.objects.get(
                id=workshop_id,
                is_published=True,
            )
        except Workshop.DoesNotExist:
            return Response(
                {"error": "Workshop not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if WorkshopRegistration.objects.filter(
            workshop=workshop,
            student=request.user,
        ).exists():
            return Response(
                {
                    "error": "Already registered for this workshop."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration = WorkshopRegistration.objects.create(
            workshop=workshop,
            student=request.user,
        )

        serializer = WorkshopRegistrationSerializer(registration)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def list(self, request):
        registrations = WorkshopRegistration.objects.filter(
            student=request.user
        )

        serializer = WorkshopRegistrationSerializer(
            registrations,
            many=True,
        )

        return Response(serializer.data)
