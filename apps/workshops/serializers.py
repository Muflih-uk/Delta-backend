from rest_framework import serializers

from .models import (
    GalleryImage,
    Workshop,
    WorkshopRegistration,
)


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = "__all__"
        read_only_fields = ("id", "uploaded_by", "created_at")


class WorkshopSerializer(serializers.ModelSerializer):
    gallery_images = GalleryImageSerializer(
        many=True,
        read_only=True,
    )

    total_registrations = serializers.SerializerMethodField()

    class Meta:
        model = Workshop
        fields = [
            "id",
            "title",
            "description",
            "status",
            "event_date",
            "location",
            "image_url",
            "is_published",
            "gallery_images",
            "total_registrations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def get_total_registrations(self, obj):
        return obj.registrations.count()


class WorkshopRegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="student.full_name",
        read_only=True,
    )

    workshop_title = serializers.CharField(
        source="workshop.title",
        read_only=True,
    )

    class Meta:
        model = WorkshopRegistration
        fields = [
            "id",
            "workshop",
            "workshop_title",
            "student",
            "student_name",
            "status",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "student",
            "status",
            "created_at",
        )
