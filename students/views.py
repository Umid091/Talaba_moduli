from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import StudentProfileForm, RentalInfoForm
from .models import StudentProfile, District


def districts_by_region(request):
    """AJAX: Hudud bo'yicha tumanlar ro'yxatini qaytaradi."""
    region_id = request.GET.get('region')
    qs = District.objects.filter(region_id=region_id) if region_id else District.objects.none()
    data = [{'id': d.id, 'name': d.name} for d in qs.order_by('name')]
    return JsonResponse({'districts': data})


def _get_or_create_student_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


@login_required
def student_dashboard(request):
    if not request.user.is_student_role:
        messages.warning(request, 'Bu sahifa faqat talabalar uchun.')
        return redirect('dashboard:home')

    profile = _get_or_create_student_profile(request.user)
    rental = getattr(profile, 'rental', None)

    return render(request, 'students/dashboard.html', {
        'profile': profile,
        'rental': rental,
    })


@login_required
def edit_profile(request):
    if not request.user.is_student_role:
        messages.warning(request, 'Bu amal faqat talabalar uchun.')
        return redirect('dashboard:home')

    profile = _get_or_create_student_profile(request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile_completed = True
            obj.save()
            messages.success(request, "Profil ma'lumotlari saqlandi.")
            if obj.is_renter:
                return redirect('students:rental_edit')
            return redirect('students:dashboard')
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'students/edit_profile.html', {'form': form, 'profile': profile})


@login_required
def edit_rental(request):
    if not request.user.is_student_role:
        messages.warning(request, 'Bu amal faqat talabalar uchun.')
        return redirect('dashboard:home')

    profile = _get_or_create_student_profile(request.user)

    if profile.housing_type != StudentProfile.HousingType.RENT:
        messages.info(request, "Ijara ma'lumotlari faqat ijarada yashovchi talabalar uchun kiritiladi.")
        return redirect('students:dashboard')

    rental = getattr(profile, 'rental', None)

    if request.method == 'POST':
        form = RentalInfoForm(request.POST, instance=rental)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = profile
            obj.save()
            messages.success(request, "Ijara ma'lumotlari saqlandi.")
            return redirect('students:dashboard')
    else:
        form = RentalInfoForm(instance=rental)

    return render(request, 'students/edit_rental.html', {'form': form, 'profile': profile})


@login_required
def toggle_payment(request):
    if not request.user.is_student_role:
        return redirect('dashboard:home')

    profile = _get_or_create_student_profile(request.user)
    rental = getattr(profile, 'rental', None)
    if not rental:
        messages.warning(request, "Avval ijara ma'lumotini kiriting.")
        return redirect('students:rental_edit')

    if request.method == 'POST':
        rental.is_paid = not rental.is_paid
        if rental.is_paid:
            rental.last_payment_date = timezone.now().date()
        rental.save()
        messages.success(request, "To'lov holati yangilandi.")

    return redirect('students:dashboard')
