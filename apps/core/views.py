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

def payment_view(request):
    """Handle payment view with application data from session"""
    # Get application data from session
    application_data = request.session.get('application_data', {})
    course_price = 20000
    
    if not application_data:
        # If no application data, redirect to application form
        return redirect('core:apply')
        
    context = {
        'application_data': application_data,
        'course_price': 20000,
        'email': application_data.get('email', ''),
        'full_name': f"{application_data.get('first_name', '')} {application_data.get('last_name', '')}",
        'phone': application_data.get('phone', ''),
    }
    
    return render(request, 'core/payment.html', context)

def payment_success(request):
    """Show payment success page only if payment was completed"""
    
    # Check if payment has been completed
    if not request.session.get('payment_completed', False):
        messages.error(request, "Please complete your payment before accessing this page.")
        return redirect('core:payment')  # Redirect to the payment page
    
    context = {
        'payment_reference': request.session.get('payment_reference', '')
    }
    
    # Optional: Clear the payment flag after showing the success page once
    # This prevents refreshing the success page multiple times
    request.session['payment_completed'] = False
    
    return render(request, 'core/payment_success.html', context)

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
            email_subject = f'Contact Form: {subject} - From {name}'  # Fixed this line
            email_body = f"""
New contact form submission from TradeWise Academy website:

Name: {name}
Email: {email}
Subject: {subject}  # Fixed this line

Message:
{message}

---
This message was sent from the TradeWise Academy contact form.
Reply directly to: {email}
            """
            
            try:
                # Send email
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    ['themosempire@gmail.com'],  # Updated with your actual email
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! We\'ll get back to you within 24 hours.')
                form = ContactForm()  # Reset form after successful submission
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
            # Instead of saving to database, store in session
            application_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'date_of_birth': form.cleaned_data['date_of_birth'].strftime('%Y-%m-%d'),
                'country': form.cleaned_data['country'],
                'city': form.cleaned_data['city'],
                'education_level': form.cleaned_data['education_level'],
                'current_occupation': form.cleaned_data['current_occupation'],
                'annual_income': form.cleaned_data['annual_income'],
                'trading_experience': form.cleaned_data['trading_experience'],
                'previous_trading_education': form.cleaned_data['previous_trading_education'],
                'trading_goals': form.cleaned_data['trading_goals'],
                'desired_course': form.cleaned_data['desired_course'],
                'study_time_per_week': form.cleaned_data['study_time_per_week'],
                'start_date_preference': form.cleaned_data['start_date_preference'].strftime('%Y-%m-%d'),
                'motivation': form.cleaned_data['motivation'],
                'financial_goals': form.cleaned_data['financial_goals'],
                'risk_tolerance': form.cleaned_data['risk_tolerance'],
                'how_did_you_hear': form.cleaned_data['how_did_you_hear'],
                'additional_comments': form.cleaned_data['additional_comments'],
                # Store form fields in session
            }
            request.session['application_data'] = application_data
            
            # Calculate course price
            course_prices = {
                'basic': 20000,
                'intermediate': 30000,
                'advanced': 40000,
                'elite': 50000
    # Add all your course options here with their prices
            }
            course_price = course_prices.get(form.cleaned_data['desired_course'], 20000)
            request.session['course_price'] = course_price
            
            # Redirect to payment page
            return redirect('core:payment')
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

@csrf_exempt
@require_http_methods(["POST"])
def payment_callback(request):
    """Handle client-side payment callback"""
    data = json.loads(request.body)
    reference = data.get('reference')
    
    # Get application data from session
    application_data = request.session.get('application_data', {})
    
    if application_data:
        try:
            from datetime import datetime
            
            application = Application(
                first_name=application_data['first_name'],
                last_name=application_data['last_name'],
                email=application_data['email'],
                phone=application_data['phone'],
                date_of_birth=datetime.strptime(application_data['date_of_birth'], '%Y-%m-%d').date(),
                country=application_data['country'],
                city=application_data['city'],
                education_level=application_data['education_level'],
                current_occupation=application_data['current_occupation'],
                annual_income=application_data['annual_income'],
                trading_experience=application_data['trading_experience'],
                previous_trading_education=application_data['previous_trading_education'],
                trading_goals=application_data['trading_goals'],
                desired_course=application_data['desired_course'],
                study_time_per_week=application_data['study_time_per_week'],
                start_date_preference=datetime.strptime(application_data['start_date_preference'], '%Y-%m-%d').date(),
                motivation=application_data['motivation'],
                financial_goals=application_data['financial_goals'],
                risk_tolerance=application_data['risk_tolerance'],
                how_did_you_hear=application_data['how_did_you_hear'],
                additional_comments=application_data['additional_comments'],
                # Payment info
                status='enrolled',  # Set status to enrolled immediately
                payment_status='paid',
                payment_reference=reference,
                payment_date=timezone.now()
            )
            application.save()
            
            # Add this: Set a payment success flag in the session
            request.session['payment_completed'] = True
            request.session['payment_reference'] = reference
            
            # Clear application data
            if 'application_data' in request.session:
                del request.session['application_data']
            if 'course_price' in request.session:
                del request.session['course_price']
                
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print(f"Error saving application: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'No application data found'}, status=400)
    
    
    
    
def payment_success(request):
    """Show payment success page only if payment was completed"""
    
    # Check if payment has been completed
    if not request.session.get('payment_completed', False):
        messages.error(request, "Please complete your payment before accessing this page.")
        return redirect('core:payment')  # Redirect to the payment page
    
    context = {
        'payment_reference': request.session.get('payment_reference', '')
    }
    

    request.session['payment_completed'] = False
    
    return render(request, 'core/payment_success.html', context)