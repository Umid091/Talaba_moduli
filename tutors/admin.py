from django.contrib import admin
from .models import TutorProfile


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('faculties', 'groups')
