from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('apply/', views.apply, name='apply'),
     path('payment/', views.payment_view, name='payment'),  # Simple payment
    path('payment/<int:application_id>/', views.payment_view, name='payment_with_app'),  # Payment with application
    path('payment-success/', views.payment_success, name='payment_success'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
]