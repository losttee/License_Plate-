# Generated by Django 4.2 on 2025-06-11 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("plates", "0005_delete_history"),
    ]

    operations = [
        migrations.CreateModel(
            name="History",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("license_plate", models.CharField(max_length=50)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("registered", "Registered"),
                            ("unregistered", "Unregistered"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "action_type",
                    models.CharField(
                        choices=[("inlot", "In Lot"), ("done", "Done")], max_length=20
                    ),
                ),
                ("entry_time", models.DateTimeField(null=True)),
                ("exit_time", models.DateTimeField(null=True)),
                (
                    "vehicle",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="plates.vehicle",
                    ),
                ),
            ],
        ),
    ]
