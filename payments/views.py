from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from course.models import Enrollment, Course
from staff.models import Staff
from .forms import PaymentSearchForm
from .models import Payment
from django.db.models import Sum

def payment_tracking(request):
    form = PaymentSearchForm(request.GET or None)
    results = []

    if form.is_valid():
        staff_code = form.cleaned_data.get('staff_code')
        course_code = form.cleaned_data.get('course_code')

        if staff_code and not course_code:
            # All courses for one staff
            staff = get_object_or_404(Staff, staff_code=staff_code)
            results = Enrollment.objects.filter(staff=staff)

        elif course_code and not staff_code:
            # All staff for one course
            course = get_object_or_404(Course, unicode=course_code)
            results = Enrollment.objects.filter(course=course)

        elif staff_code and course_code:
            # Specific staff + specific course
            staff = get_object_or_404(Staff, staff_code=staff_code)
            course = get_object_or_404(Course, unicode=course_code)
            results = Enrollment.objects.filter(staff=staff, course=course)

        # Attach total_paid and due_amount to each enrollment
        for enrollment in results:
            total_paid = Payment.objects.filter(enrollment=enrollment).aggregate(
                total=Sum('amount')
            )['total'] or 0
            enrollment.total_paid = total_paid
            enrollment.due_amount = enrollment.course.fees - total_paid

    return render(request, 'payments/payment_tracking.html', {
        'form': form,
        'results': results
    })



from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment
from staff.models import Staff
from course.models import Course
from .forms import PaymentForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment
from course.models import Enrollment  # adjust import path
from staff.models import Staff
from course.models import Course
from .forms import PaymentForm

def view_more(request, staff_id, course_id):
    # Get the enrollment for this staff and course
    enrollment = get_object_or_404(Enrollment, staff_id=staff_id, course_id=course_id)
    
    payments = Payment.objects.filter(enrollment=enrollment).order_by('-date')
    
    total_paid = sum(p.amount for p in payments)
    due_amount = enrollment.course.fees - total_paid

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.enrollment = enrollment  # link to enrollment
            payment.save()
            return redirect('view_more', staff_id=staff_id, course_id=course_id)
    else:
        form = PaymentForm()

    return render(request, 'payments/view_more.html', {
        'enrollment': enrollment,
        'course': enrollment.course,   
        'payments': payments,
        'total_paid': total_paid,
        'due_amount': due_amount,
        'form': form,
    })
