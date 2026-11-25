from django import forms

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "body"]
        labels = {"body": "Announcement"}
        widgets = {"body": forms.Textarea(attrs={"rows": 6})}
        help_texts = {"body": "Up to 3,000 characters. This post can be read by anyone."}
