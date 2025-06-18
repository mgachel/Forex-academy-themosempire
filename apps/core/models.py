from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import format_html

class Application(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner', 'Complete Beginner (0-6 months)'),
        ('novice', 'Novice (6 months - 2 years)'),
        ('intermediate', 'Intermediate (2-5 years)'),
        ('advanced', 'Advanced (5+ years)'),
    ]
    
    COURSE_TYPE_CHOICES = [
        ('premium', 'complete trading course'),
    ]
    
   
    
    EDUCATION_CHOICES = [
        ('high_school', 'High School'),
        ('diploma', 'Diploma/Certificate'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    
    # Background Information
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    current_occupation = models.CharField(max_length=100)
    annual_income = models.CharField(max_length=50, blank=True)
    
    # Trading Experience
    trading_experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    previous_trading_education = models.TextField(
        blank=True, 
        help_text="Describe any previous trading courses, books, or education you've had"
    )
    trading_goals = models.TextField(
        help_text="What do you hope to achieve through this program?"
    )
    
    # Course Selection
    desired_course = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES)
    
    
    # Commitment & Availability
    study_time_per_week = models.IntegerField(
        help_text="How many hours per week can you dedicate to studying?"
    )
    start_date_preference = models.DateField(
        help_text="When would you like to start the program?"
    )
    
    # Motivation & Goals
    motivation = models.TextField(
        help_text="Why do you want to learn forex trading? What motivates you?"
    )
    financial_goals = models.TextField(
        help_text="What are your short-term and long-term financial goals?"
    )
    risk_tolerance = models.CharField(
        max_length=50,
        choices=[
            ('conservative', 'Conservative - I prefer steady, lower returns'),
            ('moderate', 'Moderate - I accept some risk for better returns'),
            ('aggressive', 'Aggressive - I\'m willing to take high risks for high returns'),
        ]
    )
    
    # Additional Information
    how_did_you_hear = models.CharField(
        max_length=100,
        help_text="How did you hear about Themosempire Fx?"
    )
    additional_comments = models.TextField(
        blank=True,
        help_text="Any additional information you'd like us to know?"
    )
    
    # Application Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_applications'
    )
    admin_notes = models.TextField(blank=True)
    
    # Payment Information
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    def get_course_price(self):
        """Return course price based on selected course type"""
        prices = {
            'course_price': 200000,
        }
        
        return prices.get(self.desired_course, 200000)  # Default to 2500 if course not found
    
    def colored_status(self):
        return format_html('<span style="color: green;">{}</span>', self.status)
