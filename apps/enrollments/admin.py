from django.contrib import admin, messages
from django.utils import timezone

from .models import Enrollment, Payment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "status",
        "purchased_at",
        "approved_by",
        "approved_at",
    )
    list_filter = ("status", "course")
    search_fields = (
        "student__email",
        "student__username",
        "course__title",
    )
    readonly_fields = (
        "id",
        "purchased_at",
        "created_at",
        "updated_at",
    )

    actions = ["approve_enrollments", "reject_enrollments"]

    @admin.action(description="Approve selected enrollments")
    def approve_enrollments(self, request, queryset):
        updated = 0

        for enrollment in queryset.exclude(status=Enrollment.Status.ACTIVE):
            enrollment.status = Enrollment.Status.ACTIVE
            enrollment.approved_by = request.user
            enrollment.approved_at = timezone.now()
            enrollment.rejection_reason = ""
            enrollment.save()

            updated += 1

        self.message_user(
            request,
            f"{updated} enrollment(s) approved.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Reject selected enrollments")
    def reject_enrollments(self, request, queryset):
        updated = 0

        for enrollment in queryset.exclude(status=Enrollment.Status.REJECTED):
            enrollment.status = Enrollment.Status.REJECTED
            enrollment.approved_by = request.user
            enrollment.approved_at = timezone.now()
            enrollment.save()

            updated += 1

        self.message_user(
            request,
            f"{updated} enrollment(s) rejected.",
            level=messages.WARNING,
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "enrollment",
        "amount",
        "provider",
        "status",
        "paid_at",
    )
    list_filter = ("status", "provider")
    search_fields = (
        "provider_payment_id",
        "enrollment__student__email",
        "enrollment__course__title",
    )
    readonly_fields = (
        "id",
        "created_at",
    )
