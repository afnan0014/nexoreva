from django import forms
from .models import Staff
from django.conf import settings

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'reporting_manager': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'onbording_status': forms.Select(attrs={'class': 'form-select'}),
            'join_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'staff_code': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['join_date'].input_formats = ['%Y-%m-%d']
        self.fields['date_of_birth'].input_formats = ['%Y-%m-%d']
        
        # 👇 Pop 'designation' field so it's excluded from the form but kept in the model
        self.fields.pop('designation', None)
