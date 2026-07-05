import uuid

from django.conf import settings
from django.db import models

from apps.courses.models import Course


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
        PAYMENT_VERIFICATION = "payment_verification", "Payment Verification"
        PENDING_ENROLLMENT = "pending_enrollment", "Pending Enrollment"
        ACTIVE = "active", "Active"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="enrollments"
    )
    status = models.CharField(
        max_length=25, choices=Status.choices, default=Status.PENDING_PAYMENT
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollments"
        ordering = ["-purchased_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="one_enrollment_per_student_per_course",
            )
        ]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.student} -> {self.course} [{self.status}]"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    provider = models.CharField(max_length=50, blank=True)  # e.g. razorpay, stripe
    provider_payment_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_verified",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["enrollment"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Payment {self.id} — {self.status}"
