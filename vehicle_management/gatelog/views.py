import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import ExtractHour
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import ACTION_DONE, ACTION_INLOT, History
from .services import check_in, check_out, find_vehicle, open_inlot_history


def _vehicle_payload(vehicle, plate, entry_time=""):
    """Serialize vehicle fields for the check-in/out frontend."""
    if not vehicle:
        return None
    return {
        "user_name": vehicle.user_name,
        "unit": vehicle.unit,
        "model": vehicle.model,
        "license_plate": vehicle.license_plate,
        "issued_date": vehicle.issued_date.strftime("%Y-%m-%d"),
        "expired_date": vehicle.expired_date.strftime("%Y-%m-%d"),
        "phone_number": vehicle.phone_number,
        "entry_time": entry_time or timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        "avatar_url": vehicle.avatar.url if vehicle.avatar else "",
    }


@login_required
def checkin_view(request):
    return render(request, "gatelog/checkin.html")


@login_required
def save_checkin_history(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)
    plate = request.POST["license_plate"]
    action = request.POST["action"]
    if action == "in":
        check_in(plate, request.POST["status"])
    else:
        check_out(plate)
    return JsonResponse({"success": True, "message": "History updated"})


@login_required
def check_vehicle(request):
    plate = request.GET.get("plate", "").strip()
    process_type = request.GET.get("type", "in")
    if not plate:
        return JsonResponse({"error": "Missing plate number"}, status=400)

    vehicle = find_vehicle(plate)

    if process_type == "out":
        history = open_inlot_history(plate)
        payload = None
        if vehicle or history:
            entry_time = (
                history.entry_time.strftime("%Y-%m-%d %H:%M:%S") if history else ""
            )
            payload = {
                "user_name": vehicle.user_name if vehicle else "",
                "unit": vehicle.unit if vehicle else "",
                "model": vehicle.model if vehicle else "",
                "license_plate": plate,
                "issued_date": vehicle.issued_date.strftime("%Y-%m-%d") if vehicle else "",
                "expired_date": vehicle.expired_date.strftime("%Y-%m-%d") if vehicle else "",
                "entry_time": entry_time,
                "avatar_url": vehicle.avatar.url if vehicle and vehicle.avatar else "",
            }
        return JsonResponse(
            {"status": "inlot" if history else "not_in_lot", "vehicle": payload}
        )

    return JsonResponse(
        {"registered": bool(vehicle), "vehicle": _vehicle_payload(vehicle, plate)}
    )


@login_required
def history_view(request):
    keyword = request.GET.get("search", "").strip()
    histories = History.objects.select_related("vehicle")
    if keyword:
        histories = histories.filter(
            Q(vehicle__user_name__icontains=keyword)
            | Q(vehicle__unit__icontains=keyword)
            | Q(vehicle__model__icontains=keyword)
            | Q(license_plate__icontains=keyword)
        )

    paginator = Paginator(histories, 10)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request, "gatelog/history.html", {"histories": page, "search": keyword}
    )


@login_required
def dashboard_view(request):
    today = timezone.localdate()
    try:
        filter_date = datetime.datetime.strptime(
            request.GET.get("date", ""), "%Y-%m-%d"
        ).date()
    except ValueError:
        filter_date = today

    on_date = History.objects.filter(entry_time__date=filter_date)

    from vehicles.models import Vehicle

    stats = {
        "total_vehicles": on_date.count(),
        "current_vehicles": History.objects.filter(action_type=ACTION_INLOT).count(),
        "active_users": Vehicle.objects.filter(expired_date__gte=today).count(),
        "avg_duration": _average_duration(filter_date),
    }

    hourly_counts = dict(
        on_date.annotate(hour=ExtractHour("entry_time"))
        .values_list("hour")
        .annotate(count=Count("id"))
    )
    hourly_data = [
        {"hour": f"{hour:02d}:00", "count": hourly_counts.get(hour, 0)}
        for hour in range(24)
    ]

    return render(
        request,
        "gatelog/dashboard.html",
        {
            "stats": stats,
            "hourly_data": hourly_data,
            "selected_date": filter_date.strftime("%Y-%m-%d"),
            "today_date": today.strftime("%Y-%m-%d"),
        },
    )


def _average_duration(filter_date):
    completed = History.objects.filter(
        entry_time__date=filter_date,
        action_type=ACTION_DONE,
        exit_time__isnull=False,
    )
    total = datetime.timedelta(0)
    count = 0
    for parking in completed:
        total += parking.exit_time - parking.entry_time
        count += 1
    if not count:
        return "00:00:00"
    avg = total / count
    hours = int(avg.total_seconds() // 3600)
    minutes = int((avg.total_seconds() % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}:00"
