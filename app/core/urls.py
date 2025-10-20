# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("reports/", views.my_reports, name="my_reports"),

    # path for individual reports
    #path("reports/<slug:slug>/editor/", views.open_report_editor),
    path("settings/", views.my_settings, name="my_settings"),
]
