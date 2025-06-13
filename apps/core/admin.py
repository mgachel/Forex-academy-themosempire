from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 
        'email', 
        'desired_course', 
        'colored_status', 
        'course_price_display',
        'applied_at',
        'country'
    ]
    
    list_filter = [
        'status',
        'desired_course',
        'payment_plan',
        'trading_experience',
        'education_level',
        'country',
        'applied_at',
        'reviewed_at'
    ]
    
    search_fields = [
        'first_name',
        'last_name', 
        'email',
        'phone',
        'country',
        'city'
    ]
    
    readonly_fields = [
        'applied_at',
        'course_price_display',
        'full_name_display'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                ('first_name', 'last_name'),
                'email',
                'phone',
                'date_of_birth',
                ('country', 'city'),
            )
        }),
        ('Background', {
            'fields': (
                'education_level',
                'current_occupation',
                'annual_income',
            )
        }),
        ('Trading Experience', {
            'fields': (
                'trading_experience',
                'previous_trading_education',
                'trading_goals',
            )
        }),
        ('Course & Payment', {
            'fields': (
                'desired_course',
                'payment_plan',
                'course_price_display',
            )
        }),
        ('Commitment', {
            'fields': (
                'study_time_per_week',
                'start_date_preference',
            )
        }),
        ('Motivation & Goals', {
            'fields': (
                'motivation',
                'financial_goals',
                'risk_tolerance',
            )
        }),
        ('Additional Info', {
            'fields': (
                'how_did_you_hear',
                'additional_comments',
            )
        }),
        ('Application Status', {
            'fields': (
                'status',
                'applied_at',
                'reviewed_at',
                'reviewed_by',
                'admin_notes',
            )
        }),
    )
    
    actions = ['approve_applications', 'reject_applications', 'mark_under_review']
    
    def colored_status(self, obj):
        colors = {
            'pending': '#ffc107',
            'under_review': '#17a2b8',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'enrolled': '#6f42c1',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    colored_status.short_description = 'Status'
    
    def course_price_display(self, obj):
        price = obj.get_course_price()
        return format_html('${:,.0f}', price)
    course_price_display.short_description = 'Course Price'
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Full Name'
    
    def approve_applications(self, request, queryset):
        updated = queryset.update(
            status='approved',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} applications approved successfully.')
    approve_applications.short_description = 'Approve selected applications'
    
    def reject_applications(self, request, queryset):
        updated = queryset.update(
            status='rejected',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} applications rejected.')
    reject_applications.short_description = 'Reject selected applications'
    
    def mark_under_review(self, request, queryset):
        updated = queryset.update(
            status='under_review',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} applications marked as under review.')
    mark_under_review.short_description = 'Mark as under review'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
