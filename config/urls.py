from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/", include("apps.courses.urls")),
    path("api/enrollments/", include("apps.enrollments.urls")),
    # path("api/inventory/", include("apps.inventory.urls")),
    # path("api/workshops/", include("apps.workshops.urls")),
]
