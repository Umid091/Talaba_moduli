import json
import csv

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.forms import UserCreateForm, UserEditForm
from students.forms import (FacultyForm, GroupForm, RegionForm, DistrictForm)
from students.models import (StudentProfile, RentalInfo, Faculty, Group,
                             Region, District)
from tutors.models import TutorProfile
from tutors.views import _filter_students

User = get_user_model()


def _is_admin(user):
    return user.is_authenticated and user.is_admin_role


@login_required
def home(request):
    """Foydalanuvchini roliga qarab tegishli sahifaga yo'naltiradi."""
    user = request.user
    if user.is_admin_role:
        return redirect('dashboard:admin_home')
    if user.is_tutor_role:
        return redirect('tutors:dashboard')
    if user.is_student_role:
        return redirect('students:dashboard')
    return render(request, 'dashboard/home.html')


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def admin_home(request):
    students_qs = StudentProfile.objects.all()
    filtered = _filter_students(students_qs, request)

    total_students = students_qs.count()
    rent_count = students_qs.filter(housing_type='rent').count()
    dormitory_count = students_qs.filter(housing_type='dormitory').count()
    home_count = students_qs.filter(housing_type='home').count()
    debtors_count = students_qs.filter(housing_type='rent', rental__is_paid=False).count()
    paid_count = students_qs.filter(housing_type='rent', rental__is_paid=True).count()

    stats = {
        'total_students': total_students,
        'total_tutors': User.objects.filter(role='tutor').count(),
        'total_admins': User.objects.filter(Q(role='admin') | Q(is_superuser=True)).count(),
        'rent': rent_count,
        'dormitory': dormitory_count,
        'home': home_count,
        'debtors': debtors_count,
        'paid': paid_count,
        'faculties': Faculty.objects.count(),
        'groups': Group.objects.count(),
        'regions': Region.objects.count(),
        'total_rent_money': RentalInfo.objects.aggregate(s=Sum('monthly_price'))['s'] or 0,
        'collected_money': RentalInfo.objects.filter(is_paid=True).aggregate(s=Sum('monthly_price'))['s'] or 0,
    }

    region_stats = list(
        RentalInfo.objects.filter(region__isnull=False)
        .values('region__name')
        .annotate(count=Count('id'),
                  total_price=Sum('monthly_price'),
                  paid_count=Count('id', filter=Q(is_paid=True)),
                  debt_count=Count('id', filter=Q(is_paid=False)))
        .order_by('-count')
    )

    faculty_stats = list(
        StudentProfile.objects.filter(faculty__isnull=False)
        .values('faculty__name', 'faculty__short_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    course_stats = list(
        StudentProfile.objects.values('course')
        .annotate(count=Count('id'))
        .order_by('course')
    )

    chart_data = {
        'housing': {
            'labels': ['Ijarada', 'Yotoqxonada', "O'z uyida"],
            'data': [rent_count, dormitory_count, home_count],
            'colors': ['#d97706', '#0891b2', '#16a34a'],
        },
        'payment': {
            'labels': ["To'langan", 'Qarzdor'],
            'data': [paid_count, debtors_count],
            'colors': ['#16a34a', '#dc2626'],
        },
        'regions': {
            'labels': [r['region__name'] for r in region_stats[:8]],
            'data':   [r['count'] for r in region_stats[:8]],
        },
        'faculties': {
            'labels': [f['faculty__short_name'] or f['faculty__name'][:20] for f in faculty_stats],
            'data':   [f['count'] for f in faculty_stats],
        },
        'courses': {
            'labels': [f"{c['course']}-kurs" for c in course_stats],
            'data':   [c['count'] for c in course_stats],
        },
    }

    recent_students = (
        StudentProfile.objects.select_related('user', 'faculty', 'group')
        .order_by('-created_at')[:6]
    )
    debtors_list = (
        StudentProfile.objects.filter(housing_type='rent', rental__is_paid=False)
        .select_related('user', 'group', 'rental__region')[:8]
    )

    paginator = Paginator(filtered, 15)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/admin_home.html', {
        'stats': stats,
        'students': page,
        'total_filtered': filtered.count(),
        'region_stats': region_stats,
        'faculty_stats': faculty_stats,
        'chart_data_json': json.dumps(chart_data),
        'faculties': Faculty.objects.all(),
        'groups': Group.objects.all(),
        'regions': Region.objects.all(),
        'districts': District.objects.all(),
        'filters': request.GET,
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def export_students_csv(request):
    students = _filter_students(StudentProfile.objects.all(), request)
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="talabalar.csv"'
    response.write('﻿')  # BOM for Excel
    writer = csv.writer(response)
    writer.writerow(['#', 'F.I.Sh', 'Login', 'Telefon', 'Fakultet', 'Guruh', 'Kurs',
                     'Yashash turi', 'Hudud', 'Tuman', 'Manzil', 'Ijara narxi', "To'lov holati"])
    for i, s in enumerate(students, 1):
        rental = getattr(s, 'rental', None)
        writer.writerow([
            i, s.full_name, s.user.username, s.user.phone or '',
            s.faculty or '', s.group or '', s.course,
            s.get_housing_type_display(),
            (rental.region.name if rental and rental.region else (s.home_region.name if s.home_region else '')),
            (rental.district.name if rental and rental.district else (s.home_district.name if s.home_district else '')),
            rental.address if rental else '',
            rental.monthly_price if rental else '',
            ('Tolangan' if rental and rental.is_paid else 'Qarzdor') if rental else '-',
        ])
    return response


# ---- Foydalanuvchilarni boshqarish ----
@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def users_list(request):
    role = request.GET.get('role', '')
    q = request.GET.get('q', '')
    qs = User.objects.all().order_by('-date_joined')
    if role:
        qs = qs.filter(role=role)
    if q:
        qs = qs.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) |
            Q(last_name__icontains=q) | Q(phone__icontains=q)
        )
    return render(request, 'dashboard/users_list.html', {
        'users': qs,
        'filters': request.GET,
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'tutor':
                TutorProfile.objects.get_or_create(user=user)
            messages.success(request, "Foydalanuvchi yaratildi.")
            return redirect('dashboard:users_list')
    else:
        form = UserCreateForm()
    return render(request, 'dashboard/user_form.html', {
        'form': form,
        'title': "Yangi foydalanuvchi qo'shish",
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            if user.role == 'tutor':
                TutorProfile.objects.get_or_create(user=user)
            messages.success(request, "Foydalanuvchi yangilandi.")
            return redirect('dashboard:users_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'dashboard/user_form.html', {
        'form': form,
        'title': f"{user} - tahrirlash",
        'edit_user': user,
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Foydalanuvchi o'chirildi.")
        return redirect('dashboard:users_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'object': user,
        'title': f"{user} ni o'chirish",
        'cancel_url': 'dashboard:users_list',
    })


# ---- Tyutor biriktirish ----
@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def tutor_assign(request, pk):
    user = get_object_or_404(User, pk=pk, role='tutor')
    profile, _ = TutorProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        faculty_ids = request.POST.getlist('faculties')
        group_ids = request.POST.getlist('groups')
        profile.faculties.set(faculty_ids)
        profile.groups.set(group_ids)
        profile.note = request.POST.get('note', '')
        profile.save()
        messages.success(request, "Tyutor fakultet/guruhlarga biriktirildi.")
        return redirect('dashboard:users_list')
    return render(request, 'dashboard/tutor_assign.html', {
        'tutor_user': user,
        'profile': profile,
        'faculties': Faculty.objects.all(),
        'groups': Group.objects.all(),
    })


# ---- Faculty CRUD ----
@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def faculty_list(request):
    faculties = Faculty.objects.annotate(student_count=Count('students')).order_by('name')
    return render(request, 'dashboard/faculty_list.html', {'faculties': faculties})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def faculty_create(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fakultet yaratildi.")
            return redirect('dashboard:faculty_list')
    else:
        form = FacultyForm()
    return render(request, 'dashboard/simple_form.html', {
        'form': form, 'title': "Fakultet qo'shish", 'cancel_url': 'dashboard:faculty_list'
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def faculty_edit(request, pk):
    obj = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Fakultet yangilandi.")
            return redirect('dashboard:faculty_list')
    else:
        form = FacultyForm(instance=obj)
    return render(request, 'dashboard/simple_form.html', {
        'form': form, 'title': f"{obj} - tahrirlash", 'cancel_url': 'dashboard:faculty_list'
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def faculty_delete(request, pk):
    obj = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Fakultet o'chirildi.")
        return redirect('dashboard:faculty_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'object': obj, 'title': f"{obj} ni o'chirish", 'cancel_url': 'dashboard:faculty_list'
    })


# ---- Group CRUD ----
@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def group_list(request):
    groups = Group.objects.select_related('faculty').annotate(student_count=Count('students'))
    return render(request, 'dashboard/group_list.html', {'groups': groups})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Guruh yaratildi.")
            return redirect('dashboard:group_list')
    else:
        form = GroupForm()
    return render(request, 'dashboard/simple_form.html', {
        'form': form, 'title': "Guruh qo'shish", 'cancel_url': 'dashboard:group_list'
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def group_edit(request, pk):
    obj = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Guruh yangilandi.")
            return redirect('dashboard:group_list')
    else:
        form = GroupForm(instance=obj)
    return render(request, 'dashboard/simple_form.html', {
        'form': form, 'title': f"{obj} - tahrirlash", 'cancel_url': 'dashboard:group_list'
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def group_delete(request, pk):
    obj = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Guruh o'chirildi.")
        return redirect('dashboard:group_list')
    return render(request, 'dashboard/confirm_delete.html', {
        'object': obj, 'title': f"{obj} ni o'chirish", 'cancel_url': 'dashboard:group_list'
    })


# ---- Region CRUD ----
@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def region_list(request):
    regions = Region.objects.annotate(district_count=Count('districts')).order_by('name')
    return render(request, 'dashboard/region_list.html', {'regions': regions})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def region_create(request):
    if request.method == 'POST':
        form = RegionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hudud yaratildi.")
            return redirect('dashboard:region_list')
    else:
        form = RegionForm()
    return render(request, 'dashboard/simple_form.html', {
        'form': form, 'title': "Hudud qo'shish", 'cancel_url': 'dashboard:region_list'
    })


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def district_create(request):
    if request.method == 'POST':
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tuman yaratildi.")
            return redirect('dashboard:region_list')
    else:
        form = DistrictForm()
    return render(request, 'dashboard/simple_form.html', {
        'form': form, 'title': "Tuman qo'shish", 'cancel_url': 'dashboard:region_list'
    })
