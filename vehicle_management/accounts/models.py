from django.contrib.auth.models import User
from django.db import models

ROLE_GUARD = "guard"
ROLE_MANAGER = "manager"
ROLE_CHOICES = [
    (ROLE_GUARD, "Guard"),
    (ROLE_MANAGER, "Manager"),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_GUARD)

    @property
    def is_manager(self):
        return self.role == ROLE_MANAGER

    def __str__(self):
        return f"{self.user.username} - {self.role}"
