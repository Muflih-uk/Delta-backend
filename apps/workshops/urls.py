from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    GalleryImageViewSet,
    StudentWorkshopRegistrationViewSet,
    WorkshopViewSet,
)

router = DefaultRouter()

router.register(
    "workshops",
    WorkshopViewSet,
    basename="workshops",
)

router.register(
    "gallery",
    GalleryImageViewSet,
    basename="gallery",
)

router.register(
    "workshop-registrations",
    StudentWorkshopRegistrationViewSet,
    basename="workshop-registrations",
)

urlpatterns = [
    path("", include(router.urls)),
]
