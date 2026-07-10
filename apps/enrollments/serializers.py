from rest_framework import serializers

from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
    )

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = (
            "id",
            "student",
            "status",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        )
