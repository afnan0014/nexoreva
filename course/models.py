from django.db import models
from django.contrib.auth.models import User
from staff.models import Staff
import random

class CourseCategory(models.Model):
    """Model to store course categories/names dynamically"""
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Course Categories"

class SubCourse(models.Model):
    """Model to store sub-courses for each course category"""
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='sub_courses')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_category.name} - {self.name}"

    class Meta:
        unique_together = ('course_category', 'name')
        verbose_name_plural = "Sub Courses"

class Course(models.Model):
    name = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    sub_column = models.ForeignKey(SubCourse, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    unicode = models.CharField(max_length=10, unique=True, blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.unicode:
            self.unicode = self.generate_unicode()
        super().save(*args, **kwargs)

    def generate_unicode(self):
        # Generate prefix based on course name (first 3 letters, uppercase)
        if self.name and self.name.name:
            prefix = self.name.name[:3].upper()
        else:
            prefix = 'GEN'
        
        # Generate 5 random digits
        digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        
        return f"{prefix}{digits}"

    def __str__(self):
        course_name = self.name.name if self.name else 'No Course'
        sub_course_name = self.sub_column.name if self.sub_column else 'No Sub Course'
        return f"{course_name} - {sub_course_name}"


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)  # Changed back to Staff
    enrolled_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'staff')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.staff.full_name} enrolled in {self.course.name}"
