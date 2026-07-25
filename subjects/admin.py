from django.contrib import admin

from subjects.models import Chapter, Subject

admin.site.register(Subject)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["subject", "paper", "chapter_no", "name"]
    list_filter = ["subject", "paper"]
    search_fields = ["name"]
