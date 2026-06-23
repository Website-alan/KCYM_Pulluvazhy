from django.urls import path
from .views import (
    HomeView,
    RegisterView,
    RegistrationPendingView,
    CustomLoginView,
    CustomLogoutView,
    ProfileView,
    ExecutiveDashboardView,
    ApproveMemberActionView,
    RejectMemberActionView,
    MemberListView,
    MemberCreateView,
    MemberUpdateView,
    MemberDeleteView,
    BloodDonorSearchView,
    ExportBloodDonorsCSVView,
    BloodDonorCreateView,
    BloodDonorUpdateView,
    BloodDonorDeleteView,
    EventTimelineView,
    EventRSVPView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    AnnouncementCreateView,
    AnnouncementUpdateView,
    AnnouncementDeleteView,
    BloodRequestCreateView,
    BloodRequestFulfilledActionView,
    HistoryHubView
)

urlpatterns = [
    # Public Pages & Auth
    path('', HomeView.as_view(), name='home'),
    path('history/', HistoryHubView.as_view(), name='history_hub'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/pending/', RegistrationPendingView.as_view(), name='registration_pending'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Executive Dashboard & Actions
    path('dashboard/', ExecutiveDashboardView.as_view(), name='dashboard'),
    path('dashboard/approve/<int:pk>/', ApproveMemberActionView.as_view(), name='approve_member'),
    path('dashboard/reject/<int:pk>/', RejectMemberActionView.as_view(), name='reject_member'),
    
    # Members CRUD
    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/add/', MemberCreateView.as_view(), name='member_add'),
    path('members/<int:pk>/edit/', MemberUpdateView.as_view(), name='member_edit'),
    path('members/<int:pk>/delete/', MemberDeleteView.as_view(), name='member_delete'),
    
    # Blood Donors Directory
    path('blood-search/', BloodDonorSearchView.as_view(), name='blood_search'),
    path('blood-search/add/', BloodDonorCreateView.as_view(), name='donor_add'),
    path('blood-search/<int:pk>/edit/', BloodDonorUpdateView.as_view(), name='donor_edit'),
    path('blood-search/<int:pk>/delete/', BloodDonorDeleteView.as_view(), name='donor_delete'),
    path('blood-search/export/', ExportBloodDonorsCSVView.as_view(), name='blood_export_csv'),
    
    # Events Tracker & RSVP
    path('events/', EventTimelineView.as_view(), name='event_timeline'),
    path('events/add/', EventCreateView.as_view(), name='event_add'),
    path('events/<int:pk>/edit/', EventUpdateView.as_view(), name='event_edit'),
    path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('events/<int:pk>/rsvp/', EventRSVPView.as_view(), name='event_rsvp'),
    
    # Announcement CRUD
    path('announcements/add/', AnnouncementCreateView.as_view(), name='announcement_add'),
    path('announcements/<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='announcement_edit'),
    path('announcements/<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),
    
    # Emergency Blood Requests
    path('blood-requests/add/', BloodRequestCreateView.as_view(), name='blood_request_add'),
    path('blood-requests/<int:pk>/fulfill/', BloodRequestFulfilledActionView.as_view(), name='blood_request_fulfill'),
]
