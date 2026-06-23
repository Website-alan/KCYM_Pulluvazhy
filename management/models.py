import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# Validator for 10 or 12 digit phone numbers
phone_validator = RegexValidator(
    regex=r'^\d{10}$|^\d{12}$',
    message="Phone number must be exactly 10 or 12 digits long."
)

# Validator for media upload size
def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5MB limit
    if value.size > limit:
        raise ValidationError('File size too large. Size should not exceed 5 MB.')

class Member(AbstractUser):
    """
    Custom user model representing KCYM Pulluvazhy members.
    Includes role-based access control and blood donor fields.
    """
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    ROLES = [
        ('VICAR', 'Vicar'),
        ('ASSISTANT_VICAR', 'Assistant Vicar'),
        ('EXECUTIVE', 'Executive Committee'),
        ('MEMBER', 'General Member'),
        ('PENDING', 'Pending Approval'),
    ]

    GENDERS = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    phone_number = models.CharField(
        max_length=15, 
        unique=True, 
        validators=[phone_validator],
        help_text="Enter a 10 or 12-digit mobile number."
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDERS,
        null=True,
        blank=True,
        help_text="Select gender."
    )
    date_of_birth = models.DateField(
        help_text="Must be 18 years or older to register."
    )
    join_date = models.DateField(
        default=datetime.date.today,
        help_text="The date the member joined KCYM."
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUPS,
        help_text="Select blood group."
    )
    is_active_donor = models.BooleanField(
        default=True,
        help_text="Designate if this member is currently active and available to donate blood."
    )
    last_donation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last blood donation."
    )
    total_donations = models.PositiveIntegerField(
        default=0,
        blank=True,
        help_text="Total number of times this member has donated blood."
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_file_size
        ],
        help_text="Upload an optional profile photo (Max 5MB)."
    )
    role = models.CharField(
        max_length=15,
        choices=ROLES,
        default='PENDING',
        help_text="Role-based permissions level."
    )

    def clean(self):
        super().clean()
        # Validate age is 18 or above
        if self.date_of_birth:
            today = datetime.date.today()
            age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if age < 18:
                raise ValidationError({"date_of_birth": "You must be 18 years of age or older to register."})

    def is_executive(self):
        if self.role in ['EXECUTIVE', 'VICAR', 'ASSISTANT_VICAR'] or self.is_superuser:
            return True
        return self.committee_positions.filter(committee__is_active=True).exists()

    def is_general_member(self):
        return self.role == 'MEMBER'

    def current_position(self):
        """
        Returns the active committee position held by this member, if any.
        """
        active_pos = self.committee_positions.filter(committee__is_active=True).first()
        return active_pos.get_position_display() if active_pos else None

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Event(models.Model):
    """
    Events tracker model.
    Ordered reverse-chronologically by date_and_time.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_and_time = models.DateTimeField()
    location = models.CharField(
        max_length=255, 
        default="St. Thomas Church, Pulluvazhy"
    )
    coordinator = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coordinated_events",
        help_text="Member coordinating this event."
    )
    is_public = models.BooleanField(
        default=True,
        help_text="If checked, this event will be visible to non-members/public."
    )
    poster = models.ImageField(
        upload_to='event_posters/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_file_size
        ],
        help_text="Upload an optional event poster/image (Max 5MB, JPG/PNG)."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_and_time', '-id']

    def __str__(self):
        return self.title


class EventRSVP(models.Model):
    """
    Tracks responses of members for specific events.
    """
    STATUS_CHOICES = [
        ('GOING', 'Going'),
        ('MAYBE', 'Maybe'),
        ('NOT_GOING', 'Not Going'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="rsvps"
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="event_rsvps"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='GOING'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'member')

    def __str__(self):
        return f"{self.member.username} - {self.event.title} - {self.status}"


class Announcement(models.Model):
    """
    Model for notices, pins, and updates.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pinned announcements appear at the top of the feed."
    )

    class Meta:
        ordering = ['-is_pinned', '-date_posted']

    def __str__(self):
        return self.title


class BloodRequest(models.Model):
    """
    Model for reporting emergency blood needs.
    """
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(
        max_length=3,
        choices=Member.BLOOD_GROUPS
    )
    hospital = models.CharField(max_length=255)
    contact_number = models.CharField(
        max_length=15,
        validators=[phone_validator]
    )
    needed_by = models.DateField()
    details = models.TextField(
        blank=True,
        help_text="Any additional details, e.g. case number, unit count."
    )
    is_fulfilled = models.BooleanField(
        default=False,
        help_text="Mark check once blood is arranged."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_fulfilled', 'needed_by', '-created_at']

    def __str__(self):
        status = "Fulfilled" if self.is_fulfilled else "Urgent"
        return f"[{status}] {self.blood_group} for {self.patient_name}"


class Committee(models.Model):
    """
    Represents a specific year's elected committee (e.g. 2025 - 26 Committee).
    """
    name = models.CharField(
        max_length=100, 
        help_text="E.g. 2025 - 26 KCYM Committee"
    )
    start_year = models.IntegerField(help_text="E.g. 2025")
    end_year = models.IntegerField(help_text="E.g. 2026")
    is_active = models.BooleanField(
        default=False,
        help_text="Mark True if this is the current active committee. Only one committee should be active."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_year', '-id']

    def save(self, *args, **kwargs):
        # If this committee is marked active, deactivate all other committees
        if self.is_active:
            Committee.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Active" if self.is_active else "Past"
        return f"{self.name} ({status})"


class CommitteeMember(models.Model):
    """
    Elected member positions inside a specific year's Committee.
    """
    POSITIONS = [
        ('PRESIDENT', 'President'),
        ('VICE_PRESIDENT', 'Vice President'),
        ('SECRETARY', 'Secretary'),
        ('JOINT_SECRETARY', 'Joint Secretary'),
        ('TREASURER', 'Treasurer'),
        ('COMMITTEE_MEMBER', 'Committee Member'),
    ]

    committee = models.ForeignKey(
        Committee,
        on_delete=models.CASCADE,
        related_name="members"
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="committee_positions"
    )
    position = models.CharField(
        max_length=30,
        choices=POSITIONS,
        default='COMMITTEE_MEMBER'
    )
    joined_at = models.DateField(default=datetime.date.today)

    class Meta:
        unique_together = ('committee', 'member')
        ordering = ['position', 'member__first_name']

    def __str__(self):
        return f"{self.member.first_name} - {self.position} ({self.committee.name})"


class BloodDonor(models.Model):
    """
    Represents an emergency blood donor.
    Can be optionally linked to a KCYM member, or exist as a direct external entry.
    """
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='donor_profile'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(
        max_length=15, 
        unique=True, 
        validators=[phone_validator]
    )
    gender = models.CharField(
        max_length=10, 
        choices=Member.GENDERS, 
        default='MALE'
    )
    blood_group = models.CharField(
        max_length=3, 
        choices=Member.BLOOD_GROUPS
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="Donor date of birth."
    )
    last_donation_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Date of last blood donation."
    )
    total_donations = models.PositiveIntegerField(
        default=0,
        blank=True,
        help_text="Total number of times this donor has donated blood."
    )
    is_active_donor = models.BooleanField(
        default=True,
        help_text="Designate if this donor is currently active and available."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_donation_date', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.blood_group})"


# Django signals to auto-sync KCYM Members to the unified Blood Donors registry
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Member)
def sync_donor_profile(sender, instance, created, **kwargs):
    # If the member is active, approved, and wants to be a donor
    if instance.is_active and instance.role != 'PENDING' and instance.is_active_donor:
        BloodDonor.objects.update_or_create(
            member=instance,
            defaults={
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'phone_number': instance.phone_number,
                'gender': instance.gender or 'MALE',
                'blood_group': instance.blood_group,
                'date_of_birth': instance.date_of_birth,
                'last_donation_date': instance.last_donation_date,
                'total_donations': instance.total_donations,
                'is_active_donor': True
            }
        )
    else:
        # Remove them if they are no longer an active donor or not active/approved
        BloodDonor.objects.filter(member=instance).delete()

@receiver(post_delete, sender=Member)
def delete_donor_profile(sender, instance, **kwargs):
    BloodDonor.objects.filter(member=instance).delete()

