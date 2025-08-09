from django.db import models
from staff.models import Staff
from course.models import Course


class Certificate(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate_file = models.ImageField(upload_to='certificates/')
    issue_date = models.DateField()
    generated_on = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            # Generate unique certificate ID
            import random
            self.certificate_id = f"CERT{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.staff.full_name} - {self.course.name} Certificate"
    
    class Meta:
        unique_together = ('staff', 'course')  # Prevent duplicate certificates
