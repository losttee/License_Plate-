from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("user_name", "license_plate", "unit", "model", "expired_date")
    search_fields = ("user_name", "license_plate", "unit", "model")
    list_filter = ("unit",)
