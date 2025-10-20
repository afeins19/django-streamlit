# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("my_reports/", views.my_reports, name="my_reports"),
]
