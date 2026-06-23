from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Member, Event, EventRSVP, Announcement, BloodRequest, Committee, CommitteeMember

class MemberAdmin(UserAdmin):
    """
    Admin configuration for the custom User model Member.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'blood_group', 'role', 'is_active_donor', 'is_active')
    list_filter = ('role', 'blood_group', 'is_active_donor', 'is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('KCYM Profile', {'fields': ('phone_number', 'date_of_birth', 'join_date', 'blood_group', 'role')}),
        ('Blood Donation Settings', {'fields': ('is_active_donor', 'last_donation_date')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('KCYM Profile', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'join_date', 'blood_group', 'role')}),
        ('Blood Donation Settings', {'fields': ('is_active_donor', 'last_donation_date')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('first_name', 'last_name')

class EventAdmin(admin.ModelAdmin):
    """
    Admin layout configuration for the Event model.
    """
    list_display = ('title', 'date_and_time', 'location', 'coordinator', 'is_public')
    list_filter = ('is_public', 'date_and_time', 'location')
    search_fields = ('title', 'description', 'location')

class EventRSVPAdmin(admin.ModelAdmin):
    """
    Admin layout configuration for EventRSVPs.
    """
    list_display = ('event', 'member', 'status', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('event__title', 'member__username')

class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin layout configuration for Announcements.
    """
    list_display = ('title', 'date_posted', 'is_pinned')
    list_filter = ('is_pinned', 'date_posted')
    search_fields = ('title', 'content')

class BloodRequestAdmin(admin.ModelAdmin):
    """
    Admin layout configuration for BloodRequests.
    """
    list_display = ('blood_group', 'patient_name', 'hospital', 'needed_by', 'is_fulfilled')
    list_filter = ('is_fulfilled', 'blood_group', 'needed_by')
    search_fields = ('patient_name', 'hospital', 'contact_number')

# Registering models with custom admin pages
admin.site.register(Member, MemberAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventRSVP, EventRSVPAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(BloodRequest, BloodRequestAdmin)

class CommitteeMemberInline(admin.TabularInline):
    model = CommitteeMember
    extra = 1

class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_year', 'end_year', 'is_active')
    list_filter = ('is_active',)
    inlines = [CommitteeMemberInline]

class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ('committee', 'member', 'position', 'joined_at')
    list_filter = ('committee', 'position')
    search_fields = ('member__first_name', 'member__last_name', 'member__username')

admin.site.register(Committee, CommitteeAdmin)
admin.site.register(CommitteeMember, CommitteeMemberAdmin)
