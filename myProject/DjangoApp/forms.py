from django import forms
from django.core.exceptions import ValidationError
from .models import Person , Task


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['team', 'role']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'date_end', 'Executor', 'status', 'team']
        widgets = {
            'date_end': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            )}


    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if team:
            self.fields['team'].initial = team
            # self.fields['team'].widget.attrs['disabled'] = 'disabled'


