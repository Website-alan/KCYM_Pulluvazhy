import csv
import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count

from .models import Member, Event, EventRSVP, Announcement, BloodRequest, Committee, CommitteeMember, BloodDonor
from .forms import (
    MemberRegistrationForm, 
    MemberProfileForm, 
    MemberAdminUpdateForm,
    EventForm, 
    AnnouncementForm, 
    BloodRequestForm,
    BloodDonorForm
)

# --- Role-Based Access Control Mixins ---

class ExecutiveRequiredMixin(UserPassesTestMixin):
    """
    Restricts access to members who belong to the Executive Committee or are Superusers.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_executive()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Access Denied: Executive Committee permissions required.")
            return redirect('home')
        return super().handle_no_permission()


class ActiveMemberOrExecutiveRequiredMixin(UserPassesTestMixin):
    """
    Restricts access to active general members or executive committee members.
    Anonymous or pending members are barred.
    """
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_executive() or (self.request.user.is_general_member() and self.request.user.is_active)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.role == 'PENDING':
                messages.warning(self.request, "Your membership request is currently pending executive approval.")
            else:
                messages.error(self.request, "Access Denied: Approved general membership required.")
            return redirect('home')
        return super().handle_no_permission()


# --- Public Views ---

class HomeView(TemplateView):
    """
    Public home page showing stats, recent public events, announcements, and active blood requests.
    """
    template_name = "management/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Statistics
        context['total_members_count'] = Member.objects.filter(is_active=True).exclude(role='PENDING').count()
        context['active_donors_count'] = Member.objects.filter(is_active=True, is_active_donor=True).exclude(role='PENDING').count()
        
        # Pinned & standard announcements
        context['announcements'] = Announcement.objects.all()[:5]
        
        # Public events or all events depending on user role
        if self.request.user.is_authenticated and (self.request.user.is_executive() or self.request.user.is_general_member()):
            context['upcoming_events'] = Event.objects.filter(date_and_time__gte=timezone.now())[:3]
        else:
            context['upcoming_events'] = Event.objects.filter(is_public=True, date_and_time__gte=timezone.now())[:3]
            
        # Active/urgent blood requests
        context['blood_requests'] = BloodRequest.objects.filter(is_fulfilled=False)[:3]

        # 1. Fetch Clergy (Vicar and Assistant Vicar)
        clergy = list(Member.objects.filter(is_active=True, role__in=['VICAR', 'ASSISTANT_VICAR']))
        # Sort clergy: Vicar first, Assistant Vicar second
        clergy.sort(key=lambda x: 0 if x.role == 'VICAR' else 1)
        
        # 2. Fetch Active Committee Members
        active_committee_members = list(CommitteeMember.objects.filter(committee__is_active=True).select_related('member'))
        # Sort committee members by position hierarchy
        pos_order = {'PRESIDENT': 0, 'VICE_PRESIDENT': 1, 'SECRETARY': 2, 'JOINT_SECRETARY': 3, 'TREASURER': 4, 'COMMITTEE_MEMBER': 5}
        active_committee_members.sort(key=lambda x: pos_order.get(x.position, 6))
        
        # 3. Fetch other Executive members (who are not clergy and not in active committee)
        included_member_ids = {c.id for c in clergy} | {cm.member_id for cm in active_committee_members}
        other_executives = list(Member.objects.filter(
            is_active=True, 
            role='EXECUTIVE'
        ).exclude(id__in=included_member_ids).order_by('first_name', 'last_name'))
        
        # 4. Combine them into a unified leaders list
        leaders = []
        for c in clergy:
            leaders.append({
                'first_name': c.first_name,
                'last_name': c.last_name,
                'role_label': c.get_role_display(),
                'profile_image': c.profile_image,
            })
        for cm in active_committee_members:
            leaders.append({
                'first_name': cm.member.first_name,
                'last_name': cm.member.last_name,
                'role_label': cm.get_position_display(),
                'profile_image': cm.member.profile_image,
            })
        for ex in other_executives:
            leaders.append({
                'first_name': ex.first_name,
                'last_name': ex.last_name,
                'role_label': 'Executive Member',
                'profile_image': ex.profile_image,
            })
        context['leaders'] = leaders
        context['clergy_list'] = clergy
        context['active_committee_members'] = active_committee_members
        context['executives_list'] = other_executives

        return context


class RegisterView(CreateView):
    """
    Registration view for new members.
    Defaults to status PENDING.
    """
    model = Member
    form_class = MemberRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('registration_pending')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Registration request submitted successfully! Pending Executive approval.")
        return response


class RegistrationPendingView(TemplateView):
    """
    Landing page for newly registered users waiting for executive approval.
    """
    template_name = 'registration/pending_approval.html'


class CustomLoginView(LoginView):
    """
    Overridden Login view to customize display and check member status upon successful login.
    """
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if user.role == 'PENDING':
            messages.warning(self.request, "Your account is pending approval. You cannot log in yet.")
            return redirect('registration_pending')
        return super().form_valid(form)


class CustomLogoutView(View):
    """
    Logout view that handles logout and redirects home.
    """
    def get(self, request):
        logout(request)
        messages.info(request, "Logged out successfully.")
        return redirect('home')
        
    def post(self, request):
        logout(request)
        messages.info(request, "Logged out successfully.")
        return redirect('home')


# --- Member Profile views ---

class ProfileView(LoginRequiredMixin, ActiveMemberOrExecutiveRequiredMixin, View):
    """
    Allows a member to view their details and update donor settings.
    """
    def get(self, request):
        form = MemberProfileForm(instance=request.user)
        rsvps = EventRSVP.objects.filter(member=request.user)
        return render(request, 'management/profile.html', {'form': form, 'rsvps': rsvps})

    def post(self, request):
        form = MemberProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        rsvps = EventRSVP.objects.filter(member=request.user)
        return render(request, 'management/profile.html', {'form': form, 'rsvps': rsvps})


# --- Executive Dashboard and Approvals ---

class ExecutiveDashboardView(LoginRequiredMixin, ExecutiveRequiredMixin, TemplateView):
    """
    Overview page for Executive Committee with registration approvals and user counts.
    """
    template_name = 'management/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Statistics breakdown
        context['pending_approvals'] = Member.objects.filter(role='PENDING')
        context['total_members'] = Member.objects.exclude(role='PENDING').count()
        context['active_donors'] = Member.objects.filter(is_active_donor=True, is_active=True).exclude(role='PENDING').count()
        context['upcoming_events_count'] = Event.objects.filter(date_and_time__gte=timezone.now()).count()
        
        # Blood donor breakdown
        blood_counts = Member.objects.filter(is_active=True).exclude(role='PENDING').values('blood_group').annotate(count=Count('blood_group'))
        context['blood_breakdown'] = {item['blood_group']: item['count'] for item in blood_counts}
        return context


class ApproveMemberActionView(LoginRequiredMixin, ExecutiveRequiredMixin, View):
    """
    Action view to approve pending member registrations.
    """
    def post(self, request, pk):
        member = get_object_or_404(Member, pk=pk)
        if member.role == 'PENDING':
            member.role = 'MEMBER'
            member.is_active = True
            member.save()
            messages.success(request, f"Approved registration request for {member.first_name} {member.last_name}.")
        return redirect('dashboard')


class RejectMemberActionView(LoginRequiredMixin, ExecutiveRequiredMixin, View):
    """
    Action view to reject/delete pending registrations.
    """
    def post(self, request, pk):
        member = get_object_or_404(Member, pk=pk)
        if member.role == 'PENDING':
            name = f"{member.first_name} {member.last_name}"
            member.delete()
            messages.success(request, f"Rejected and removed registration request for {name}.")
        return redirect('dashboard')


# --- Member Directory / CRUD (Executive only) ---

class MemberListView(LoginRequiredMixin, ExecutiveRequiredMixin, ListView):
    """
    Lists all non-pending members.
    """
    model = Member
    template_name = 'management/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        return Member.objects.exclude(role='PENDING').order_by('first_name', 'last_name')


class MemberCreateView(LoginRequiredMixin, ExecutiveRequiredMixin, CreateView):
    """
    Create a new member from the dashboard.
    """
    model = Member
    form_class = MemberAdminUpdateForm
    template_name = 'management/member_form.html'
    success_url = reverse_lazy('member_list')

    def form_valid(self, form):
        messages.success(self.request, "Member created successfully.")
        return super().form_valid(form)


class MemberUpdateView(LoginRequiredMixin, ExecutiveRequiredMixin, UpdateView):
    """
    Update details of a member.
    """
    model = Member
    form_class = MemberAdminUpdateForm
    template_name = 'management/member_form.html'
    success_url = reverse_lazy('member_list')

    def form_valid(self, form):
        messages.success(self.request, f"Member '{self.object.username}' updated successfully.")
        return super().form_valid(form)


class MemberDeleteView(LoginRequiredMixin, ExecutiveRequiredMixin, DeleteView):
    """
    Delete a member.
    """
    model = Member
    template_name = 'management/member_confirm_delete.html'
    success_url = reverse_lazy('member_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Member deleted successfully.")
        return super().delete(request, *args, **kwargs)


# --- Blood Donor Search Engine ---

from django.db.models import Q

class BloodDonorSearchView(LoginRequiredMixin, ActiveMemberOrExecutiveRequiredMixin, ListView):
    """
    Blood donor directory. Filters members by Blood Group and Active status.
    Accessible to General Members and Executive.
    Only shows male donors, other/unset genders, and female donors with rare blood groups.
    """
    model = BloodDonor
    template_name = 'management/blood_search.html'
    context_object_name = 'donors'

    def get_queryset(self):
        queryset = BloodDonor.objects.all()
        
        # Filter: Male, Other, Blank/Null, or Female with allowed blood groups (B-, AB+)
        allowed_female_groups = ['B-', 'AB+']
        condition = Q(gender='MALE') | Q(gender__isnull=True) | Q(gender='') | Q(gender='OTHER') | (Q(gender='FEMALE') & Q(blood_group__in=allowed_female_groups))
        queryset = queryset.filter(condition)
        
        # Filtering by Blood Group
        self.blood_group = self.request.GET.get('blood_group')
        if self.blood_group:
            queryset = queryset.filter(blood_group=self.blood_group)
            
        # Filtering by active donors only (default = show active only)
        self.active_only = self.request.GET.get('active_only', 'on') == 'on'
        if self.active_only:
            queryset = queryset.filter(is_active_donor=True)
            
        return queryset.order_by('last_donation_date', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blood_groups'] = Member.BLOOD_GROUPS
        context['selected_blood_group'] = self.blood_group
        context['active_only'] = self.active_only
        return context


class ExportBloodDonorsCSVView(LoginRequiredMixin, ExecutiveRequiredMixin, View):
    """
    Exports filtered blood donor list to CSV. Executive only.
    """
    def get(self, request):
        queryset = BloodDonor.objects.all()
        
        # Filter: Male, Other, Blank/Null, or Female with allowed blood groups (B-, AB+)
        allowed_female_groups = ['B-', 'AB+']
        condition = Q(gender='MALE') | Q(gender__isnull=True) | Q(gender='') | Q(gender='OTHER') | (Q(gender='FEMALE') & Q(blood_group__in=allowed_female_groups))
        queryset = queryset.filter(condition)
        
        blood_group = request.GET.get('blood_group')
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
            
        active_only = request.GET.get('active_only') == 'true'
        if active_only:
            queryset = queryset.filter(is_active_donor=True)
            
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="kcym_blood_donors_{datetime.date.today()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Blood Group', 'Phone Number', 'Email', 'Active Donor', 'Last Donation Date', 'Source'])
        
        for donor in queryset:
            writer.writerow([
                donor.first_name,
                donor.last_name,
                donor.blood_group,
                donor.phone_number,
                donor.email,
                'Yes' if donor.is_active_donor else 'No',
                donor.last_donation_date if donor.last_donation_date else 'N/A',
                'KCYM / Church Unit' if donor.member else 'Outside Donor'
            ])
            
        return response


class BloodDonorCreateView(LoginRequiredMixin, ExecutiveRequiredMixin, CreateView):
    """
    Allows Executives to register a new external blood donor.
    """
    model = BloodDonor
    form_class = BloodDonorForm
    template_name = 'management/donor_form.html'
    success_url = reverse_lazy('blood_search')

    def form_valid(self, form):
        messages.success(self.request, "External donor registered successfully.")
        return super().form_valid(form)


class BloodDonorUpdateView(LoginRequiredMixin, ExecutiveRequiredMixin, UpdateView):
    """
    Allows Executives to update parameters of an external blood donor.
    """
    model = BloodDonor
    form_class = BloodDonorForm
    template_name = 'management/donor_form.html'
    success_url = reverse_lazy('blood_search')

    def form_valid(self, form):
        messages.success(self.request, "Donor details updated successfully.")
        return super().form_valid(form)


class BloodDonorDeleteView(LoginRequiredMixin, ExecutiveRequiredMixin, DeleteView):
    """
    Allows Executives to remove a blood donor from the registry.
    """
    model = BloodDonor
    template_name = 'management/donor_confirm_delete.html'
    success_url = reverse_lazy('blood_search')

    def form_valid(self, form):
        donor = self.get_object()
        if donor.member:
            member = donor.member
            member.is_active_donor = False
            member.save()
        messages.success(self.request, "Donor removed from directory successfully.")
        return super().form_valid(form)


# --- Events Tracker and RSVPs ---

class EventTimelineView(ListView):
    """
    Lists events in reverse-chronological order.
    Members see all events; anonymous users see only public events.
    """
    model = Event
    template_name = 'management/event_timeline.html'
    context_object_name = 'events'

    def get_queryset(self):
        if self.request.user.is_authenticated and (self.request.user.is_executive() or self.request.user.is_general_member()):
            queryset = Event.objects.all()
        else:
            queryset = Event.objects.filter(is_public=True)
            
        if self.request.user.is_authenticated:
            # Create a lookup dictionary of event_id -> status
            rsvps = {rsvp.event_id: rsvp.status for rsvp in EventRSVP.objects.filter(member=self.request.user)}
            for event in queryset:
                event.user_rsvp = rsvps.get(event.id, None)
        return queryset



class EventRSVPView(LoginRequiredMixin, ActiveMemberOrExecutiveRequiredMixin, View):
    """
    Records RSVP response for a specific event.
    """
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        status = request.POST.get('status')
        if status in ['GOING', 'MAYBE', 'NOT_GOING']:
            rsvp, created = EventRSVP.objects.update_or_create(
                event=event,
                member=request.user,
                defaults={'status': status}
            )
            messages.success(request, f"RSVP updated for event: {event.title}.")
        else:
            messages.error(request, "Invalid RSVP status.")
        return redirect('event_timeline')


class EventCreateView(LoginRequiredMixin, ExecutiveRequiredMixin, CreateView):
    """
    Create a new event. Executive only.
    """
    model = Event
    form_class = EventForm
    template_name = 'management/event_form.html'
    success_url = reverse_lazy('event_timeline')

    def form_valid(self, form):
        messages.success(self.request, "Event scheduled successfully.")
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, ExecutiveRequiredMixin, UpdateView):
    """
    Update an event. Executive only.
    """
    model = Event
    form_class = EventForm
    template_name = 'management/event_form.html'
    success_url = reverse_lazy('event_timeline')

    def form_valid(self, form):
        messages.success(self.request, "Event updated successfully.")
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, ExecutiveRequiredMixin, DeleteView):
    """
    Delete an event. Executive only.
    """
    model = Event
    template_name = 'management/event_confirm_delete.html'
    success_url = reverse_lazy('event_timeline')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Event deleted successfully.")
        return super().delete(request, *args, **kwargs)


# --- Announcement CRUD (Executive only) ---

class AnnouncementCreateView(LoginRequiredMixin, ExecutiveRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'management/announcement_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Announcement posted successfully.")
        return super().form_valid(form)


class AnnouncementUpdateView(LoginRequiredMixin, ExecutiveRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'management/announcement_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Announcement updated successfully.")
        return super().form_valid(form)


class AnnouncementDeleteView(LoginRequiredMixin, ExecutiveRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'management/announcement_confirm_delete.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Announcement removed successfully.")
        return super().delete(request, *args, **kwargs)


# --- Emergency Blood Requests ---

class BloodRequestCreateView(CreateView):
    """
    Allows any user (public or member) to register an urgent blood requirement.
    """
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = 'management/blood_request_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Emergency Blood Request posted! Our members will be notified.")
        return super().form_valid(form)


class BloodRequestFulfilledActionView(LoginRequiredMixin, ActiveMemberOrExecutiveRequiredMixin, View):
    """
    Marks a blood request as fulfilled.
    """
    def post(self, request, pk):
        blood_request = get_object_or_404(BloodRequest, pk=pk)
        blood_request.is_fulfilled = True
        blood_request.save()
        messages.success(request, f"Blood request for {blood_request.patient_name} marked as Fulfilled. Thank you!")
        return redirect('home')


class HistoryHubView(TemplateView):
    """
    Unified History Hub view listing:
    1. Committees history
    2. Past/Completed events (with RBAC visibility)
    3. Fulfilled/Arranged blood requests history
    """
    template_name = 'management/history_hub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Committees
        context['committees'] = Committee.objects.all().prefetch_related('members__member')
        
        # Completed/Past Events
        if self.request.user.is_authenticated and (self.request.user.is_executive() or self.request.user.is_general_member()):
            context['past_events'] = Event.objects.filter(date_and_time__lt=timezone.now())
        else:
            context['past_events'] = Event.objects.filter(is_public=True, date_and_time__lt=timezone.now())
            
        # Fulfilled/Arranged blood requests
        context['arranged_blood'] = BloodRequest.objects.filter(is_fulfilled=True).order_by('-created_at')
        
        return context
