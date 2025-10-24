from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import datetime
from zoneinfo import ZoneInfo
from django.utils import timezone

from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)  # use module name for clarity


""""
NOTE: we are using a through model. this means
that we use an intermediate object userReportAccess() to manipulate a 'through' table to manage report access 
"""

# ------------------------------ DEFAULTS ------------------------------
# DEFINE DEFAULT DJANGO USER
User = get_user_model()
REPORT_TIME_ZONE = ZoneInfo("America/New_York")        # dst safe
# ----------------------------------------------------------------------

# Create your models here


class TimeSlot(models.Model):
    """Selectable dropdown for time of day."""

    # half-hour intervals from midnight to 23:30
    TIME_CHOICES = [
        (f"{h:02d}:{m:02d}:00", f"{h:02d}:{m:02d}")
        for h in range(0, 24)
        for m in (0, 30)
    ]

    time = models.TimeField(choices=TIME_CHOICES, unique=True)

    class Meta:
        ordering = ["time"]

    def __str__(self):
        return self.time.strftime("%H:%M")


class Report(models.Model):
    """Represents a specific report."""

    REPORT_CADENCE_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
    ]

    DAYS_OF_WEEK_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    # all reports will be set to US/Eastern Time zone -> corporate time zeon 

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    cadence = models.CharField(max_length=20, choices=REPORT_CADENCE_CHOICES)

    
    day_of_week_deadline = models.IntegerField(
        choices=DAYS_OF_WEEK_CHOICES, blank=True, null=True
    )

    time_deadline = models.ForeignKey(
        TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Time of day (WITH RESPECT TO YOUR TIME ZONE) the report should be updated by.",
    )

    users = models.ManyToManyField(
        User,
        through="UserReportAccess",
        related_name="accessible_reports",
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# ---------- Canonical computation for default corporate time zone ----------
    def next_deadline_est(self, from_dt=None):
        """
        Next deadline as an aware datetime in America/New_York.
            Respects time_deadline (TimeSlot) + day_of_week_deadline (0=Mon..6=Sun).
            - Daily: today at time, or tomorrow if past.
            - Weekly: next occurrence of configured weekday at time.
        """
        if not self.time_deadline:
            return None

        now_est = (from_dt or timezone.now()).astimezone(REPORT_TIME_ZONE)
        hour   = self.time_deadline.time.hour
        minute = self.time_deadline.time.minute

        base_today = now_est.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if self.cadence == "Weekly" and self.day_of_week_deadline is not None:
            delta = (int(self.day_of_week_deadline) - now_est.weekday()) % 7
            candidate = base_today + timedelta(days=delta)
            if delta == 0 and now_est > candidate:
                candidate += timedelta(days=7)
            return candidate

        # Daily (or fallback)
        return base_today if now_est <= base_today else base_today + timedelta(days=1)

    # ---------- Presentation for a user ----------
    def deadline_for_user(self, user, from_dt=None):
        """Return the canonical deadline converted to the user's timezone."""
        est_dt = self.next_deadline_est(from_dt)
        if not est_dt:
            return None
        user_tz = ZoneInfo(getattr(getattr(user, "profile", None), "timezone", "UTC"))
        return est_dt.astimezone(user_tz)

    def remaining_for_user(self, user, from_dt=None):
        """Timedelta until the user's localized deadline (negative if past)."""
        local_deadline = self.deadline_for_user(user, from_dt)
        if not local_deadline:
            return None
        now_local = (from_dt or timezone.now()).astimezone(local_deadline.tzinfo)
        return local_deadline - now_local

    def __str__(self):
        return f"{self.name} (refreshes) @ {self.description}"



class UserProfile(models.Model):
    LOCATION_CHOICES = [
            ("CORPORATE" , "CORPORATE"),
            ("ACBO" , "ACBO"),
            ("WCBO" , "WCBO"),
        ]

    LOCATION_TIMEZONES = {
        "CORPORATE" : "America/New_York",
        "ACBO" : "America/New_York",
        "WCBO" : "America/Los_Angeles",
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(choices=LOCATION_CHOICES, default="CORPORATE", help_text="Please select your work location")
    timezone = models.CharField(max_length=64, default="America/New_York", editable=False)

    def save(self, *args, **kwargs):
        """autoset time zone based on user's location"""
        self.timezone = self.LOCATION_TIMEZONES.get(self.location, "America/New_York") # default is nyc
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.user.username} @ {self.location}"


class UserReportAccess(models.Model):
    ROLE_CHOICES = [("view","View"), ("edit","Edit"), ("owner","Owner")]
    user   = models.ForeignKey(User,   on_delete=models.CASCADE, related_name="report_links")       # user -> reports
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="user_links")        # report -> users
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="edit")
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "report"], name="uniqe_user_report_access"
            )
        ]

        indexes = [
            models.Index(fields=["user", "report"]),
            models.Index(fields=["report", "user"]),
        ]
     
    def __str__(self):
        return f"{self.user} → {self.report} [{self.role}]"
