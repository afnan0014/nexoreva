from django.db import models

# Create your models here.
from django.db import models
from course.models import Enrollment
from decimal import Decimal

class Payment(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount} on {self.date} for {self.enrollment}"

    @property
    def total_paid_for_enrollment(self):
        """
        Returns the total paid so far for the enrollment this payment belongs to.
        """
        total = self.enrollment.payments.aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        return total

    @property
    def due_amount(self):
        """
        Returns the remaining due amount for the enrollment.
        """
        total_fee = self.enrollment.course.fees
        return total_fee - self.total_paid_for_enrollment
