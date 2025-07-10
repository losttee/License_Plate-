from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("checkin/", views.checkin_view, name="checkin"),
    path("history/", views.history_view, name="history"),
    path("save_checkin_history/", views.save_checkin_history, name="save_checkin_history"),
    path("check_vehicle/", views.check_vehicle, name="check_vehicle"),
]
