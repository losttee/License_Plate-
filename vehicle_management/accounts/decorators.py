from functools import wraps

from django.http import JsonResponse

from .models import ROLE_GUARD, UserProfile


def get_profile(user):
    """Return the user's profile, creating a default guard profile if missing.

    Superusers created via createsuperuser have no profile; without this they
    would raise UserProfile.DoesNotExist on every role check.
    """
    profile, _ = UserProfile.objects.get_or_create(
        user=user, defaults={"role": ROLE_GUARD}
    )
    return profile


def manager_required(view_func):
    """Allow only authenticated managers; return JSON errors for AJAX callers."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        if not get_profile(request.user).is_manager:
            return JsonResponse({"error": "Permission denied"}, status=403)
        return view_func(request, *args, **kwargs)

    return wrapper
