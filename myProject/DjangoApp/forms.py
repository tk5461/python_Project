from django import forms
from django.core.exceptions import ValidationError
from .models import Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['team', 'role']
