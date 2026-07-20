import uuid

from django.conf import settings
from django.db import models


class GalleryAlbum(models.Model):
    """
    A named collection/category for grouping gallery images.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="gallery_albums_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gallery_albums"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published"]),
        ]

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    """
    A single image belonging to a GalleryAlbum.
    The image file is uploaded to Supabase Storage; only the public URL is stored here.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(
        GalleryAlbum,
        on_delete=models.CASCADE,
        related_name="images",
    )
    title = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    image_url = models.URLField()
    # Internal storage path so we can delete from Supabase later
    storage_path = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="gallery_app_images_uploaded",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gallery_app_images"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["album"]),
        ]

    def __str__(self):
        return self.title or f"Image {self.id} in {self.album}"
