from django import forms
from django.utils import timezone

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "category", "starts_at", "ends_at", "location", "desc"]
        labels = {
            "name": "Event name",
            "starts_at": "Starts",
            "ends_at": "Ends (optional)",
            "desc": "Description (optional)",
        }
        help_texts = {
            "location": "Include a building and street address or city for a more accurate map.",
        }
        widgets = {
            "starts_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
            ),
            "ends_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
            ),
            "desc": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = True
        self.fields["category"].choices = [("", "Choose a category"), *Event.Category.choices]
        self.fields["starts_at"].required = True
        self.fields["starts_at"].help_text = (
            f"Campus time ({timezone.get_current_timezone_name().replace('_', ' ')})."
        )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("starts_at")
        end = cleaned_data.get("ends_at")
        if start and end and end <= start:
            self.add_error("ends_at", "The end time must be after the start time.")
        for field, value in (("starts_at", start), ("ends_at", end)):
            if value and not 2 <= value.year <= 9998:
                self.add_error(field, "Choose a year between 2 and 9998.")
        return cleaned_data
