from django.shortcuts import render
from staff.models import Staff
from workassignment.models import WorkAssignment
from . forms import TaskStatusUpdateForm

# Create your views here.

def task_status(request):
    error_message = None
    assigned_tasks = None
    staff_name = None
    staff_code = None

    if request.method == "POST":
        staff_code = request.POST.get('staff_code', '').strip()

        if staff_code:
            try:
                staff_obj = Staff.objects.get(staff_code=staff_code)
                staff_name = staff_obj.full_name
                staff_code = staff_obj.staff_code
                assigned_tasks = WorkAssignment.objects.filter(assigned_to=staff_obj)
                
                # If no tasks found, still show the staff info but with empty tasks
                if not assigned_tasks.exists():
                    assigned_tasks = []  # Empty queryset to show the section
                    
            except Staff.DoesNotExist:
                error_message = "No staff found with this code."
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
        else:
            error_message = "Please enter a staff code."

    return render(request, 'task_trakking/task_status.html', {
        'assigned_tasks': assigned_tasks,
        'error_message': error_message,
        'name': staff_name,
        'staff_code': staff_code
    })

def update_status(request, staff_id):
    try:
        staff = Staff.objects.get(staff_code=staff_id)
        success_message = None
        error_message = None
        
        if request.method == 'POST':
            form = TaskStatusUpdateForm(request.POST)
            if form.is_valid():
                staff_code = form.cleaned_data['staff_code']
                task_code = form.cleaned_data['task_code']
                new_status = form.cleaned_data['status']
                
                # Get the task and update its status
                try:
                    task = WorkAssignment.objects.get(task_code=task_code, assigned_to=staff)
                    task.status = new_status
                    task.save()
                    success_message = f"Status updated successfully! Task '{task.task_title}' is now {new_status}."
                    
                    # Reset form with same staff code
                    form = TaskStatusUpdateForm(initial={'staff_code': staff.staff_code})
                except WorkAssignment.DoesNotExist:
                    error_message = "Task not found or not assigned to this staff member."
            else:
                error_message = "Please correct the errors below."
        else:
            form = TaskStatusUpdateForm(initial={'staff_code': staff.staff_code})
        
        return render(request, 'task_trakking/update_status.html', {
            'frm': form,
            'staff_name': staff.full_name,
            'success_message': success_message,
            'error_message': error_message
        })
        
    except Staff.DoesNotExist:
        error_message = "Staff not found."
        form = TaskStatusUpdateForm()
        return render(request, 'task_trakking/update_status.html', {
            'frm': form,
            'error_message': error_message
        })
