from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import requests
from .forms import ContactForm, ApplicationForm
from .models import Application

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html') 

def payment_view(request, application_id=None):
    """Handle payment view with optional application_id"""
    if application_id:
        try:
            application = Application.objects.get(id=application_id)
            course_price = application.get_course_price()
            
            context = {
                'application': application,
                'course_price': course_price,
            }
            
            return render(request, 'core/payment.html', context)
            
        except Application.DoesNotExist:
            messages.error(request, 'Application not found.')
            return redirect('core:home')
    else:
        # Simple payment without application
        context = {
            'course_price': 1500,  # Default price
        }
        return render(request, 'core/payment.html', context)

def payment_success(request):
    return render(request, 'core/payment_success.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get cleaned data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Create email subject and body
            email_subject = f'Contact Form: {dict(form.SUBJECT_CHOICES)[subject]} - From {name}'
            email_body = f"""
New contact form submission from TradeWise Academy website:

Name: {name}
Email: {email}
Subject: {dict(form.SUBJECT_CHOICES)[subject]}

Message:
{message}

---
This message was sent from the TradeWise Academy contact form.
Reply directly to: {email}
            """
            
            try:
                # Send email (you'll need to configure email settings)
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@tradewise.com',
                    ['ayarisiamos@tradewise.com'],  # Replace with actual email
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! We\'ll get back to you within 24 hours.')
                # Create a new empty form after successful submission
                form = ContactForm()
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again or contact us directly via WhatsApp.')
                print(f"Email error: {e}")  # For debugging
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = ContactForm()
    
    # Always pass the form to the template
    return render(request, 'core/contact.html', {'form': form})

def apply(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            # Redirect to payment with the application ID
            return redirect('core:payment_with_app', application_id=application.id)
            
            # Send confirmation email to applicant (this code won't execute due to return above)
            try:
                send_confirmation_email(application)
                send_admin_notification_email(application)
                
                messages.success(
                    request, 
                    f'Thank you {application.first_name}! Your application has been submitted successfully. '
                    f'You will receive a confirmation email shortly. We will review your application and get back to you within 2-3 business days.'
                )
                return redirect('core:apply')
            except Exception as e:
                messages.warning(
                    request,
                    'Your application was submitted successfully, but there was an issue sending the confirmation email. '
                    'We will still process your application and contact you soon.'
                )
                print(f"Email error: {e}")
                return redirect('core:apply')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = ApplicationForm()
    
    return render(request, 'core/apply.html', {'form': form})

def send_confirmation_email(application):
    """Send confirmation email to the applicant"""
    subject = f'Application Received - TradeWise Academy'
    
    # Calculate course price
    course_price = application.get_course_price()
    
    message = f"""
Dear {application.first_name} {application.last_name},

Thank you for applying to TradeWise Academy! We have received your application for the {application.get_desired_course_display()}.

Application Details:
- Course: {application.get_desired_course_display()}
- Payment Plan: {application.get_payment_plan_display()}
- Course Fee: ${course_price:,.0f}
- Preferred Start Date: {application.start_date_preference.strftime('%B %d, %Y')}

What happens next?
1. Our team will review your application within 2-3 business days
2. You will receive an email with our decision
3. If approved, you'll receive enrollment instructions and payment details
4. You can start your trading journey with Ayarisi Amos!

If you have any questions, please don't hesitate to contact us:
- WhatsApp: +233 XXX XXX XXX
- Email: ayarisiamos@tradewise.com

Best regards,
The TradeWise Academy Team

---
This is an automated message. Please do not reply to this email.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@tradewise.com',
        [application.email],
        fail_silently=False,
    )

def send_admin_notification_email(application):
    """Send notification email to admin"""
    subject = f'New Application: {application.full_name} - {application.get_desired_course_display()}'
    
    message = f"""
New application received for TradeWise Academy:

Applicant Information:
- Name: {application.full_name}
- Email: {application.email}
- Phone: {application.phone}
- Country: {application.country}
- Age: {application.date_of_birth}

Course Details:
- Course: {application.get_desired_course_display()}
- Payment Plan: {application.get_payment_plan_display()}
- Trading Experience: {application.get_trading_experience_display()}
- Study Time: {application.study_time_per_week} hours/week

Motivation:
{application.motivation}

Trading Goals:
{application.trading_goals}

Review this application in the admin panel: /admin/core/application/{application.id}/

---
TradeWise Academy Application System
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@tradewise.com',
        ['ayarisiamos@tradewise.com'],  # Replace with actual admin email
        fail_silently=False,
    )

@csrf_exempt
@require_http_methods(["POST"])
def verify_payment(request):
    """Verify payment with Paystack and update application status"""
    try:
        # Debug: Print request data
        print("Request body:", request.body)
        print("Request POST:", request.POST)
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        reference = data.get('reference')
        application_id = data.get('application_id')
        
        print(f"Reference: {reference}")
        print(f"Application ID: {application_id}")
        
        if not reference:
            return JsonResponse({'success': False, 'message': 'Missing payment reference'})
            
        if not application_id:
            return JsonResponse({'success': False, 'message': 'Missing application ID'})
        
        # Get the application
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found'})
        
        # Verify payment with Paystack
        headers = {
            'Authorization': f'Bearer sk_test_your_secret_key_here',  # Replace with your actual secret key
            'Content-Type': 'application/json',
        }
        
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers
        )
        
        if response.status_code == 200:
            payment_data = response.json()
            
            if payment_data['status'] and payment_data['data']['status'] == 'success':
                # Update application status
                application.payment_status = 'paid'
                application.payment_reference = reference
                application.payment_date = timezone.now()
                application.status = 'enrolled'  # Update status to enrolled
                application.save()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Payment verified successfully',
                    'application_id': application_id,
                    'reference': reference
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Payment verification failed - payment not successful'
                })
        else:
            return JsonResponse({
                'success': False, 
                'message': f'Unable to verify payment with Paystack. Status: {response.status_code}'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        print(f"Error in verify_payment: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': f'Error verifying payment: {str(e)}'
        })

# Remove the duplicate payment_view function that was at the bottom