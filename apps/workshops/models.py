import uuid

from django.conf import settings
from django.db import models


class Workshop(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.UPCOMING
    )
    event_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="workshops_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workshops"
        ordering = ["-event_date"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True)
    image_url = models.URLField()
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gallery_images",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="gallery_images_uploaded",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gallery_images"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workshop"])]

    def __str__(self):
        return self.title or f"Gallery image {self.id}"
