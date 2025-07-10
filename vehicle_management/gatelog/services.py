from django.utils import timezone

from vehicles.models import Vehicle

from .models import ACTION_DONE, ACTION_INLOT, History


def find_vehicle(plate):
    return Vehicle.objects.filter(license_plate__iexact=plate).first()


def open_inlot_history(plate):
    """Return the open (not yet exited) in-lot record for a plate, if any."""
    return History.objects.filter(
        license_plate__iexact=plate,
        action_type=ACTION_INLOT,
        exit_time__isnull=True,
    ).first()


def check_in(plate, status):
    """Record a vehicle entering the lot."""
    return History.objects.create(
        license_plate=plate,
        status=status,
        action_type=ACTION_INLOT,
        entry_time=timezone.now(),
        vehicle=find_vehicle(plate),
    )


def check_out(plate):
    """Close the open in-lot record for a plate. Returns it, or None if absent."""
    history = open_inlot_history(plate)
    if history:
        history.action_type = ACTION_DONE
        history.exit_time = timezone.now()
        history.save()
    return history
