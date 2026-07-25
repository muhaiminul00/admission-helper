from django.conf import settings
from django.db import models

from lectures.models import LectureTopic
from routines.models import Lecture


class Progress(models.Model):
    """One user's study-stage completion for one LectureTopic.

    Milestone 7: Progress became per-user (previously one row per
    LectureTopic for the whole, single-user application). `lecture_topic`
    changed from OneToOneField to ForeignKey since many users can now
    each have their own Progress row for the same topic; the
    (user, lecture_topic) UniqueConstraint below is what actually
    enforces "at most one Progress row per user per topic" now that the
    field-level OneToOne uniqueness is gone.
    """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_records"
    )
    lecture_topic = models.ForeignKey(
        LectureTopic, on_delete=models.CASCADE, related_name="progress_records"
    )
    class_done = models.BooleanField(default=False)
    notes_done = models.BooleanField(default=False)
    revision_done = models.BooleanField(default=False)
    practice_done = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ["updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lecture_topic"], name="unique_user_lecture_topic"
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.lecture_topic.topic}"


class RevisionSchedule(models.Model):
    """One user's revision stage for one fully-completed Lecture.

    Milestone 9: revision is scheduled per-lecture, not per-topic - a
    lecture's topics collectively represent "what to revise," so this
    intentionally does not duplicate any `LectureTopic`/`Progress` data,
    only references the `Lecture` (topics are reached via
    `lecture.topics` when a revision's detail page needs them).

    Three rows (one per `Level`) are created together, all at once,
    the moment a lecture becomes fully completed - see
    `progress/services/revision.py: ensure_revision_schedule()`. The
    (user, lecture, revision_level) constraint is what prevents a
    second set of schedules being created for the same lecture.
    """

    class Level(models.IntegerChoices):
        FIRST = 1, "First Revision"
        SECOND = 2, "Second Revision"
        FINAL = 3, "Final Revision"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="revision_schedules"
    )
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="revision_schedules"
    )
    revision_level = models.PositiveSmallIntegerField(choices=Level.choices)
    due_date = models.DateField(db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "revision_level"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lecture", "revision_level"],
                name="unique_user_lecture_revision_level",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.lecture.lecture_code} - {self.get_revision_level_display()}"


class RevisionHistory(models.Model):
    """An immutable record of one completed revision.

    Never deleted or overwritten when a revision is completed again in
    the future (it can't be - each `RevisionSchedule` only completes
    once, per this milestone's "mark as complete" one-way workflow) -
    this exists as the durable audit trail `RevisionSchedule.completed_at`
    alone doesn't provide (that field gets overwritten if a schedule
    were ever reopened; this table never would be).
    """

    id = models.BigAutoField(primary_key=True)
    revision_schedule = models.ForeignKey(
        RevisionSchedule, on_delete=models.CASCADE, related_name="history"
    )
    completed_at = models.DateTimeField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.revision_schedule} completed {self.completed_at}"
