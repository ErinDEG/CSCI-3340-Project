from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    # Meta will transform the data into Metadata
    class Meta:
        model = Event
        fields = ["name", "desc", "location", "submitted_by"]
