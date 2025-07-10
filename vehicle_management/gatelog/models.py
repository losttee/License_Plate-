from django.db import models

STATUS_CHOICES = [
    ("registered", "Registered"),
    ("unregistered", "Unregistered"),
]
ACTION_INLOT = "inlot"
ACTION_DONE = "done"
ACTION_CHOICES = [
    (ACTION_INLOT, "In Lot"),
    (ACTION_DONE, "Done"),
]


class History(models.Model):
    license_plate = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entry_time = models.DateTimeField(null=True)
    exit_time = models.DateTimeField(null=True)
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["-entry_time"]
        verbose_name_plural = "Histories"

    def __str__(self):
        return f"{self.license_plate} - {self.action_type}"
