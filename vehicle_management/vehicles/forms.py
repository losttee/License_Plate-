from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "user_name",
            "unit",
            "model",
            "license_plate",
            "phone_number",
            "issued_date",
            "expired_date",
            "avatar",
        ]
