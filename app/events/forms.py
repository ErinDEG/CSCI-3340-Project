from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "location", "desc"]
        labels = {"name": "Event Name", "desc": "Description"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "desc": forms.TextInput(attrs={"class": "form-control", "required": True}),
        }
