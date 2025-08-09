from django.urls import path
from . import views

urlpatterns = [
    path('track/', views.payment_tracking, name='payment_tracking'),
    path('<int:staff_id>/<int:course_id>/', views.view_more, name='view_more'),
]
