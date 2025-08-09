from django import forms
from .models import Course, CourseCategory, SubCourse

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'sub_column', 'unicode', 'description', 'start_date', 'end_date', 'fees']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control', 'id': 'id_name'}),
            'sub_column': forms.Select(attrs={'class': 'form-control', 'id': 'id_sub_column'}),
            'unicode': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_unicode', 'readonly': 'readonly', 'placeholder': 'Auto-generated'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'id_end_date', 'type': 'date'}),
            'fees': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate course categories from database
        self.fields['name'].queryset = CourseCategory.objects.all().order_by('name')
        self.fields['name'].empty_label = "Select a course"
        
        # For sub-courses, start with empty queryset - will be populated via AJAX
        self.fields['sub_column'].queryset = SubCourse.objects.none()
        self.fields['sub_column'].empty_label = "Select a sub course"
        
        # Make sub_column required
        self.fields['sub_column'].required = True
        
        # If we have initial data for name, populate sub_courses
        if self.initial and 'name' in self.initial:
            try:
                course_category = CourseCategory.objects.get(id=self.initial['name'])
                self.fields['sub_column'].queryset = SubCourse.objects.filter(course_category=course_category).order_by('name')
            except CourseCategory.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        sub_column = cleaned_data.get('sub_column')
        
        # Ensure sub_column is selected
        if not sub_column:
            raise forms.ValidationError("Please select a sub-course. All courses must have a sub-course.")
        
        # Ensure sub_column belongs to the selected course category
        if name and sub_column and sub_column.course_category != name:
            raise forms.ValidationError("The selected sub-course does not belong to the selected course category.")
        
        return cleaned_data
