from django.contrib import admin
from .models import Report, UserReportAccess

# Register your models here.
admin.site.register(Report)
admin.site.register(UserReportAccess)