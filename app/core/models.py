from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.conf import settings

""""
NOTE: we are using a through model. this means
that we use an intermediate object userReportAccess() to manipulate a 'through' table to manage report access 
"""

# DEFINE DEFAULT DJANGO USER
User = get_user_model()

# Create your models here.
class Report(models.Model):
    """represents a specific report"""

    REPORT_CADENCE_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
    ]

    DAYS_OF_WEEK_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    TIME_OF_DAY_CHOICES = [(t,t) for t in range(12)]


    name = models.CharField(max_length=200, unique=True)                                    # report name
    slug = models.SlugField(unique=True)                                                    # unique id for report
    description = models.TextField(blank=True)                                              # description
    cadence = models.CharField(choices=REPORT_CADENCE_CHOICES)                              # refresh period e.g. daily, weekly etc. 
    day_of_week_deadline = models.IntegerField(                                             # deadline to update
        choices=DAYS_OF_WEEK_CHOICES, blank=True, null=True
    )

    time_deadline = models.TimeField(
        blank=True, 
        null=True,
        help_text="Time of day (WITH RESPECT TO YOUR TIME ZONE) the report should be updated by."
    )

    # any user that has some sort of access to the report (read or write)
    users = models.ManyToManyField(
        User,
        through='UserReportAccess',
        related_name='reports',
        blank=True,
    )

    class Meta:
        ordering = ["name"]


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (refreshes) - {self.description}"


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
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="user_links")         # report -> users
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="edit")
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "report"], name="uniq_user_report_access"
            )
        ]

        indexes = [
            models.Index(fields=["user", "report"]),
            models.Index(fields=["report", "user"]),
        ]
     
    def __str__(self):
        return f"{self.user} → {self.report} [{self.role}]"
