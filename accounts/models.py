from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        TUTOR = 'tutor', 'Tyutor'
        STUDENT = 'student', 'Talaba'

    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='Rol',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Rasm')

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        full = self.get_full_name().strip()
        return full or self.username

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_tutor_role(self):
        return self.role == self.Role.TUTOR

    @property
    def is_student_role(self):
        return self.role == self.Role.STUDENT

    def get_absolute_url(self):
        return reverse('dashboard:home')
