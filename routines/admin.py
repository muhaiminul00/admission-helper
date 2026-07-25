from django.contrib import admin

from routines.models import DatasetVersion, Exam, ImportLog, Lecture, Routine

admin.site.register(Routine)
admin.site.register(Lecture)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["exam_code", "exam_name", "exam_type", "exam_date", "online_start", "online_end"]
    list_filter = ["exam_type"]
    search_fields = ["exam_code", "exam_name"]


@admin.register(DatasetVersion)
class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ["version_name", "is_active", "imported_by", "imported_at", "checksum"]
    list_filter = ["is_active"]
    search_fields = ["version_name", "checksum"]
    readonly_fields = ["checksum", "statistics", "imported_at"]


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ["started_at", "status", "user", "duration_seconds", "dataset_version"]
    list_filter = ["status", "user"]
    search_fields = ["errors"]
    readonly_fields = [
        "dataset_version", "importer_version", "user", "started_at", "duration_seconds",
        "status", "imported_counts", "skipped_counts", "errors", "warnings",
    ]
