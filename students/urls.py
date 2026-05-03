from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='profile_edit'),
    path('rental/edit/', views.edit_rental, name='rental_edit'),
    path('rental/toggle-payment/', views.toggle_payment, name='toggle_payment'),
    path('api/districts/', views.districts_by_region, name='districts_by_region'),
]
