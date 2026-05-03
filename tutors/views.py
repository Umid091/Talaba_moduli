from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.shortcuts import render, redirect, get_object_or_404

from students.models import StudentProfile, Faculty, Group, Region, District, RentalInfo
from .models import TutorProfile


def _get_or_create_tutor_profile(user):
    profile, _ = TutorProfile.objects.get_or_create(user=user)
    return profile


def _filter_students(qs, request):
    """Common filter logic used by tutor and admin views."""
    region_id = request.GET.get('region')
    district_id = request.GET.get('district')
    group_id = request.GET.get('group')
    faculty_id = request.GET.get('faculty')
    course = request.GET.get('course')
    housing = request.GET.get('housing')
    debt = request.GET.get('debt')
    q = request.GET.get('q')

    if faculty_id:
        qs = qs.filter(faculty_id=faculty_id)
    if group_id:
        qs = qs.filter(group_id=group_id)
    if course:
        qs = qs.filter(course=course)
    if housing:
        qs = qs.filter(housing_type=housing)

    if region_id:
        qs = qs.filter(
            Q(rental__region_id=region_id) | Q(home_region_id=region_id)
        )
    if district_id:
        qs = qs.filter(
            Q(rental__district_id=district_id) | Q(home_district_id=district_id)
        )

    if debt == 'yes':
        qs = qs.filter(housing_type='rent', rental__is_paid=False)
    elif debt == 'no':
        qs = qs.filter(
            Q(housing_type__in=['home', 'dormitory']) |
            Q(housing_type='rent', rental__is_paid=True)
        )

    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__phone__icontains=q)
        )

    return qs.select_related('user', 'faculty', 'group', 'home_region', 'rental__region')


@login_required
def tutor_dashboard(request):
    if not request.user.is_tutor_role:
        messages.warning(request, 'Bu sahifa faqat tyutorlar uchun.')
        return redirect('dashboard:home')

    tutor = _get_or_create_tutor_profile(request.user)
    students_qs = tutor.students_qs()

    filtered = _filter_students(students_qs, request)

    rent_count = students_qs.filter(housing_type='rent').count()
    dormitory_count = students_qs.filter(housing_type='dormitory').count()
    home_count = students_qs.filter(housing_type='home').count()
    debtors_count = students_qs.filter(housing_type='rent', rental__is_paid=False).count()

    stats = {
        'total': students_qs.count(),
        'rent': rent_count,
        'dormitory': dormitory_count,
        'home': home_count,
        'debtors': debtors_count,
        'paid': students_qs.filter(housing_type='rent', rental__is_paid=True).count(),
    }

    region_stats = list(
        students_qs.filter(rental__region__isnull=False)
        .values('rental__region__name')
        .annotate(count=Count('id'), total_price=Sum('rental__monthly_price'))
        .order_by('-count')
    )

    import json
    chart_data = {
        'housing': {
            'labels': ['Ijarada', 'Yotoqxonada', "O'z uyida"],
            'data': [rent_count, dormitory_count, home_count],
            'colors': ['#d97706', '#0891b2', '#16a34a'],
        },
        'regions': {
            'labels': [r['rental__region__name'] for r in region_stats[:6]],
            'data':   [r['count'] for r in region_stats[:6]],
        },
    }

    debtors = (
        students_qs.filter(housing_type='rent', rental__is_paid=False)
        .select_related('user', 'rental__region', 'group')[:6]
    )
    incomplete = (
        students_qs.filter(profile_completed=False)
        .select_related('user', 'group')[:6]
    )

    paginator = Paginator(filtered, 15)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'tutors/dashboard.html', {
        'tutor': tutor,
        'students': page,
        'total_filtered': filtered.count(),
        'stats': stats,
        'region_stats': region_stats,
        'debtors': debtors,
        'incomplete': incomplete,
        'chart_data_json': json.dumps(chart_data),
        'faculties': Faculty.objects.all(),
        'groups': Group.objects.all(),
        'regions': Region.objects.all(),
        'districts': District.objects.all(),
        'filters': request.GET,
    })


@login_required
def student_detail(request, pk):
    if not (request.user.is_tutor_role or request.user.is_admin_role):
        messages.warning(request, 'Ruxsat yo\'q.')
        return redirect('dashboard:home')

    student = get_object_or_404(StudentProfile, pk=pk)

    if request.user.is_tutor_role:
        tutor = _get_or_create_tutor_profile(request.user)
        if not tutor.students_qs().filter(pk=pk).exists():
            messages.warning(request, 'Ushbu talaba sizga biriktirilmagan.')
            return redirect('tutors:dashboard')

    rental = getattr(student, 'rental', None)
    return render(request, 'tutors/student_detail.html', {
        'student': student,
        'rental': rental,
    })
