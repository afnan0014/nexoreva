from django.db import models
from django.contrib.auth.models import User
import random

def generate_unique_code(role_prefix):
    number = ''.join(random.choices('0123456789', k=4))
    return f"{role_prefix}{number}"

class Staff(models.Model):
    ROLE_CHOICES = [
        ('Employee', 'Employee'),
        ('Intern', 'Intern'),
    ]

    DEPARTMENT_CHOICES = [
        ('HR', 'HR'),
        ('Engineering', 'Engineering'),
        ('Marketing', 'Marketing'),
        ('Finance', 'Finance'),
        ('Operations', 'Operations'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    ]

    STATUS_CHOICES = [
        ('DocPending', 'DocPending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        
    ]

    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    designation = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    reporting_manager = models.CharField(max_length=100, blank=True, null=True)
    join_date = models.DateField()

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)

    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()

    id_proof = models.FileField(upload_to='id_proofs/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    offer_letter = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    admin_notes = models.TextField(blank=True, null=True)

    staff_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.staff_code:
            prefix = 'nxrint' if self.role == 'Intern' else 'nxremp'
            while True:
                new_code = generate_unique_code(prefix)
                if not Staff.objects.filter(staff_code=new_code).exists():
                    self.staff_code = new_code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
