# 📚 Talaba Moduli

Oliy ta'lim muassasasi talabalarining shaxsiy, o'quv va yashashga oid ma'lumotlarini yagona platformada boshqaruvchi web-tizim.

**Backend:** Django 6 · **Frontend:** HTML + CSS (custom, oliy ta'lim — navy/gold uslubi) · **Charts:** Chart.js · **DB:** SQLite

---

## ✨ Imkoniyatlar

### 👤 Talaba moduli
- 📋 **Profilni to'ldirish** — F.I.Sh, telefon, email, fakultet, kurs, guruh, pasport, tug'ilgan sana/hudud
- 🏠 **Yashash turini tanlash:** Ijarada / Yotoqxonada / O'z uyida
- 🏘️ **Ijarada bo'lsa:** manzil, hudud, tuman, oylik narx, uy egasi (F.I.Sh, telefon, pasport)
- ✏️ Ma'lumotlarni istalgan vaqtda **tahrirlash**
- 💰 Ijara to'lovi holatini o'zi belgilash (qarzdor / to'langan)
- 📊 **Profil to'liqligi foizi** (progress bar — 90%+ yashil, 60-89% sariq, <60% qizil)
- 🔑 Parolni o'zgartirish

### 🎓 Tyutor moduli
- 👥 Login orqali **faqat o'ziga biriktirilgan talabalar** ko'rinadi
- 🔍 **Filtrlash:** hudud, tuman, fakultet, guruh, kurs, yashash turi, moliyaviy holat
- 🔎 Qidiruv (ism/familiya/login/telefon)
- 📈 **Interaktiv chartlar:** yashash turi taqsimoti, hududlar bo'yicha bar-chart
- ⚠️ **"Diqqat talab qiluvchi" panel:** qarzdor talabalar va profili to'liq emaslar (top-6)
- 📍 Hududlar bo'yicha statistika (talabalar soni, umumiy ijara summasi)
- 📞 Talabaga qo'ng'iroq/email uchun klik-aloqa
- 🖨️ Talaba kartasini chop etish

### 👑 Administrator moduli
- 🛠 Django admin paneli + maxsus boshqaruv paneli
- 👥 **Foydalanuvchilar CRUD** (qo'shish/tahrirlash/o'chirish, rol berish)
- 🎯 **Tyutorlarni fakultet/guruhlarga biriktirish** (multi-select)
- 🏛 Fakultet, guruh, hudud, tuman CRUD
- 📊 **Boy statistika va 5 ta interaktiv chart:**
  - Hududlar bo'yicha gorizontal bar (Top-8)
  - Yashash turi (doughnut + foiz tooltip)
  - Fakultetlar (bar)
  - Kurslar (doughnut)
  - To'lov holati (pie)
- 💰 Moliyaviy ko'rsatkichlar: jami ijara summasi, to'plangan summa, qarzdorlar
- 🕒 So'nggi qo'shilgan talabalar widget
- 🚨 Qarzdor talabalar widget (top-8)
- 📥 **CSV eksport** — filterlangan talabalarni Excel uchun yuklab olish
- 🔍 Kengaytirilgan filterlash (admin)

---

## 🚀 Ishga tushirish

### 1. Virtual muhitni faollashtiring
```powershell
cd C:\Users\GF63\Desktop\talaba_modul
.\venv\Scripts\activate
```

### 2. Windowsda emoji chiqishi uchun (bir martalik)
```powershell
$env:PYTHONIOENCODING="utf-8"
```

### 3. Migratsiyalar (faqat birinchi marta)
```powershell
python manage.py migrate
```

### 4. Demo ma'lumotlarni yaratish
```powershell
python manage.py seed --students 40 --tutors 4
```

### 5. Serverni ishga tushirish
```powershell
python manage.py runserver
```

Brauzerda oching: **http://127.0.0.1:8000/**

---

## 🔑 Demo akkauntlar

| Rol | Login | Parol |
|------|------|------|
| 👑 Administrator | `admin` | `admin123` |
| 🎓 Tyutor (1–4) | `tutor1`, `tutor2`, ... | `tutor123` |
| 👤 Talaba (1–40) | `student1`, `student2`, ... | `student123` |

---

## 📁 Loyiha tuzilmasi

```
talaba_modul/
├── config/                    # Django asosiy sozlamalar
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  # Custom User (admin/tutor/student rollari)
│   ├── models.py              # User (AbstractUser + role + phone + avatar)
│   ├── forms.py               # Login, profile, user create/edit
│   ├── views.py               # login, logout, profile, password_change
│   └── urls.py
├── students/                  # Talabalar moduli
│   ├── models.py              # StudentProfile, RentalInfo, Faculty,
│   │                          # Group, Region, District
│   ├── forms.py
│   ├── views.py               # dashboard, edit_profile, edit_rental,
│   │                          # toggle_payment, districts_by_region (AJAX)
│   ├── signals.py             # auto-create StudentProfile
│   └── urls.py
├── tutors/                    # Tyutor moduli
│   ├── models.py              # TutorProfile + students_qs()
│   ├── views.py               # tutor_dashboard, student_detail
│   └── urls.py
├── dashboard/                 # Admin paneli + statistika
│   ├── views.py               # admin_home (chartlar), users CRUD,
│   │                          # faculty/group/region CRUD, export_students_csv
│   ├── urls.py
│   ├── context_processors.py  # role flags (role_admin, role_tutor, role_student)
│   └── management/commands/seed.py
├── templates/
│   ├── base.html              # Sidebar + topbar + breadcrumb layout
│   ├── 404.html, 403.html, 500.html  # Custom error sahifalari
│   ├── accounts/              # login.html (HEMIS-style),
│   │                          # profile.html, password_change.html
│   ├── students/              # dashboard.html (progress bar),
│   │                          # edit_profile.html, edit_rental.html
│   ├── tutors/                # dashboard.html (chartlar+widgetlar),
│   │                          # student_detail.html, _filter_bar.html,
│   │                          # _students_table.html
│   └── dashboard/             # admin_home (chart+widget), users_list,
│                              # user_form, faculty_list, group_list,
│                              # region_list, tutor_assign, simple_form,
│                              # confirm_delete
├── static/
│   ├── css/styles.css         # Universitet uslubi (navy + gold)
│   └── js/app.js              # Mobile sidebar, AJAX dropdowns, alerts
├── manage.py
└── db.sqlite3
```

---

## 🗄️ Ma'lumotlar bazasi modellari

| Model | Asosiy maydonlar |
|-------|------------------|
| **User** | `username`, `role` (admin/tutor/student), `phone`, `avatar` |
| **StudentProfile** | `user`, `university`, `faculty`, `group`, `course`, `housing_type`, `home_region`, `home_district`, `birth_date`, `passport`, `profile_completed` |
| **RentalInfo** | `student`, `region`, `district`, `address`, `monthly_price`, `owner_full_name`, `owner_phone`, `is_paid`, `last_payment_date`, `note` |
| **TutorProfile** | `user`, `faculties` (M2M), `groups` (M2M), `note` |
| **Faculty** | `name`, `short_name` |
| **Group** | `faculty`, `name`, `course` |
| **Region / District** | `name`, (district → region FK) |

### Hisoblanadigan property'lar
- `StudentProfile.completion_percent` — profil to'ldirilganlik foizi (0-100)
- `StudentProfile.has_debt` — qarzdor yoki yo'qligini tekshirish
- `StudentProfile.is_renter` — ijarada yashash holati
- `User.is_admin_role / is_tutor_role / is_student_role` — rol tekshiruvi

---

## 🌐 URL marshrutlari

### Auth (accounts)
| URL | Sahifa |
|-----|--------|
| `/accounts/login/` | Kirish (HEMIS-style) |
| `/accounts/logout/` | Chiqish |
| `/accounts/profile/` | Mening hisobim (avatar, ma'lumot tahrirlash) |
| `/accounts/password/` | Parolni o'zgartirish |

### Talaba sahifalari
| URL | Sahifa |
|-----|--------|
| `/` | Rolga qarab redirect |
| `/students/` | Talaba dashboard (profile + progress bar) |
| `/students/profile/edit/` | Profilni tahrirlash |
| `/students/rental/edit/` | Ijara ma'lumotlari |
| `/students/rental/toggle-payment/` | To'lov holatini almashtirish (POST) |
| `/students/api/districts/?region=N` | AJAX: hudud bo'yicha tumanlar |

### Tyutor sahifalari
| URL | Sahifa |
|-----|--------|
| `/tutors/` | Tyutor dashboard (chartlar + widgetlar) |
| `/tutors/students/<id>/` | Talaba to'liq profili |

### Admin / boshqaruv
| URL | Sahifa |
|-----|--------|
| `/admin-panel/` | Admin statistika (5 chart + 3 widget) |
| `/users/` | Foydalanuvchilar ro'yxati |
| `/users/create/` | Yangi foydalanuvchi |
| `/users/<id>/edit/` | Tahrirlash |
| `/users/<id>/delete/` | O'chirish |
| `/users/<id>/assign/` | Tyutorni biriktirish |
| `/faculties/`, `/groups/`, `/regions/` | CRUD ro'yxatlari |
| `/export/students.csv` | CSV eksport |
| `/admin/` | Django built-in admin |

---

## 📊 Charts (Chart.js)

Admin paneli quyidagi 5 ta interaktiv chartni ko'rsatadi:

1. **Hududlar bo'yicha (top 8)** — gorizontal bar
2. **Yashash turi taqsimoti** — doughnut (foiz tooltip bilan)
3. **Fakultetlar bo'yicha** — vertical bar
4. **Kurslar bo'yicha** — doughnut
5. **To'lov holati** — pie

Tyutor paneli — 2 ta chart (yashash turi + hududlar).

**Tooltip'lar** har bir hover'da ko'rsatadi: son + foiz (masalan "Ijarada: 22 ta (55%)").

---

## 🎨 UI/UX xususiyatlari

- 🎨 **Universitet uslubi** — navy (#0a1f44) + oltin (#d4a017) palitra, light theme
- 🔤 **Inter font** — zamonaviy, o'qish oson
- 📱 **Mobile responsive** — sidebar toggle (☰) tugmasi 1024px dan kichikda
- 🌐 **HEMIS uslubidagi login** — split-card, muassasa muhri (TM seal), ikonkali input maydonlar
- 📍 **Breadcrumb navigatsiya** — har bir sahifada
- 📋 **Profil to'liqligi progress bar** — 3 ranglar (yashil/sariq/qizil)
- 🔄 **Cascading dropdowns** — Hudud tanlansa, faqat o'sha hududning tumanlari avtomatik yuklanadi (AJAX)
- ⚡ **Auto-dismiss alerts** — 5 sekundda yopiladi (× tugmasi bilan ham)
- 🖼 **Avatar bilan jadvallar** — har bir foydalanuvchi/talaba uchun
- 📑 **Sahifalash (pagination)** — 15 talabadan ortiq bo'lsa
- 🚨 **Custom 404 / 403 / 500** sahifalari
- 🖨 **Print stylesheet** — talaba ma'lumotlarini chop etish

---

## 🆕 So'nggi qo'shilgan funksiyalar (v1.1)

- ✅ Profil to'liqligi foizi (progress bar)
- ✅ Cascading region → district dropdowns (AJAX)
- ✅ Mobile sidebar toggle button
- ✅ Tyutor "Diqqat" panel (qarzdorlar + profili to'liq emaslar)
- ✅ Admin "So'nggi qo'shilganlar" + "Qarzdorlar" widgetlari
- ✅ CSV eksport (filterlanga talabalar)
- ✅ Custom 404/403/500 error sahifalari
- ✅ Parolni o'zgartirish sahifasi
- ✅ Chart tooltip'lari (% va son)
- ✅ HEMIS-uslubidagi yangi login sahifasi
- ✅ Auto-dismiss alert'lar
- ✅ Print uchun CSS

---

## 🛠 Texnologiyalar

| Texnologiya | Versiya | Maqsad |
|-------------|---------|--------|
| **Python** | 3.13 | Til |
| **Django** | 6.0 | Backend framework |
| **SQLite** | bundled | DB (production'da PostgreSQL'ga o'tish mumkin) |
| **Pillow** | latest | Avatar/rasmlar uchun |
| **django-widget-tweaks** | 1.5 | Formalarga CSS qo'shish |
| **Chart.js** | 4.4.0 | CDN orqali, interaktiv chartlar |
| **Inter font** | Google Fonts | Tipografiya |

---

## 🛠 Ishlab chiqish bo'yicha eslatmalar

- Custom User: `accounts.User` (`AUTH_USER_MODEL` settings.py'da)
- Til: O'zbek (uz), vaqt zonasi: Asia/Tashkent
- Statika `runserver` orqali xizmat qilinadi (development)
- Yangi talaba ro'yxatdan o'tganda `StudentProfile` signal orqali avtomatik yaratiladi
- Chart'lar **CDN'dan** yuklab olinadi (internet ulanish kerak)
- Admin panel uchun decorator: `@login_required` + `@user_passes_test(_is_admin)`
- AJAX endpoint javob formati: `{"districts": [{"id": N, "name": "..."}]}`

---

## 🔧 Foydali komandalar

```powershell
# Bazani tozalash va qaytadan tiklash
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed --students 40 --tutors 4

# Yangi superuser yaratish
python manage.py createsuperuser

# Statik fayllarni yig'ish (production)
python manage.py collectstatic

# Tizim tekshiruvi
python manage.py check

# Migrationlarni ko'rish
python manage.py showmigrations
```

---

## 📂 Asosiy fayllar haqida

| Fayl | Tavsifi |
|------|---------|
| [config/settings.py](config/settings.py) | Django sozlamalari, `INSTALLED_APPS`, `AUTH_USER_MODEL` |
| [accounts/models.py](accounts/models.py) | Custom User modeli |
| [students/models.py](students/models.py) | StudentProfile, RentalInfo, Faculty, Group, Region, District |
| [tutors/models.py](tutors/models.py) | TutorProfile + `students_qs()` helper |
| [tutors/views.py](tutors/views.py) | Filterlash logikasi (`_filter_students`) |
| [dashboard/views.py](dashboard/views.py) | Admin home (statistika), CRUD'lar, CSV eksport |
| [dashboard/management/commands/seed.py](dashboard/management/commands/seed.py) | Demo ma'lumotlarni yaratuvchi komanda |
| [static/css/styles.css](static/css/styles.css) | Universitet uslubidagi UI |
| [static/js/app.js](static/js/app.js) | Mobile sidebar, cascading dropdowns, alerts |
| [templates/base.html](templates/base.html) | Sidebar + topbar layout |
| [templates/accounts/login.html](templates/accounts/login.html) | HEMIS-style login |

---

## 🧪 Test qilingan funksiyalar

| Funksiya | Status |
|----------|--------|
| 3 rol uchun login (admin/tutor/student) | ✅ |
| Admin: 5 chart, 3 widget, CSV eksport | ✅ |
| Tutor: filtrlash, "Diqqat" panel, sahifalash | ✅ |
| Student: profil progress, ijara CRUD, to'lov belgilash | ✅ |
| Cascading dropdowns (Region → District) | ✅ |
| Mobile sidebar toggle | ✅ |
| Auto-dismiss alerts | ✅ |
| Custom 404 sahifa | ✅ |
| Password change flow | ✅ |
| CRUD (Faculty/Group/Region/District/User) | ✅ |

---

## 📌 Demo'ni qaytadan tiklash

```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py seed --students 40 --tutors 4
```

---

## 📝 Litsenziya va muallif

✏️ **Muallif:** Latifbek Bahronov
🎓 Oliy ta'lim muassasalari uchun ishlab chiqilgan
📅 © {YEAR} Talaba Moduli — barcha huquqlar himoyalangan
