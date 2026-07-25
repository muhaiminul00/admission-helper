from django.db import models


class Subject(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    display_order = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Chapter(models.Model):
    class Paper(models.IntegerChoices):
        FIRST = 1, "1st Paper"
        SECOND = 2, "2nd Paper"

    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="chapters"
    )
    paper = models.PositiveSmallIntegerField(choices=Paper.choices)
    chapter_no = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=200)
    display_order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["subject", "paper", "chapter_no"]
        indexes = [
            models.Index(fields=["chapter_no"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "paper", "chapter_no"],
                name="unique_subject_paper_chapter_no",
            ),
        ]

    def __str__(self):
        return (
            f"{self.subject.name} - {self.get_paper_display()} - "
            f"Chapter {self.chapter_no} - {self.name}"
        )
