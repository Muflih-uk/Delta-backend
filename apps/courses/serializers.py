from rest_framework import serializers

from .models import (
    Announcement,
    Course,
    CourseFeedback,
    CourseMaterial,
)


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
        )


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
        )


class CourseFeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = CourseFeedback
        fields = "__all__"
        read_only_fields = (
            "id",
            "student",
            "created_at",
            "updated_at",
        )


class CourseSerializer(serializers.ModelSerializer):
    materials = CourseMaterialSerializer(many=True, read_only=True)
    announcements = AnnouncementSerializer(many=True, read_only=True)
    feedback = CourseFeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )
