from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnnouncementViewSet,
    CourseMaterialViewSet,
    CourseViewSet,
)

router = DefaultRouter()

router.register(
    "courses",
    CourseViewSet,
    basename="courses",
)

router.register(
    "materials",
    CourseMaterialViewSet,
    basename="materials",
)

router.register(
    "announcements",
    AnnouncementViewSet,
    basename="announcements",
)

urlpatterns = [
    path("", include(router.urls)),
]
