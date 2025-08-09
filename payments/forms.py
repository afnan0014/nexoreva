from django import forms

class PaymentSearchForm(forms.Form):
    staff_code = forms.CharField(
        max_length=20,
        required=False,
        label="Staff Code",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    course_code = forms.CharField(
        max_length=20,
        required=False,
        label="Course Code",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
