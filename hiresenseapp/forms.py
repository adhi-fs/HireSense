from django import forms
from .models import Jobs

class JobForm(forms.ModelForm):
    class Meta:
        model = Jobs
        fields = ['job_title', 'job_role', 'job_location', 'job_salary', 'job_status', 'job_description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
