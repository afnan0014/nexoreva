from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import uuid


class WorkAssignment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    task_code = models.CharField(max_length=20, unique=True, editable=False)
    task_title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    assigned_to = models.ForeignKey('staff.Staff', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
        if not self.task_code:
            self.task_code = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.task_title

@receiver(post_save, sender=WorkAssignment)
def send_task_notification(sender, instance, created, **kwargs):
    if created:
        subject = f"New Task Assigned: {instance.task_title}"
        message = (
            f"Hello {instance.assigned_to.full_name},\n\n"
            f"You have been assigned a new task.\n\n"
            f"Task Code: {instance.task_code}\n"
            f"Title: {instance.task_title}\n"
            f"Description: {instance.description}\n"
            f"Start Date: {instance.start_date}\n"
            f"End Date: {instance.end_date}\n\n"
            f"Please log in to the system for more details."
        )
        recipient_list = [instance.assigned_to.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
