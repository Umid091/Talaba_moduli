from django.conf import settings
from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name='Hudud nomi')

    class Meta:
        verbose_name = 'Hudud'
        verbose_name_plural = 'Hududlar'
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts', verbose_name='Hudud')
    name = models.CharField(max_length=120, verbose_name='Tuman nomi')

    class Meta:
        verbose_name = 'Tuman'
        verbose_name_plural = 'Tumanlar'
        unique_together = ('region', 'name')
        ordering = ['region__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.region.name})'


class Faculty(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Fakultet nomi')
    short_name = models.CharField(max_length=20, blank=True, verbose_name='Qisqa nomi')

    class Meta:
        verbose_name = 'Fakultet'
        verbose_name_plural = 'Fakultetlar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Group(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='groups', verbose_name='Fakultet')
    name = models.CharField(max_length=50, verbose_name='Guruh nomi')
    course = models.PositiveSmallIntegerField(verbose_name='Kurs', default=1)

    class Meta:
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'
        unique_together = ('faculty', 'name')
        ordering = ['faculty__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.faculty.short_name or self.faculty.name})'


class StudentProfile(models.Model):
    class HousingType(models.TextChoices):
        RENT = 'rent', 'Ijarada'
        DORMITORY = 'dormitory', 'Yotoqxonada'
        HOME = 'home', "O'z uyida"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Foydalanuvchi',
    )
    university = models.CharField(max_length=200, verbose_name="Oliy ta'lim muassasasi",
                                  default='Toshkent davlat universiteti')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='students', verbose_name='Fakultet')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='students', verbose_name='Guruh')
    course = models.PositiveSmallIntegerField(default=1, verbose_name='Kurs')

    housing_type = models.CharField(
        max_length=16,
        choices=HousingType.choices,
        default=HousingType.HOME,
        verbose_name='Yashash turi',
    )

    home_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='home_students', verbose_name="Tug'ilgan hudud")
    home_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='home_students', verbose_name="Tug'ilgan tuman")

    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")
    passport = models.CharField(max_length=20, blank=True, verbose_name='Pasport seriyasi')

    profile_completed = models.BooleanField(default=False, verbose_name="Profil to'ldirilgan")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Talaba profili'
        verbose_name_plural = 'Talabalar profillari'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.get_housing_type_display()}'

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_renter(self):
        return self.housing_type == self.HousingType.RENT

    @property
    def has_debt(self):
        if not self.is_renter:
            return False
        rental = getattr(self, 'rental', None)
        if not rental:
            return False
        return not rental.is_paid

    @property
    def completion_percent(self):
        """Profil to'ldirilganlik foizi (0-100)."""
        fields = [
            self.user.first_name, self.user.last_name, self.user.phone,
            self.faculty_id, self.group_id, self.course,
            self.home_region_id, self.home_district_id, self.birth_date, self.passport,
        ]
        filled = sum(1 for f in fields if f)
        total = len(fields)
        if self.is_renter:
            rental = getattr(self, 'rental', None)
            total += 4
            if rental:
                rental_fields = [rental.address, rental.monthly_price, rental.owner_full_name, rental.owner_phone]
                filled += sum(1 for f in rental_fields if f)
        if total == 0:
            return 0
        return int(filled * 100 / total)


class RentalInfo(models.Model):
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='rental',
        verbose_name='Talaba',
    )
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='rentals', verbose_name='Hudud')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='rentals', verbose_name='Tuman')
    address = models.CharField(max_length=255, verbose_name='Manzil')

    monthly_price = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                        verbose_name="Oylik ijara narxi (so'm)")

    owner_full_name = models.CharField(max_length=120, verbose_name='Uy egasining F.I.Sh')
    owner_phone = models.CharField(max_length=20, verbose_name='Uy egasi telefoni')
    owner_passport = models.CharField(max_length=20, blank=True, verbose_name='Uy egasi pasporti')

    is_paid = models.BooleanField(default=False, verbose_name="To'lov qilingan")
    last_payment_date = models.DateField(null=True, blank=True, verbose_name="Oxirgi to'lov sanasi")
    note = models.TextField(blank=True, verbose_name='Izoh')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ijara ma'lumoti"
        verbose_name_plural = "Ijara ma'lumotlari"

    def __str__(self):
        return f'{self.student.full_name} - {self.address}'
