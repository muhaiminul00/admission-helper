from django.conf import settings
from django.db import models

from subjects.models import Subject


class Routine(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    imported_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-imported_at"]

    def __str__(self):
        return self.name


class Lecture(models.Model):
    id = models.BigAutoField(primary_key=True)
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name="lectures"
    )
    lecture_code = models.CharField(max_length=30)
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="lectures"
    )
    title = models.CharField(max_length=200, blank=True, default="")
    lecture_date = models.DateField(null=True, blank=True, db_index=True)
    day = models.CharField(max_length=20, blank=True, default="")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["lecture_date", "start_time"]
        indexes = [
            models.Index(fields=["lecture_code"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["routine", "lecture_code"], name="unique_routine_lecture_code"
            ),
        ]

    def __str__(self):
        return self.lecture_code


class Exam(models.Model):
    class ExamType(models.TextChoices):
        WEEKLY = "Weekly", "Weekly"
        MONTHLY = "Monthly", "Monthly"
        SPECIAL = "Special", "Special"

    id = models.BigAutoField(primary_key=True)
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name="exams"
    )
    exam_code = models.CharField(max_length=30, unique=True)
    exam_name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=ExamType.choices)
    exam_date = models.DateField(db_index=True)
    online_start = models.DateField(null=True, blank=True)
    online_end = models.DateField(null=True, blank=True)
    covered_lectures = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["exam_date"]
        indexes = [
            models.Index(fields=["exam_type"]),
        ]

    def __str__(self):
        return self.exam_name


class DatasetVersion(models.Model):
    """One imported CSV dataset snapshot (Milestone 10).

    Created automatically by every successful `import_csv` run (not by
    `--preview` or `--dry-run`, which write nothing). `source` holds the
    directory the archived source CSVs for this version live in
    (`routines/services/dataset/versioning.py: archive_source_csvs()`)
    - this is what makes `rollback_dataset` possible: rolling back
    re-imports from a *previous* version's archived CSVs rather than
    attempting to reconstruct rows from `statistics` alone (which is
    only a summary, not a data snapshot).

    Only one `DatasetVersion` may be active at a time - enforced by the
    partial `UniqueConstraint` below, not just application logic (see
    `versioning.py: activate_version()`).
    """

    id = models.BigAutoField(primary_key=True)
    version_name = models.CharField(max_length=100, unique=True)
    source = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dataset_versions",
    )
    imported_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    checksum = models.CharField(max_length=64)
    statistics = models.JSONField(default=dict)

    class Meta:
        ordering = ["-imported_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"], condition=models.Q(is_active=True),
                name="unique_active_dataset_version",
            ),
        ]

    def __str__(self):
        return self.version_name


class ImportLog(models.Model):
    """An audit record of one `import_csv` run - preview, dry-run, real
    import, or rollback (Milestone 10). Written regardless of outcome,
    including failures, so "what happened last time I tried this" is
    always answerable without re-reading console output that may
    already be gone.
    """

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        DRY_RUN = "dry_run", "Dry Run"
        PREVIEW = "preview", "Preview"
        ROLLBACK = "rollback", "Rollback"

    id = models.BigAutoField(primary_key=True)
    dataset_version = models.ForeignKey(
        DatasetVersion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="import_logs",
    )
    importer_version = models.CharField(max_length=20)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="import_logs",
    )
    started_at = models.DateTimeField()
    duration_seconds = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, db_index=True)
    imported_counts = models.JSONField(default=dict)
    skipped_counts = models.JSONField(default=dict)
    errors = models.TextField(blank=True, default="")
    warnings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.get_status_display()} import at {self.started_at:%Y-%m-%d %H:%M}"
