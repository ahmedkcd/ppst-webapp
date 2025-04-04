from django import forms
from datetime import timedelta
from .models import TestSession

class TestSessionForm(forms.ModelForm):
    duration = forms.CharField(required=False, help_text="e.g. '5 minutes', '1 hour', '2h 30m'")

    class Meta:
        model = TestSession
        fields = '__all__'

    def clean_duration(self):
        value = self.cleaned_data['duration']
        if not value:
            return None

        # Basic parsing
        import re
        minutes = 0
        hours = 0
        parts = re.findall(r'(\d+)\s*(h|hr|hour|m|min|minute)', value.lower())
        for amount, unit in parts:
            if unit.startswith('h'):
                hours += int(amount)
            elif unit.startswith('m'):
                minutes += int(amount)

        return timedelta(hours=hours, minutes=minutes)