from django.urls import path

from . import views

urlpatterns = [
    path("user_statistic/", views.user_statistic_view, name="user_statistic"),
    path("add_vehicle/", views.add_vehicle, name="add_vehicle"),
    path("delete_vehicle/<int:vehicle_id>/", views.delete_vehicle, name="delete_vehicle"),
    path("update_vehicle/<int:vehicle_id>/", views.update_vehicle, name="update_vehicle"),
]
