from django.db import models

from routines.models import Lecture
from subjects.models import Chapter


class LectureTopic(models.Model):
    id = models.BigAutoField(primary_key=True)
    lecture = models.ForeignKey(
        Lecture, on_delete=models.CASCADE, related_name="topics"
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.PROTECT, related_name="lecture_topics",
        null=True, blank=True,
    )
    topic = models.CharField(max_length=255)
    display_order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["lecture", "display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["lecture", "chapter", "topic"],
                name="unique_lecture_chapter_topic",
            ),
        ]

    def __str__(self):
        return self.topic
