from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from accounts.decorators import get_profile, manager_required

from .forms import VehicleForm
from .models import Vehicle


@login_required
def user_statistic_view(request):
    keyword = request.GET.get("search", "").strip()
    vehicles = Vehicle.objects.all()
    if keyword:
        vehicles = vehicles.filter(
            Q(user_name__icontains=keyword)
            | Q(unit__icontains=keyword)
            | Q(model__icontains=keyword)
            | Q(license_plate__icontains=keyword)
            | Q(phone_number__icontains=keyword)
        )
    return render(
        request,
        "vehicles/user_statistic.html",
        {
            "vehicles": vehicles,
            "search": keyword,
            "is_manager": get_profile(request.user).is_manager,
        },
    )


@manager_required
def add_vehicle(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)
    form = VehicleForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return JsonResponse({"message": "Vehicle added successfully"})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@manager_required
def update_vehicle(request, vehicle_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    form = VehicleForm(request.POST, request.FILES, instance=vehicle)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@manager_required
def delete_vehicle(request, vehicle_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    return JsonResponse({"success": True})
