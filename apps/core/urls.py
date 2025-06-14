from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('apply/', views.apply, name='apply'),
    path('payment/', views.payment_view, name='payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-success/', views.payment_success, name='payment_success'),
]