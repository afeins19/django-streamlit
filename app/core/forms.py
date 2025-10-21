# core/forms.py
from django import forms
from .models import UserProfile
from zoneinfo import ZoneInfo


import logging

logger = logging.getLogger(__name__)  # use module name for clarity


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
                    "location",
                 ]

    def clean_timezone(self):
        tz = self.cleaned_data["timezone"]
        ZoneInfo(tz)  # raises if invalid
        return tz
