from datetime import date

from django.db import models


class Vehicle(models.Model):
    user_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    issued_date = models.DateField()
    expired_date = models.DateField()
    avatar = models.ImageField(upload_to="vehicle_avatars/", null=True, blank=True)

    @property
    def status(self):
        return "Active" if self.expired_date >= date.today() else "Inactive"

    def __str__(self):
        return f"{self.user_name} - {self.license_plate}"
