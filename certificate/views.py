import os
from PIL import Image, ImageDraw, ImageFont
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from staff.models import Staff
from course.models import Course, Enrollment
from .models import Certificate
from .forms import CertificateGenerationForm
from io import BytesIO
import urllib.parse
from datetime import date


def center_text(draw, text, font, y, image_width):
    """Center text horizontally on the image"""
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) // 2
    draw.text((x, y), text, font=font, fill='black')


def get_best_font_size(text, font_path, max_width, start_size):
    """Find the best font size that fits within max_width"""
    if not font_path or not os.path.exists(font_path):
        return ImageFont.load_default(), start_size
        
    for size in range(start_size, 15, -2):
        try:
            font = ImageFont.truetype(font_path, size)
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                return font, size
        except:
            continue
    
    return ImageFont.load_default(), 15


def generate_whatsapp_share_link(certificate):
    """Generate WhatsApp share link with certificate details as text message"""
    # Generate certificate URL
    full_url = f"{settings.DOMAIN_URL if hasattr(settings, 'DOMAIN_URL') else 'http://127.0.0.1:8000'}{certificate.certificate_file.url}"
    
    # Create formatted text message for WhatsApp
    message_text = f"""🎓 CERTIFICATE GENERATED! 🎓

Congratulations {certificate.staff.full_name}!

✅ Course: {certificate.course.name}
🏆 Certificate ID: {certificate.certificate_id}
📅 Issue Date: {certificate.issue_date.strftime('%d %B, %Y')}
📸 Certificate: {full_url}

To download your certificate:
1. Click the link above
2. Save the image to your device
3. Share with family and friends!

Well done on completing the course! 🎉

Best regards,
Certificate Team"""
    
    # URL encode the message for WhatsApp
    encoded_message = urllib.parse.quote(message_text)
    
    # Create WhatsApp share link (works without API)
    whatsapp_link = f"https://wa.me/?text={encoded_message}"
    
    return whatsapp_link


@csrf_exempt
@require_POST
def get_whatsapp_share_link_ajax(request):
    """AJAX endpoint to get WhatsApp share link (no API required)"""
    try:
        certificate_id = request.POST.get('certificate_id')
        
        if not certificate_id:
            return JsonResponse({
                'success': False,
                'error': 'Certificate ID is required.'
            })
        
        certificate = Certificate.objects.get(certificate_id=certificate_id)
        whatsapp_link = generate_whatsapp_share_link(certificate)
        
        return JsonResponse({
            'success': True,
            'whatsapp_link': whatsapp_link,
            'message': 'WhatsApp share link generated successfully!'
        })

    except Certificate.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Certificate not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"Error generating WhatsApp share link: {str(e)}"
        })


def generate_certificate(request):
    """Main view for certificate generation with WhatsApp sharing"""
    certificate_url = None
    certificate_id = None
    whatsapp_share_link = None
    form = CertificateGenerationForm()
    
    # Get all certificates for the list tab
    all_certificates = Certificate.objects.all().order_by('-generated_on')
    today_certificates = Certificate.objects.filter(generated_on__date=date.today())
    unique_courses = Course.objects.filter(certificate__in=all_certificates).distinct()
    
    if request.method == 'POST':
        form = CertificateGenerationForm(request.POST)
        
        if form.is_valid():
            try:
                staff_code = form.cleaned_data['staff_code']
                course_unicode = form.cleaned_data['course_unicode']
                
                # Fetch staff and course objects
                staff_obj = Staff.objects.get(staff_code=staff_code)
                course_obj = Course.objects.get(unicode=course_unicode)
                
                # Check if certificate already exists
                existing_cert = Certificate.objects.filter(
                    staff=staff_obj, 
                    course=course_obj
                ).first()
                
                if existing_cert:
                    messages.info(request, f"Certificate already exists for {staff_obj.full_name}")
                    certificate_url = existing_cert.certificate_file.url
                    certificate_id = existing_cert.certificate_id
                    whatsapp_share_link = generate_whatsapp_share_link(existing_cert)
                    
                    # Update certificate lists
                    all_certificates = Certificate.objects.all().order_by('-generated_on')
                    today_certificates = Certificate.objects.filter(generated_on__date=date.today())
                    unique_courses = Course.objects.filter(certificate__in=all_certificates).distinct()
                    
                    return render(request, 'certificate/generate_certificate.html', {
                        'form': form,
                        'certificate_url': certificate_url,
                        'certificate_id': certificate_id,
                        'whatsapp_share_link': whatsapp_share_link,
                        'all_certificates': all_certificates,
                        'today_certificates': today_certificates,
                        'unique_courses': unique_courses,
                    })
                
                # Generate new certificate (your existing certificate generation code)
                start_date = course_obj.start_date
                end_date = course_obj.end_date
                
                # Check enrollment (optional warning)
                enrollment_exists = Enrollment.objects.filter(
                    staff=staff_obj, 
                    course=course_obj
                ).exists()
                
                if not enrollment_exists:
                    messages.warning(request, f"Note: {staff_obj.full_name} is not enrolled in {course_obj.name}")

                # Load certificate template
                template_path = os.path.join(settings.BASE_DIR, 'certificate', 'static', 'certificate', 'certificate.png')
                
                if not os.path.exists(template_path):
                    messages.error(request, "Certificate template not found.")
                    raise FileNotFoundError("Template file missing")
                
                image = Image.open(template_path)
                draw = ImageDraw.Draw(image)

                # Font configuration
                font_dir = os.path.join(settings.BASE_DIR, 'certificate', 'fonts')
                font_path = os.path.join(font_dir, 'arial.ttf')
                
                if not os.path.exists(font_path):
                    try:
                        import platform
                        if platform.system() == "Windows":
                            font_path = "C:/Windows/Fonts/arial.ttf"
                        elif platform.system() == "Darwin":
                            font_path = "/System/Library/Fonts/Arial.ttf"
                        else:
                            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                        
                        if not os.path.exists(font_path):
                            font_path = None
                    except:
                        font_path = None

                image_width = image.width
                image_height = image.height

                # Perfect positioning
                name_y = int(image_height * 0.50)
                course_y = int(image_height * 0.600)
                date_y = int(image_height * 0.650)
                max_text_width = int(image_width * 0.85)

                # Staff Full Name
                name_start_size = int(image_height * 0.08)
                name_font, actual_name_size = get_best_font_size(
                    staff_obj.full_name, font_path, max_text_width, name_start_size
                )

                if font_path and os.path.exists(font_path):
                    center_text(draw, staff_obj.full_name, name_font, name_y, image_width)
                else:
                    for i in range(4):
                        center_text(draw, staff_obj.full_name, name_font, name_y + i, image_width)

                # Course Information
                course_text = f"Successfully completed the {course_obj.name}"
                if course_obj.sub_column:
                    course_text += f" {course_obj.sub_column}"
                course_text += " Course"
                
                course_start_size = int(image_height * 0.045)
                course_font, actual_course_size = get_best_font_size(
                    course_text, font_path, max_text_width, course_start_size
                )

                if font_path and os.path.exists(font_path):
                    center_text(draw, course_text, course_font, course_y, image_width)
                else:
                    for i in range(2):
                        center_text(draw, course_text, course_font, course_y + i, image_width)

                # Date Information
                date_text = f"{end_date.strftime('%d-%m-%Y')}"
                date_start_size = int(image_height * 0.032)
                date_font, actual_date_size = get_best_font_size(
                    date_text, font_path, max_text_width, date_start_size
                )

                if font_path and os.path.exists(font_path):
                    center_text(draw, date_text, date_font, date_y, image_width)
                else:
                    center_text(draw, date_text, date_font, date_y, image_width)

                # Save certificate to database
                safe_name = staff_obj.full_name.replace(' ', '_').replace('/', '_')
                course_safe_name = course_obj.name.replace(' ', '_').replace('/', '_')
                filename = f"{safe_name}_{course_safe_name}_certificate.png"
                
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                certificate = Certificate(
                    staff=staff_obj,
                    course=course_obj,
                    issue_date=end_date
                )
                
                certificate.certificate_file.save(
                    filename,
                    ContentFile(img_buffer.getvalue()),
                    save=True
                )
                
                certificate_url = certificate.certificate_file.url
                certificate_id = certificate.certificate_id
                whatsapp_share_link = generate_whatsapp_share_link(certificate)
                
                messages.success(request, f'Certificate generated for {staff_obj.full_name}!')

                # Update certificate lists with fresh data
                all_certificates = Certificate.objects.all().order_by('-generated_on')
                today_certificates = Certificate.objects.filter(generated_on__date=date.today())
                unique_courses = Course.objects.filter(certificate__in=all_certificates).distinct()

            except Staff.DoesNotExist:
                messages.error(request, f"Staff with code '{staff_code}' not found.")
            except Course.DoesNotExist:
                messages.error(request, f"Course with code '{course_unicode}' not found.")
            except Exception as e:
                messages.error(request, f"Error generating certificate: {str(e)}")

    return render(request, 'certificate/generate_certificate.html', {
        'form': form,
        'certificate_url': certificate_url,
        'certificate_id': certificate_id,
        'whatsapp_share_link': whatsapp_share_link,
        'all_certificates': all_certificates,
        'today_certificates': today_certificates,
        'unique_courses': unique_courses,
    })


def certificate_list(request):
    """Separate view for certificate list"""
    certificates = Certificate.objects.all().order_by('-generated_on')
    today_certificates = Certificate.objects.filter(generated_on__date=date.today())
    unique_courses = Course.objects.filter(certificate__in=certificates).distinct()
    
    return render(request, 'certificate/certificate_list.html', {
        'certificates': certificates,
        'today_certificates': today_certificates,
        'unique_courses': unique_courses,
    })
