from django.db import models
from django.contrib.auth.models import User
from staff.models import Staff
import random

class Course(models.Model):
    COURSE_CHOICES = [
        ('IT', 'IT'),
        ('Engineering', 'Engineering'),
        ('Medical', 'Medical'),
        ('Business', 'Business'),
        ('Arts', 'Arts'),
        ('Science', 'Science'),
    ]

    SUB_COLUMN_CHOICES = [
        ('', '---------'),
        ('Web Development', 'Web Development'),
        ('Data Science', 'Data Science'),
        ('Networking', 'Networking'),
        ('Cyber Security', 'Cyber Security'),
        ('Computer Science Engineering (CSE)', 'Computer Science Engineering (CSE)'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('MBBS (Bachelor of Medicine & Bachelor of Surgery)', 'MBBS (Bachelor of Medicine & Bachelor of Surgery)'),
        ('BDS (Bachelor of Dental Surgery)', 'BDS (Bachelor of Dental Surgery)'),
        ('BAMS (Ayurveda)', 'BAMS (Ayurveda)'),
        ('BHMS (Homeopathy)', 'BHMS (Homeopathy)'),
        ('Accounting', 'Accounting'),
        ('Marketing', 'Marketing'),
        ('Finance', 'Finance'),
        ('Human Resources', 'Human Resources'),
        ('Painting', 'Painting'),
        ('Music', 'Music'),
        ('Dance', 'Dance'),
        ('Literature', 'Literature'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
        ('Mathematics', 'Mathematics'),
    ]

    name = models.CharField(max_length=255, choices=COURSE_CHOICES)
    sub_column = models.CharField(max_length=255, choices=SUB_COLUMN_CHOICES, blank=True)
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
        if self.name:
            prefix = self.name[:3].upper()
        else:
            prefix = 'GEN'
        
        # Generate 5 random digits
        digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        
        return f"{prefix}{digits}"

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)  # Changed back to Staff
    enrolled_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'staff')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.staff.full_name} enrolled in {self.course.name}"
