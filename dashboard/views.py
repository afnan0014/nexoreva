from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from attendance.models import Attendance


# Custom Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'dashboard/login.html')


# Custom Logout View
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    attendance = Attendance.objects.select_related('staff').all()

    context = {
        'total_staff': 12,
        'total_departments': 4,
        'total_interns': 5,
        'attendance': attendance
    }
    return render(request, 'dashboard/dashboard.html', context)
