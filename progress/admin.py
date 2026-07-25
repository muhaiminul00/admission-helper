from django.contrib import admin

from progress.models import Progress, RevisionHistory, RevisionSchedule


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "lecture_topic", "completion_status", "updated_at"]
    list_filter = ["user", "lecture_topic__lecture__subject"]
    search_fields = ["user__username", "lecture_topic__topic"]

    @admin.display(description="Completion status", boolean=True)
    def completion_status(self, obj):
        return obj.class_done and obj.notes_done and obj.revision_done and obj.practice_done


class RevisionHistoryInline(admin.TabularInline):
    model = RevisionHistory
    extra = 0
    readonly_fields = ["completed_at", "notes"]
    can_delete = False


@admin.register(RevisionSchedule)
class RevisionScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "user", "lecture", "revision_level", "due_date", "status", "completed_at",
    ]
    list_filter = ["status", "revision_level", "lecture__subject", "user"]
    search_fields = ["user__username", "lecture__lecture_code"]
    inlines = [RevisionHistoryInline]


@admin.register(RevisionHistory)
class RevisionHistoryAdmin(admin.ModelAdmin):
    list_display = ["revision_schedule", "completed_at"]
    list_filter = ["revision_schedule__user"]
    search_fields = ["revision_schedule__lecture__lecture_code"]
