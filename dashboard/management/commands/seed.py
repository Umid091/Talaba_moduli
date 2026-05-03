import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from students.models import (Region, District, Faculty, Group,
                             StudentProfile, RentalInfo)
from tutors.models import TutorProfile

User = get_user_model()

REGIONS = {
    'Toshkent shahri': ['Yunusobod', 'Mirzo Ulug\'bek', 'Chilonzor', 'Yashnobod', 'Olmazor'],
    'Toshkent viloyati': ['Bekobod', 'Chirchiq', 'Angren', 'Yangiyo\'l'],
    'Samarqand viloyati': ['Samarqand sh.', 'Urgut', 'Kattaqo\'rg\'on'],
    'Andijon viloyati': ['Andijon sh.', 'Asaka', 'Xonobod'],
    'Farg\'ona viloyati': ['Farg\'ona sh.', 'Marg\'ilon', 'Qo\'qon'],
    'Buxoro viloyati': ['Buxoro sh.', 'G\'ijduvon', 'Kogon'],
    'Qashqadaryo viloyati': ['Qarshi', 'Shahrisabz', 'G\'uzor'],
    'Surxondaryo viloyati': ['Termiz', 'Denov', 'Sho\'rchi'],
    'Xorazm viloyati': ['Urganch', 'Xiva', 'Bog\'ot'],
    'Namangan viloyati': ['Namangan sh.', 'Chust', 'Pop'],
    'Navoiy viloyati': ['Navoiy sh.', 'Zarafshon', 'Karmana'],
    'Sirdaryo viloyati': ['Guliston', 'Yangiyer', 'Sirdaryo sh.'],
    'Jizzax viloyati': ['Jizzax sh.', 'Pakhtakor', 'Zomin'],
    'Qoraqalpog\'iston Resp.': ['Nukus', 'Beruniy', 'Mo\'ynoq'],
}

FACULTIES = [
    ('Axborot texnologiyalari fakulteti', 'AT'),
    ('Iqtisodiyot fakulteti', 'IQT'),
    ('Filologiya fakulteti', 'FIL'),
    ('Tarix fakulteti', 'TAR'),
    ('Fizika-matematika fakulteti', 'FM'),
    ('Pedagogika fakulteti', 'PED'),
]

UZBEK_NAMES = [
    ('Akbar', 'Karimov'), ('Bobur', 'Tursunov'), ('Davron', 'Yusupov'),
    ('Eldor', 'Saidov'), ('Farhod', 'Nazarov'), ('Gulnora', 'Rashidova'),
    ('Hilola', 'Olimova'), ('Iroda', 'Sharipova'), ('Jasur', 'Mamatkulov'),
    ('Komron', 'Erkinov'), ('Lola', 'Yo\'ldosheva'), ('Madina', 'Tojiboyeva'),
    ('Nilufar', 'Qodirova'), ('Otabek', 'Soliyev'), ('Po\'lat', 'Hamidov'),
    ('Quvonch', 'Rustamov'), ('Rustam', 'G\'aniev'), ('Sabina', 'Toshmatova'),
    ('Tohir', 'Abdullayev'), ('Umid', 'Boboyev'), ('Vali', 'Nurullayev'),
    ('Xushnud', 'Ergashev'), ('Yulduz', 'Saliyeva'), ('Zarina', 'Rahmonova'),
    ('Aziz', 'Holmatov'), ('Bekzod', 'Sodiqov'), ('Diyora', 'Aliyeva'),
    ('Erkin', 'Otaboev'), ('Feruza', 'Yusupova'), ('Sherzod', 'Komilov'),
]


class Command(BaseCommand):
    help = "Demo ma'lumotlarni yaratadi: admin, tyutorlar, talabalar, fakultetlar, hududlar"

    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=40)
        parser.add_argument('--tutors', type=int, default=4)

    def handle(self, *args, **opts):
        self.stdout.write(self.style.NOTICE('🌱 Demo ma\'lumotlar tayyorlanmoqda...'))

        # Hududlar va tumanlar
        for region_name, districts in REGIONS.items():
            region, _ = Region.objects.get_or_create(name=region_name)
            for d in districts:
                District.objects.get_or_create(region=region, name=d)

        # Fakultetlar
        for name, short in FACULTIES:
            Faculty.objects.get_or_create(name=name, defaults={'short_name': short})

        # Guruhlar
        for fac in Faculty.objects.all():
            for course in range(1, 5):
                for letter in ['A', 'B']:
                    Group.objects.get_or_create(
                        faculty=fac,
                        name=f'{fac.short_name}-{course}{letter}',
                        defaults={'course': course},
                    )

        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', password='admin123',
                email='admin@university.uz', first_name='Tizim', last_name='Administratori',
                role='admin', phone='+998901234567',
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Admin yaratildi: admin / admin123'))

        # Tyutorlar
        all_faculties = list(Faculty.objects.all())
        all_groups = list(Group.objects.all())

        for i in range(opts['tutors']):
            uname = f'tutor{i+1}'
            if User.objects.filter(username=uname).exists():
                continue
            first, last = random.choice(UZBEK_NAMES)
            user = User.objects.create_user(
                username=uname, password='tutor123',
                first_name=first, last_name=last,
                email=f'{uname}@university.uz',
                phone=f'+99890{random.randint(1000000, 9999999)}',
                role='tutor',
            )
            tprofile, _ = TutorProfile.objects.get_or_create(user=user)
            assigned_faculty = all_faculties[i % len(all_faculties)]
            tprofile.faculties.add(assigned_faculty)
            tprofile.groups.add(*assigned_faculty.groups.all()[:4])

        self.stdout.write(self.style.SUCCESS(f'✓ {opts["tutors"]} ta tyutor yaratildi (parol: tutor123)'))

        # Talabalar
        all_regions = list(Region.objects.all())
        all_districts = list(District.objects.all())

        existing_count = User.objects.filter(role='student').count()
        target = opts['students']
        to_create = max(0, target - existing_count)

        housing_choices = ['rent', 'rent', 'rent', 'dormitory', 'home', 'home']

        for i in range(to_create):
            uname = f'student{existing_count + i + 1}'
            first, last = random.choice(UZBEK_NAMES)
            faculty = random.choice(all_faculties)
            group = random.choice(list(faculty.groups.all()))
            region = random.choice(all_regions)
            district = random.choice([d for d in all_districts if d.region_id == region.id])

            user = User.objects.create_user(
                username=uname, password='student123',
                first_name=first, last_name=last,
                email=f'{uname}@stud.uz',
                phone=f'+99891{random.randint(1000000, 9999999)}',
                role='student',
            )
            # Profile auto-created by signal — update it
            profile = StudentProfile.objects.get(user=user)
            profile.faculty = faculty
            profile.group = group
            profile.course = group.course
            profile.home_region = region
            profile.home_district = district
            profile.birth_date = date(2003, random.randint(1, 12), random.randint(1, 28))
            profile.passport = f'AA{random.randint(1000000, 9999999)}'
            profile.housing_type = random.choice(housing_choices)
            profile.profile_completed = True
            profile.save()

            if profile.housing_type == 'rent':
                rent_region = random.choice(all_regions)
                rent_district = random.choice([d for d in all_districts if d.region_id == rent_region.id])
                RentalInfo.objects.create(
                    student=profile,
                    region=rent_region,
                    district=rent_district,
                    address=f'{rent_district.name}, {random.choice(["Mustaqillik", "Amir Temur", "Bobur", "Navoiy"])} ko\'chasi, {random.randint(1, 100)}-uy',
                    monthly_price=Decimal(random.choice([1500000, 2000000, 2500000, 3000000, 3500000])),
                    owner_full_name=f'{random.choice(UZBEK_NAMES)[1]} {random.choice(UZBEK_NAMES)[0]}',
                    owner_phone=f'+99893{random.randint(1000000, 9999999)}',
                    owner_passport=f'AB{random.randint(1000000, 9999999)}',
                    is_paid=random.choice([True, False, True]),
                    last_payment_date=date.today() - timedelta(days=random.randint(0, 60)),
                )

        self.stdout.write(self.style.SUCCESS(f'✓ {to_create} ta yangi talaba yaratildi (parol: student123)'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Tayyor! Demo akkauntlar:'))
        self.stdout.write('   👑 Admin:   admin / admin123')
        self.stdout.write('   🎓 Tyutor:  tutor1 / tutor123')
        self.stdout.write('   👤 Talaba:  student1 / student123')
