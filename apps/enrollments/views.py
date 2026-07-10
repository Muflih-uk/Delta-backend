from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from core.permissions import IsStudent

from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollCourseView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsStudent,
    ]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(
                id=course_id,
                is_published=True,
            )
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
        )

        if not created:
            return Response(
                {"detail": "Already enrolled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EnrollmentSerializer(enrollment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class MyEnrollmentsView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsStudent,
    ]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)

        serializer = EnrollmentSerializer(
            enrollments,
            many=True,
        )

        return Response(serializer.data)
