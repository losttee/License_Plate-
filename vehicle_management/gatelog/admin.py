from django.contrib import admin

from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("license_plate", "action_type", "status", "entry_time", "exit_time")
    list_filter = ("action_type", "status")
    search_fields = ("license_plate",)
    date_hierarchy = "entry_time"
