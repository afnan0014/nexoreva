# course/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from staff.models import Staff
from .models import Course, Enrollment, CourseCategory, SubCourse
from .forms import CourseForm
from django.contrib import messages

def course_list(request):
    courses = Course.objects.all().select_related('name', 'sub_column')
    return render(request, 'course/course_list.html', {'courses': courses})

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        
        # Before validation, set the sub_courses queryset based on the selected course
        if form.data.get('name'):
            try:
                course_category = CourseCategory.objects.get(id=form.data['name'])
                form.fields['sub_column'].queryset = SubCourse.objects.filter(course_category=course_category).order_by('name')
            except (CourseCategory.DoesNotExist, ValueError):
                pass
        
        if form.is_valid():
            form.save()
            return redirect('course_list')
        else:
            # If form is invalid, we need to populate sub_courses for the selected course
            if form.cleaned_data.get('name'):
                form.fields['sub_column'].queryset = SubCourse.objects.filter(course_category=form.cleaned_data['name']).order_by('name')
            # If no course selected or validation failed, show error message
            if not form.cleaned_data.get('name'):
                form.add_error('name', 'Please select a course category first.')
    else:
        form = CourseForm()
        
        # Pre-fill form with data from URL parameters (from create_course)
        course_name = request.GET.get('course_name')
        sub_courses = request.GET.get('sub_courses', '')
        
        if course_name:
            # Try to get or create the course category
            course_category, created = CourseCategory.objects.get_or_create(name=course_name)
            form.initial['name'] = course_category.id
            
            # If sub courses are provided, create them and set the first one
            if sub_courses:
                sub_courses_list = sub_courses.split('|')
                for sub_course_name in sub_courses_list:
                    if sub_course_name.strip():
                        sub_course, created = SubCourse.objects.get_or_create(
                            course_category=course_category,
                            name=sub_course_name.strip()
                        )
                        if not form.initial.get('sub_column'):
                            form.initial['sub_column'] = sub_course.id
            
            # Set the sub_courses queryset for the selected course
            form.fields['sub_column'].queryset = SubCourse.objects.filter(course_category=course_category).order_by('name')
    
    return render(request, 'course/add_course.html', {'form': form})

def create_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        # Use getlist to get all sub_courses from the array format
        sub_courses_list = request.POST.getlist('sub_courses[]')
        
        if course_name:
            # Create the course category
            course_category, created = CourseCategory.objects.get_or_create(name=course_name)
            
            # Filter out empty sub-course names
            sub_courses_list = [name.strip() for name in sub_courses_list if name.strip()]
            
            # Ensure at least one sub-course is provided
            if not sub_courses_list:
                # If no sub-courses provided, create a default one
                default_sub_course, created = SubCourse.objects.get_or_create(
                    course_category=course_category,
                    name=f"{course_name} - General"
                )
                sub_courses_list = [default_sub_course.name]
            
            # Create sub courses
            created_sub_courses = []
            for sub_course_name in sub_courses_list:
                sub_course, created = SubCourse.objects.get_or_create(
                    course_category=course_category,
                    name=sub_course_name
                )
                created_sub_courses.append(sub_course)
            
            # Ensure at least one sub-course exists
            if not created_sub_courses:
                default_sub_course, created = SubCourse.objects.get_or_create(
                    course_category=course_category,
                    name=f"{course_name} - General"
                )
                created_sub_courses.append(default_sub_course)
            
            # Join sub-courses for URL parameters
            sub_courses_param = '|'.join([sub.name for sub in created_sub_courses])
            
            # Redirect to add course form with pre-filled data
            return redirect(f"{reverse('add_course')}?course_name={course_name}&sub_courses={sub_courses_param}")
        else:
            # If no course name provided, redirect back with error
            return redirect('create_course')
    
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
        # Set the sub_courses queryset for existing instances
        if course.name:
            form.fields['sub_column'].queryset = SubCourse.objects.filter(course_category=course.name).order_by('name')
    
    return render(request, 'course/edit_course.html', {'form': form, 'course': course})

@require_http_methods(["GET"])
def get_sub_courses(request):
    """AJAX endpoint to get sub-courses for a selected course category"""
    course_category_id = request.GET.get('course_category_id')
    if course_category_id:
        try:
            course_category = CourseCategory.objects.get(id=course_category_id)
            sub_courses = SubCourse.objects.filter(course_category=course_category).values('id', 'name')
            return JsonResponse({'sub_courses': list(sub_courses)})
        except CourseCategory.DoesNotExist:
            return JsonResponse({'sub_courses': []})
    return JsonResponse({'sub_courses': []})

def delete_course(request, course_id):
    """Delete a course"""
    if request.method == 'POST':
        try:
            course = Course.objects.get(id=course_id)
            course.delete()
        except Course.DoesNotExist:
            pass
        except Exception as e:
            pass
    
    return redirect('course_list')
