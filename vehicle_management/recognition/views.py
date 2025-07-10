import os
import tempfile

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from gatelog.services import find_vehicle, open_inlot_history

from .services import PlateRecognizer


def _build_entry(plate, img_b64, frame_time, process_type):
    """Build the per-vehicle payload the check-in frontend consumes."""
    vehicle = find_vehicle(plate)

    if process_type == "out":
        history = open_inlot_history(plate)
        return {
            "plate": plate,
            "status": "inlot" if history else "not_in_lot",
            "user_info": {
                "license_plate": plate,
                "model": vehicle.model if vehicle else "",
                "user_name": vehicle.user_name if vehicle else "",
                "unit": vehicle.unit if vehicle else "",
                "issued_date": vehicle.issued_date.strftime("%Y-%m-%d") if vehicle else "",
                "expired_date": vehicle.expired_date.strftime("%Y-%m-%d") if vehicle else "",
                "entry_time": history.entry_time.strftime("%Y-%m-%d %H:%M:%S") if history else "",
                "avatar_url": vehicle.avatar.url if vehicle and vehicle.avatar else "",
            },
            "img_b64": img_b64,
            "frame_time": frame_time,
        }

    if vehicle:
        from django.utils import timezone

        return {
            "plate": plate,
            "status": "registered",
            "user_info": {
                "user_name": vehicle.user_name,
                "unit": vehicle.unit,
                "model": vehicle.model,
                "license_plate": vehicle.license_plate,
                "issued_date": vehicle.issued_date.strftime("%Y-%m-%d"),
                "expired_date": vehicle.expired_date.strftime("%Y-%m-%d"),
                "phone_number": vehicle.phone_number,
                "entry_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "avatar_url": vehicle.avatar.url if vehicle.avatar else "",
            },
            "img_b64": img_b64,
            "frame_time": frame_time,
        }

    return {
        "plate": plate,
        "status": "unregistered",
        "user_info": {"license_plate": plate, "model": ""},
        "img_b64": img_b64,
        "frame_time": frame_time,
    }


@login_required
def recognize_plate_from_video(request):
    if request.method != "POST" or not request.FILES.get("video"):
        return JsonResponse({"error": "Invalid request"}, status=400)

    process_type = request.GET.get("type", "in")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        for chunk in request.FILES["video"].chunks():
            temp.write(chunk)
        temp_path = temp.name

    try:
        detections = PlateRecognizer.instance().scan_video(temp_path)
    finally:
        os.remove(temp_path)

    vehicles = [
        _build_entry(plate, img_b64, frame_time, process_type)
        for plate, img_b64, frame_time in detections
    ]

    if not vehicles:
        return JsonResponse(
            {"success": False, "message": "Không phát hiện được biển số nào trong video"}
        )
    return JsonResponse(
        {"success": True, "total_vehicles": len(vehicles), "vehicles": vehicles}
    )
