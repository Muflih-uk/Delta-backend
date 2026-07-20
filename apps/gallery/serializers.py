from rest_framework import serializers

from .models import GalleryAlbum, GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = [
            "id",
            "album",
            "title",
            "caption",
            "image_url",
            "storage_path",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = ("id", "image_url", "storage_path", "uploaded_by", "created_at")

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return None


class GalleryAlbumSerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)
    image_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = GalleryAlbum
        fields = [
            "id",
            "title",
            "description",
            "cover_image_url",
            "is_published",
            "images",
            "image_count",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def get_image_count(self, obj):
        return obj.images.count()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class GalleryAlbumListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (no nested images)."""

    image_count = serializers.SerializerMethodField()

    class Meta:
        model = GalleryAlbum
        fields = [
            "id",
            "title",
            "description",
            "cover_image_url",
            "is_published",
            "image_count",
            "created_at",
            "updated_at",
        ]

    def get_image_count(self, obj):
        return obj.images.count()
