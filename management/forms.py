import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Member, Event, Announcement, BloodRequest

class MemberRegistrationForm(UserCreationForm):
    """
    Form for registering a new user (Member).
    Initial role defaults to PENDING.
    """
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="You must be at least 18 years old to register."
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        help_text="Enter a 10 or 12 digit phone number."
    )
    blood_group = forms.ChoiceField(
        choices=Member.BLOOD_GROUPS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    gender = forms.ChoiceField(
        choices=Member.GENDERS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = Member
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'phone_number', 'gender', 'date_of_birth', 'blood_group'
        )

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.date.today()
            age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
            if age < 18:
                raise ValidationError("You must be 18 years of age or older to register.")
        return dob

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Strip any non-digit chars
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) not in [10, 12]:
                raise ValidationError("Phone number must be exactly 10 or 12 digits.")
            return digits
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PENDING'
        user.is_active = False  # Keep inactive until approved by Executive
        if commit:
            user.save()
        return user


class MemberProfileForm(forms.ModelForm):
    """
    Form for members to update their profile and donor details.
    """
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'date_of_birth', 'blood_group', 'is_active_donor', 'last_donation_date', 'total_donations', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'is_active_donor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_donations': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) not in [10, 12]:
                raise ValidationError("Phone number must be exactly 10 or 12 digits.")
            return digits
        return phone

    def clean_last_donation_date(self):
        last_donation = self.cleaned_data.get('last_donation_date')
        if last_donation:
            if last_donation > datetime.date.today():
                raise ValidationError("Last donation date cannot be in the future.")
        return last_donation


class MemberAdminUpdateForm(forms.ModelForm):
    """
    Form for Executive Committee to edit all member fields including roles and approval status.
    """
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'blood_group', 'date_of_birth', 'is_active_donor', 'last_donation_date', 'total_donations', 'role', 'is_active', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active_donor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_donations': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class EventForm(forms.ModelForm):
    """
    Form for creating/scheduling and modifying events.
    """
    class Meta:
        model = Event
        fields = ['title', 'description', 'date_and_time', 'location', 'coordinator', 'is_public', 'poster']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'coordinator': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'poster': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AnnouncementForm(forms.ModelForm):
    """
    Form for creating and editing notices.
    """
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BloodRequestForm(forms.ModelForm):
    """
    Form to request emergency blood donation.
    """
    class Meta:
        model = BloodRequest
        fields = ['patient_name', 'blood_group', 'hospital', 'contact_number', 'needed_by', 'details']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'hospital': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'needed_by': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_needed_by(self):
        needed_by = self.cleaned_data.get('needed_by')
        if needed_by and needed_by < datetime.date.today():
            raise ValidationError("The requested date cannot be in the past.")
        return needed_by

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if contact:
            digits = ''.join(c for c in contact if c.isdigit())
            if len(digits) not in [10, 12]:
                raise ValidationError("Contact phone number must be exactly 10 or 12 digits.")
            return digits
        return contact


from .models import BloodDonor

class BloodDonorForm(forms.ModelForm):
    """
    Form for Executive Committee to add and update external/direct blood donors.
    """
    class Meta:
        model = BloodDonor
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'blood_group', 'date_of_birth', 'last_donation_date', 'total_donations', 'is_active_donor']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_donations': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active_donor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_birth'].required = True

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) not in [10, 12]:
                raise ValidationError("Phone number must be exactly 10 or 12 digits.")
            return digits
        return phone

