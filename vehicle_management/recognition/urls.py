from django.urls import path

from . import views

urlpatterns = [
    path("recognize_plate/", views.recognize_plate_from_video, name="recognize_plate"),
]
