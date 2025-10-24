# core/middleware.py
from django.utils import timezone
from zoneinfo import ZoneInfo

DEFAULT_TZ = "America/New_York"

class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_name = None

        # if user has a profile, set time zone from profile
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            tz_name = request.user.profile.timezone or DEFAULT_TZ
        timezone.activate(ZoneInfo(tz_name or DEFAULT_TZ))
        response = self.get_response(request)
        timezone.deactivate()
        return response
