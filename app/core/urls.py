# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("reports/", views.my_reports, name="my_reports"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    # path for individual reports
    #path("reports/<slug:slug>/editor/", views.open_report_editor),
    path("settings/", views.my_settings, name="my_settings"),
    path("settings/edit/", views.edit_my_settings, name="edit_my_settings"),
]
