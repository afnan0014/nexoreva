from django.urls import path
from .views import dashboard_view, user_login, user_logout


urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
