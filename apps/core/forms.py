from django import forms

from .models import Application
from datetime import date, timedelta
class ContactForm(forms.Form):
    SUBJECT_CHOICES = [
        ('', 'Select a topic'),
        ('course_inquiry', 'Course Inquiry'),
        ('trading_consultation', 'Trading Consultation'),
        ('technical_support', 'Technical Support'),
        ('partnership', 'Partnership Opportunity'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'Enter your full name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'your.email@example.com'
        })
    )
    
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white focus:outline-none'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none resize-none',
            'placeholder': 'Tell us how we can help you...',
            'rows': 5
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message
    
    
    
    


class ContactForm(forms.Form):
    # Keep your existing ContactForm code here...
    SUBJECT_CHOICES = [
        ('', 'Select a topic'),
        ('course_inquiry', 'Course Inquiry'),
        ('trading_consultation', 'Trading Consultation'),
        ('technical_support', 'Technical Support'),
        ('partnership', 'Partnership Opportunity'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'Enter your full name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'your.email@example.com'
        })
    )
    
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white focus:outline-none'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none resize-none',
            'placeholder': 'Tell us how we can help you...',
            'rows': 5
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'country', 'city', 'education_level', 'current_occupation', 'annual_income',
            'trading_experience', 'previous_trading_education', 'trading_goals',
            'desired_course', 'payment_plan', 'study_time_per_week', 'start_date_preference',
            'motivation', 'financial_goals', 'risk_tolerance', 'how_did_you_hear',
            'additional_comments'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Common CSS classes
        text_input_class = 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none'
        select_class = 'w-full px-4 py-3 rounded-xl form-input text-white focus:outline-none'
        textarea_class = 'w-full px-4 py-3 rounded-xl form-input text-white placeholder-gray-400 focus:outline-none resize-vertical'
        
        # Apply styling to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': text_input_class})
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({'class': text_input_class})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': text_input_class})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': text_input_class,
                    'type': 'date'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': select_class})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': textarea_class, 'rows': 4})
        
        # Specific field customizations
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['email'].widget.attrs['placeholder'] = 'your.email@example.com'
        self.fields['phone'].widget.attrs['placeholder'] = '+233 XX XXX XXXX'
        self.fields['country'].widget.attrs['placeholder'] = 'e.g., Ghana'
        self.fields['city'].widget.attrs['placeholder'] = 'e.g., Accra'
        self.fields['current_occupation'].widget.attrs['placeholder'] = 'e.g., Software Engineer'
        self.fields['annual_income'].widget.attrs['placeholder'] = 'Optional - e.g., $20,000 - $50,000'
        self.fields['how_did_you_hear'].widget.attrs['placeholder'] = 'e.g., Google search, Social media, Friend referral'
        
        # Set minimum date for date of birth (18 years old)
        min_date = date.today() - timedelta(days=18*365)
        self.fields['date_of_birth'].widget.attrs['max'] = min_date.strftime('%Y-%m-%d')
        
        # Set minimum date for start preference (today)
        self.fields['start_date_preference'].widget.attrs['min'] = date.today().strftime('%Y-%m-%d')
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            raise forms.ValidationError("You must be at least 18 years old to apply.")
        if age > 100:
            raise forms.ValidationError("Please enter a valid date of birth.")
        
        return dob
    
    def clean_study_time_per_week(self):
        hours = self.cleaned_data['study_time_per_week']
        if hours < 1:
            raise forms.ValidationError("You must commit at least 1 hour per week.")
        if hours > 168:  # 24 hours * 7 days
            raise forms.ValidationError("Please enter a realistic number of hours per week.")
        return hours
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if Application.objects.filter(email=email, status__in=['pending', 'under_review', 'approved', 'enrolled']).exists():
            raise forms.ValidationError("An application with this email already exists.")
        return email