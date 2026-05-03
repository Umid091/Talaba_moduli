from django.contrib import admin
from .models import Region, District, Faculty, Group, StudentProfile, RentalInfo


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    search_fields = ('name', 'short_name')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'course')
    list_filter = ('faculty', 'course')
    search_fields = ('name',)


class RentalInfoInline(admin.StackedInline):
    model = RentalInfo
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty', 'group', 'course', 'housing_type', 'profile_completed')
    list_filter = ('housing_type', 'faculty', 'course', 'profile_completed')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    inlines = [RentalInfoInline]


@admin.register(RentalInfo)
class RentalInfoAdmin(admin.ModelAdmin):
    list_display = ('student', 'address', 'monthly_price', 'is_paid', 'last_payment_date')
    list_filter = ('is_paid', 'region')
    search_fields = ('address', 'owner_full_name')
