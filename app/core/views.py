from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, render
from .models import Report, UserReportAccess


# Create your views here.

def home(request):
    return render(request, "core/home.html")


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