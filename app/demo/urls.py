"""
URL configuration for demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

# custom view importing
from core import views

# DEBUGING HEADERS
def debug_headers(request):
    return JsonResponse({
        "is_secure": request.is_secure(),
        "scheme": request.scheme,
        "host": request.get_host(),
        "x_forwarded_proto": request.META.get("HTTP_X_FORWARDED_PROTO"),
        "origin": request.META.get("HTTP_ORIGIN"),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),   	# initial landing point/home page
    path("_debug_headers", debug_headers),	# test debuging -> is_secure should be true
]
