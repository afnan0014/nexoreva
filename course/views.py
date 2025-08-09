# course/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from staff.models import Staff
from .models import Course, Enrollment
from .forms import CourseForm

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course/course_list.html', {'courses': courses})

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
        
        # Pre-fill form with data from URL parameters (from create_course)
        course_name = request.GET.get('course_name')
        sub_courses = request.GET.get('sub_courses', '')
        
        if course_name:
            form.initial['name'] = course_name
        if sub_courses:
            # Set the first sub course as the sub_column
            sub_courses_list = sub_courses.split('|')
            if sub_courses_list:
                form.initial['sub_column'] = sub_courses_list[0]
    
    return render(request, 'course/add_course.html', {'form': form})

def create_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        sub_courses = request.POST.get('sub_courses', '')
        
        if course_name:
            # Redirect to add course form with pre-filled data
            return redirect(f"{reverse('add_course')}?course_name={course_name}&sub_courses={sub_courses}")
    
    return render(request, 'course/create_course.html')

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'course/course_detail.html', {
        'course': course,
        'enrollments': enrollments
    })

def enroll_user(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        staff_code = request.POST.get('staff_code')
        try:
            staff = Staff.objects.get(staff_code=staff_code)
        except Staff.DoesNotExist:
            return render(request, 'course/enroll_user.html', {
                'course': course,
                'error': 'No staff member found with this unicode.'
            })

        if Enrollment.objects.filter(course=course, staff=staff).exists():
            return render(request, 'course/enroll_user.html', {
                'course': course,
                'error': 'This staff member is already enrolled.'
            })

        Enrollment.objects.create(course=course, staff=staff)
        return redirect('course_detail', course_id=course.id)

    return render(request, 'course/enroll_user.html', {'course': course})

def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course/edit_course.html', {'form': form, 'course': course})
