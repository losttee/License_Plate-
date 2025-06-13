"""
URL configuration for vehicle_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from plates import views  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path("admin/", admin.site.urls),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('checkin/', views.checkin_view, name='checkin'),
    path('history/', views.history_view, name='history'),  
    path('save_checkin_history/', views.save_checkin_history, name='save_checkin_history'),
    path('user_statistic/', views.user_statistic_view, name='user_statistic'),
    path('add_vehicle/', views.add_vehicle, name='add_vehicle'),
    path('delete_vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('update_vehicle/<int:vehicle_id>/', views.update_vehicle, name='update_vehicle'),
    path('recognize_plate/', views.recognize_plate_from_video, name='recognize_plate_from_video'),
    path('check_vehicle/', views.check_vehicle, name='check_vehicle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
