from django.urls import path
from . import views

app_name = 'tutors'

urlpatterns = [
    path('', views.tutor_dashboard, name='dashboard'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
]
