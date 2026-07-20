from django.contrib import admin
from django.utils.html import format_html

from .models import GalleryAlbum, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0
    readonly_fields = ("id", "image_preview", "image_url", "storage_path", "uploaded_by", "created_at")
    fields = ("image_preview", "title", "caption", "image_url", "storage_path", "uploaded_by", "created_at")

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height:80px; border-radius:4px;" />',
                obj.image_url,
            )
        return "—"

    image_preview.short_description = "Preview"


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_published",
        "image_count",
        "cover_preview",
        "created_by",
        "created_at",
    )
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("id", "cover_preview", "created_at", "updated_at")
    inlines = [GalleryImageInline]

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = "Images"

    def cover_preview(self, obj):
        if obj.cover_image_url:
            return format_html(
                '<img src="{}" style="max-height:80px; border-radius:4px;" />',
                obj.cover_image_url,
            )
        return "—"

    cover_preview.short_description = "Cover"

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "album",
        "uploaded_by",
        "created_at",
    )
    list_filter = ("album", "created_at")
    search_fields = ("title", "caption", "album__title")
    readonly_fields = ("id", "image_preview", "storage_path", "uploaded_by", "created_at")

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height:80px; border-radius:4px;" />',
                obj.image_url,
            )
        return "—"

    image_preview.short_description = "Preview"

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
