import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Course(models.Model):
    class Level(models.TextChoices):
        SCHOOL = "school", "School"
        COLLEGE = "college", "College"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=10, choices=Level.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    thumbnail_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="courses_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["is_published"]),
        ]

    def __str__(self):
        return self.title


class CourseMaterial(models.Model):
    class Type(models.TextChoices):
        VIDEO = "video", "Video"
        PDF = "pdf", "PDF"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="materials"
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    title = models.CharField(max_length=255)
    url = models.URLField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="materials_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_materials"
        ordering = ["course"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="announcements",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "announcements"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["course"])]

    def __str__(self):
        return self.title


class CourseFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="feedback"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_feedback",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_feedback"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student"], name="one_review_per_student_per_course"
            )
        ]
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.student} rated {self.course} — {self.rating}/5"
