# course/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),                      # /courses/
    path('add/', views.add_course, name='add_course'),                    # /courses/add/
    path('create/', views.create_course, name='create_course'),           # /courses/create/
    path('<int:course_id>/', views.course_detail, name='course_detail'),  # /courses/1/
    path('<int:course_id>/enroll/', views.enroll_user, name='enroll_user'),  # /courses/1/enroll/
    path('<int:course_id>/edit/', views.edit_course, name='edit_course'),
]
