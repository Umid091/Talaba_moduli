from django.conf import settings
from django.db import models


class TutorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_profile',
        verbose_name='Foydalanuvchi',
    )
    faculties = models.ManyToManyField('students.Faculty', blank=True,
                                       related_name='tutors', verbose_name='Fakultetlar')
    groups = models.ManyToManyField('students.Group', blank=True,
                                    related_name='tutors', verbose_name='Guruhlar')
    note = models.TextField(blank=True, verbose_name='Izoh')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tyutor profili'
        verbose_name_plural = 'Tyutorlar profillari'

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def students_qs(self):
        from students.models import StudentProfile
        return StudentProfile.objects.filter(
            models.Q(group__in=self.groups.all()) |
            models.Q(faculty__in=self.faculties.all())
        ).distinct()
