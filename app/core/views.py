from django.shortcuts import render
from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, render, redirect

from .models import Report, UserReportAccess, UserProfile, User
from .forms import ProfileForm
from datetime import datetime
from zoneinfo import ZoneInfo
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)  # use module name for clarity



# Create your views here.

def home(request):
    # AUTH CHECK FIRST!
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    profile=None

    # try and fetch custom profile for default django user object
    if user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=user)
            user_tz = profile.timezone or None
            logger.error(">>>>>Found profile for %s with timezone %s", request.user.username, profile.timezone)
        except UserProfile.DoesNotExist:
            logger.error(">>>>>No profile found for user %s", request.user.username)
            pass        # profile remains null... logic for hiding null profile in html

        # >>>>>>> fetch reports and deadlines:
        # user_links -> UserReportAcess Objects -> user
        reports = reports = Report.objects.filter(user_links__user=user).order_by("day_of_week_deadline", "time_deadline")

        report_data = []
        user_data = []
        now = timezone.now()


        # only calculate time until deadline if user has a defined timezone
        if user_tz and user_tz.strip().lower() != "none":
            now = now.astimezone(ZoneInfo(user_tz))

            # calcualte deadlines with a delta from users timezone
            for r in reports:
                # get report submission deadline in terms of users local tz
                local_deadline = r.deadline_date_time(user_tz)
                is_overdue = False

                 # skip reports with missing deadline 
                if not (local_deadline):
                    is_overdue = False
                    status_text = "No Deadline Defined"
                    continue 

                delta = local_deadline - now 
                delta_seconds = int(delta.total_seconds())

                if delta_seconds <= 0:
                    is_overdue = True
                    status_text=f"Overdue! (due at {str(local_deadline)})"

                else: 
                    # 86400 seconds in day, 3600/hr
                    days = delta_seconds // 86400
                    delta_seconds %= 86400
                    hours = delta_seconds // 3600
                    delta_seconds %= 3600 
                    minutes = delta_seconds // 60

                    status_text = f"{days}d, {hours}h, {minutes}m" 


                report_data.append({
                    "report_name" : r.name,
                    "status_text" : status_text,
                    "is_overdue" : is_overdue
                })

                user_data = {
                    "user_first_name" : user.first_name,
                    "user_location" : profile.location,
                    "user_timezone" : profile.timezone
                }
            
        return render(request, "core/home.html", {"report_data" : report_data, "user_data" : user_data})


# ----------------------
# ADMIN REPORT VIEW
# ----------------------

@staff_member_required
def admin_report_list(request):
    """listing reports along with all users that have acess"""
    qs = (
        Report.objects
        .annotate(user_count=Count("user_links"))   # user_links means related_names on UserReportAccess.report
        .orderby("name")
    )

    # pagination for viewing list of users
    paginator = Paginator(qs, 25)
    page = request.GET.get("page") or 1
    page_obj = paginator.get_page(page)
    return render(request, "reports/admin_report_list.html", {"page_obj" : page_obj})

@staff_member_required
def admin_report_detail(request, slug):
    """user permissions detail about a specific report"""

    report = get_object_or_404(Report, slug=slug)

    access_qs = (
        UserReportAccess.objects
        .select_related("user")
        .filter(report=report)
        .order_by("user__username")
    )

    paginator = Paginator(acess_qs, 50)
    page = request.Get.get("page") or 1
    page_obj = paginator.get_page(page)

    return render(
        request,
        "reports/admin_report_detail.html",
        {"report" : report, "page_obj" : page_obj}
    )


# ----------------------
# USER REPORT VIEW
# ----------------------

@login_required
def my_reports(request):
    """
        only returns the reports the current user can access. The `my_access` objecft
        will return a list of through-rows from which the report names can be extracted
    """

    my_access = (
        UserReportAccess.objects
        .select_related("report")
        .filter(user=request.user)
        .order_by("report__name")
    )

    pageinator = Paginator(my_access, 25)
    page = request.GET.get("page") or 1
    page_obj = pageinator.get_page(page)

    return render(request, "core/my_reports.html", {"page_obj" : page_obj})

@login_required
def edit_my_settings(request):
    """user settings where they can edit their profile"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":        # submitting form 
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings Saved!')
            return redirect("my_settings")
    else:                               # requesting form
        form = ProfileForm(instance=profile)
    return render(request, "core/edit_my_settings.html", {"form": form})

@login_required
def my_settings(request):
    """user settings where they can edit their profile"""
    profile = UserProfile.objects.get(user=request.user)
    return render(request, "core/my_settings.html", {"profile" : profile})