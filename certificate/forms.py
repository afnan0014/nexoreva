from django import forms
from staff.models import Staff
from course.models import Course


class CertificateGenerationForm(forms.Form):
    staff_code = forms.CharField(
        label="Staff Unicode Code",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter staff code (e.g., nxremp1234)',
            'required': True
        })
    )
    
    course_unicode = forms.CharField(
        label="Course Unicode Code", 
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter course code (e.g., IT12345)',
            'required': True
        })
    )
    
    def clean_staff_code(self):
        staff_code = self.cleaned_data['staff_code']
        try:
            staff = Staff.objects.get(staff_code=staff_code)
            return staff_code
        except Staff.DoesNotExist:
            raise forms.ValidationError(f"Staff with code '{staff_code}' not found.")
    
    def clean_course_unicode(self):
        course_unicode = self.cleaned_data['course_unicode']
        try:
            course = Course.objects.get(unicode=course_unicode)
            return course_unicode
        except Course.DoesNotExist:
            raise forms.ValidationError(f"Course with code '{course_unicode}' not found.")
