from django.contrib import admin
from .models import Course, Enrollment, CourseCategory, SubCourse

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(SubCourse)
class SubCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_category', 'created_at', 'updated_at']
    list_filter = ['course_category']
    search_fields = ['name', 'course_category__name']
    ordering = ['course_category__name', 'name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'sub_column', 'unicode', 'start_date', 'end_date', 'fees']
    list_filter = ['name', 'sub_column']
    search_fields = ['name__name', 'sub_column__name', 'unicode']
    ordering = ['name__name']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'staff', 'enrolled_on']
    list_filter = ['course', 'enrolled_on']
    search_fields = ['course__name__name', 'staff__full_name']
    ordering = ['-enrolled_on']
