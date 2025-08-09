from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['staff', 'course', 'certificate_id', 'issue_date', 'generated_on']
    list_filter = ['issue_date', 'generated_on', 'course']
    search_fields = ['staff__full_name', 'course__name', 'certificate_id']
    readonly_fields = ['certificate_id', 'generated_on']
    date_hierarchy = 'generated_on'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('staff', 'course')
