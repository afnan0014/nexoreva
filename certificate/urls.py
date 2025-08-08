from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_certificate, name='generate_certificate'),
    path('get-whatsapp-share/', views.get_whatsapp_share_link_ajax, name='get_whatsapp_share_link_ajax'),
    path('certificates/', views.certificate_list, name='certificate_list'),
]
