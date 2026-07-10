from django.urls import path

from .views import (
    EnrollCourseView,
    MyEnrollmentsView,
)

urlpatterns = [
    path(
        "courses/<uuid:course_id>/enroll/",
        EnrollCourseView.as_view(),
        name="enroll-course",
    ),
    path(
        "my-enrollments/",
        MyEnrollmentsView.as_view(),
        name="my-enrollments",
    ),
]
