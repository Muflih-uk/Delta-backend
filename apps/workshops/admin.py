from django.contrib import admin

from .models import (
    GalleryImage,
    Workshop,
    WorkshopRegistration,
)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


class WorkshopRegistrationInline(admin.TabularInline):
    model = WorkshopRegistration
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "event_date",
        "location",
        "is_published",
        "created_by",
        "created_at",gmail
    )
    list_filter = (
        "status",
        "is_published",
        "event_date",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "location",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    inlines = [
        GalleryImageInline,
        WorkshopRegistrationInline,
    ]

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "workshop",
        "uploaded_by",
        "created_at",
    )
    list_filter = (
        "workshop",
        "created_at",
    )
    search_fields = (
        "title",
        "workshop__title",
    )
    readonly_fields = (
        "id",
        "created_at",
    )

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "workshop",
        "student",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "workshop__title",
        "student__username",
        "student__email",
    )
    readonly_fields = (
        "id",
        "created_at",
    )
