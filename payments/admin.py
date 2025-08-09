from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount', 'date', 'due_amount', 'created_at')
    list_filter = ('date',)
    search_fields = ('enrollment__staff__full_name', 'enrollment__course__name')
