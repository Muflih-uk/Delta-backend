from django.contrib import admin

from .models import (
    Announcement,
    Course,
    CourseFeedback,
    CourseMaterial,
)


class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 1


class AnnouncementInline(admin.TabularInline):
    model = Announcement
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "level",
        "price",
        "is_published",
        "created_by",
        "created_at",
    )
    list_filter = ("level", "is_published", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [CourseMaterialInline, AnnouncementInline]

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "type",
        "created_by",
        "created_at",
    )
    list_filter = ("type", "created_at")
    search_fields = ("title", "course__title")
    readonly_fields = ("id", "created_at")

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "created_by",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("title", "content", "course__title")
    readonly_fields = ("id", "created_at")

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CourseFeedback)
class CourseFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "student",
        "rating",
        "is_published",
        "created_at",
    )
    list_filter = ("rating", "is_published", "created_at")
    search_fields = (
        "course__title",
        "student__username",
        "comment",
    )
    readonly_fields = ("id", "created_at", "updated_at")
