from django import forms
from .models import StudentProfile, RentalInfo, Faculty, Group, Region, District


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = (
            'university', 'faculty', 'group', 'course',
            'housing_type', 'home_region', 'home_district',
            'birth_date', 'passport',
        )
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-input')


class RentalInfoForm(forms.ModelForm):
    class Meta:
        model = RentalInfo
        fields = (
            'region', 'district', 'address', 'monthly_price',
            'owner_full_name', 'owner_phone', 'owner_passport',
            'is_paid', 'last_payment_date', 'note',
        )
        widgets = {
            'last_payment_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_paid':
                field.widget.attrs.setdefault('class', 'form-check')
            else:
                field.widget.attrs.setdefault('class', 'form-input')


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ('name', 'short_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-input')


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('faculty', 'name', 'course')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-input')


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-input')


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ('region', 'name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-input')
