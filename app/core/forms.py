from django import forms
from django.contrib.auth import get_user_model


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
        }
