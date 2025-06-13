from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('guard', 'Guard'),
        ('manager', 'Manager')
    ], default='guard')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Vehicle(models.Model):
    user_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    issued_date = models.DateField()
    expired_date = models.DateField()
    avatar = models.ImageField(upload_to='vehicle_avatars/', null=True, blank=True)  # Thêm dòng này

    @property
    def status(self):
        return 'Active' if self.expired_date >= date.today() else 'Inactive'

    def __str__(self):
        return f"{self.user_name} - {self.license_plate}"
    
class History(models.Model):
    license_plate = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ('registered', 'Registered'),
        ('unregistered', 'Unregistered')
    ])
    action_type = models.CharField(max_length=20, choices=[
        ('inlot', 'In Lot'),
        ('done', 'Done')
    ])
    entry_time = models.DateTimeField(null=True)
    exit_time = models.DateTimeField(null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.license_plate} - {self.action_type}"