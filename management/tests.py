import datetime
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Member, Event, EventRSVP, Announcement, BloodRequest, BloodDonor, Committee, CommitteeMember
from .forms import MemberRegistrationForm, BloodRequestForm, BloodDonorForm, MemberProfileForm, MemberAdminUpdateForm


class ModelTestCase(TestCase):
    """
    Tests model creation and structural validations.
    """
    def setUp(self):
        # Setup basic member
        self.member = Member.objects.create_user(
            username='johndoe',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='1234567890',
            gender='MALE',
            date_of_birth='1995-05-15',
            blood_group='O+',
            role='MEMBER'
        )

    def test_member_creation(self):
        self.assertEqual(self.member.username, 'johndoe')
        self.assertEqual(self.member.blood_group, 'O+')
        self.assertEqual(self.member.role, 'MEMBER')
        self.assertEqual(self.member.gender, 'MALE')
        self.assertTrue(self.member.is_active)
        self.assertEqual(str(self.member), "John Doe (johndoe)")

    def test_committee_and_member_creation(self):
        from .models import Committee, CommitteeMember
        
        # Create Committee
        committee = Committee.objects.create(
            name="2025 - 26 KCYM Committee",
            start_year=2025,
            end_year=2026,
            is_active=True
        )
        
        # Create Committee Member
        committee_member = CommitteeMember.objects.create(
            committee=committee,
            member=self.member,
            position='PRESIDENT'
        )
        
        self.assertEqual(committee.name, "2025 - 26 KCYM Committee")
        self.assertEqual(committee_member.position, "PRESIDENT")
        self.assertEqual(self.member.current_position(), "President")
        self.assertTrue(self.member.is_executive())

    def test_age_validation(self):
        # Under 18 member
        underage_member = Member(
            username='underage',
            first_name='Kid',
            last_name='Doe',
            email='kid@example.com',
            phone_number='0987654321',
            date_of_birth=datetime.date.today() - datetime.timedelta(days=17 * 365), # 17 years old
            blood_group='A-',
            role='PENDING'
        )
        with self.assertRaises(ValidationError):
            underage_member.clean()

    def test_event_ordering(self):
        event1 = Event.objects.create(
            title='Old Event',
            description='This event happened yesterday.',
            date_and_time=timezone.now() - datetime.timedelta(days=1),
            location='St. Thomas Church'
        )
        event2 = Event.objects.create(
            title='New Event',
            description='This event will happen tomorrow.',
            date_and_time=timezone.now() + datetime.timedelta(days=1),
            location='St. Thomas Church'
        )
        events = Event.objects.all()
        # Event2 should come first due to reverse-chronological order
        self.assertEqual(events[0], event2)
        self.assertEqual(events[1], event1)


class FormTestCase(TestCase):
    """
    Tests phone number and age validations in Forms.
    """
    def test_registration_form_age_validation(self):
        # Underage registration data
        underage_data = {
            'username': 'minor',
            'first_name': 'Minor',
            'last_name': 'User',
            'email': 'minor@example.com',
            'phone_number': '1122334455',
            'gender': 'MALE',
            'date_of_birth': (datetime.date.today() - datetime.timedelta(days=16 * 365)).strftime('%Y-%m-%d'),
            'blood_group': 'B+',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = MemberRegistrationForm(data=underage_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

        # Valid adult registration data
        adult_data = underage_data.copy()
        adult_data['username'] = 'adult'
        adult_data['date_of_birth'] = (datetime.date.today() - datetime.timedelta(days=20 * 365)).strftime('%Y-%m-%d')
        form = MemberRegistrationForm(data=adult_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_phone_validation(self):
        # Invalid phone number (9 digits)
        invalid_phone_data = {
            'username': 'phone_test',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone_number': '123456789', # 9 digits
            'gender': 'FEMALE',
            'date_of_birth': '1990-01-01',
            'blood_group': 'AB+',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = MemberRegistrationForm(data=invalid_phone_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

        # Valid phone number (10 digits)
        valid_phone_data = invalid_phone_data.copy()
        valid_phone_data['phone_number'] = '9876543211'
        form = MemberRegistrationForm(data=valid_phone_data)
        self.assertTrue(form.is_valid())


class PermissionsTestCase(TestCase):
    """
    Verifies Role-Based Access Control (RBAC) rules.
    """
    def setUp(self):
        # Create standard Member
        self.member = Member.objects.create_user(
            username='member_user',
            password='Password123!',
            first_name='Member',
            last_name='User',
            email='member@example.com',
            phone_number='1112223334',
            date_of_birth='1998-05-15',
            blood_group='A+',
            role='MEMBER',
            is_active=True
        )
        
        # Create Executive
        self.exec_user = Member.objects.create_user(
            username='exec_user',
            password='Password123!',
            first_name='Exec',
            last_name='User',
            email='exec@example.com',
            phone_number='4445556667',
            date_of_birth='1990-05-15',
            blood_group='O+',
            role='EXECUTIVE',
            is_active=True
        )

        # Create Vicar
        self.vicar_user = Member.objects.create_user(
            username='vicar_user',
            password='Password123!',
            first_name='Fr. Thomas',
            last_name='Vicar',
            email='vicar@example.com',
            phone_number='4445556668',
            date_of_birth='1975-05-15',
            blood_group='A+',
            role='VICAR',
            is_active=True
        )

        # Create Assistant Vicar
        self.assistant_vicar_user = Member.objects.create_user(
            username='assistant_vicar_user',
            password='Password123!',
            first_name='Fr. Joseph',
            last_name='Assistant',
            email='assistant.vicar@example.com',
            phone_number='4445556669',
            date_of_birth='1985-05-15',
            blood_group='B+',
            role='ASSISTANT_VICAR',
            is_active=True
        )

        # Create Pending User
        self.pending_user = Member.objects.create_user(
            username='pending_user',
            password='Password123!',
            first_name='Pending',
            last_name='User',
            email='pending@example.com',
            phone_number='7778889990',
            date_of_birth='2002-05-15',
            blood_group='B-',
            role='PENDING',
            is_active=False
        )

    def test_anonymous_access(self):
        # Anonymous users can access home and event timeline
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('executives_list', response.context)
        self.assertIn(self.exec_user, response.context['executives_list'])

        response = self.client.get(reverse('event_timeline'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('history_hub'))
        self.assertEqual(response.status_code, 200)

        # Anonymous users cannot access the blood donor search or dashboard
        response = self.client.get(reverse('blood_search'))
        self.assertEqual(response.status_code, 302) # Redirect to login

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_general_member_access(self):
        # Log in as general member
        self.client.login(username='member_user', password='Password123!')

        # Can access home, timeline, blood donor search, profile
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('event_timeline')).status_code, 200)
        self.assertEqual(self.client.get(reverse('blood_search')).status_code, 200)
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)

        # Cannot access executive dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect back home

    def test_executive_access(self):
        # Log in as executive member
        self.client.login(username='exec_user', password='Password123!')

        # Can access everything including dashboard
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('member_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('blood_search')).status_code, 200)

        # Can approve pending member
        response = self.client.post(reverse('approve_member', kwargs={'pk': self.pending_user.pk}))
        self.assertEqual(response.status_code, 302) # Redirect to dashboard
        
        # Verify pending user role updated and login active
        self.pending_user.refresh_from_db()
        self.assertEqual(self.pending_user.role, 'MEMBER')
        self.assertTrue(self.pending_user.is_active)

    def test_clergy_access(self):
        # Log in as Vicar
        self.client.login(username='vicar_user', password='Password123!')
        # Should be able to view dashboard (role VICAR counts as executive)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('member_list')).status_code, 200)

        # Log in as Assistant Vicar
        self.client.login(username='assistant_vicar_user', password='Password123!')
        # Should be able to view dashboard (role ASSISTANT_VICAR counts as executive)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('member_list')).status_code, 200)

    def test_blood_donor_gender_filtering(self):
        # Create a male donor with common blood group
        male_donor = Member.objects.create_user(
            username='male_donor',
            password='Password123!',
            first_name='Male',
            last_name='Donor',
            email='male@example.com',
            phone_number='1112223344',
            gender='MALE',
            date_of_birth='1990-01-01',
            blood_group='O+',
            role='MEMBER',
            is_active=True,
            is_active_donor=True
        )

        # Create a female donor with allowed rare blood group B- (should show)
        female_b_neg = Member.objects.create_user(
            username='female_b_neg',
            password='Password123!',
            first_name='Female',
            last_name='BNegative',
            email='female.bneg@example.com',
            phone_number='1112223345',
            gender='FEMALE',
            date_of_birth='1990-01-01',
            blood_group='B-',
            role='MEMBER',
            is_active=True,
            is_active_donor=True
        )

        # Create a female donor with allowed rare blood group AB+ (should show)
        female_ab_pos = Member.objects.create_user(
            username='female_ab_pos',
            password='Password123!',
            first_name='Female',
            last_name='ABPositive',
            email='female.abpos@example.com',
            phone_number='1112223346',
            gender='FEMALE',
            date_of_birth='1990-01-01',
            blood_group='AB+',
            role='MEMBER',
            is_active=True,
            is_active_donor=True
        )

        # Create a female donor with rare blood group O- (previously allowed, now hidden)
        female_o_neg = Member.objects.create_user(
            username='female_o_neg',
            password='Password123!',
            first_name='Female',
            last_name='ONegative',
            email='female.oneg@example.com',
            phone_number='1112223347',
            gender='FEMALE',
            date_of_birth='1990-01-01',
            blood_group='O-',
            role='MEMBER',
            is_active=True,
            is_active_donor=True
        )

        # Create a female donor with common blood group O+ (should hide)
        female_o_pos = Member.objects.create_user(
            username='female_o_pos',
            password='Password123!',
            first_name='Female',
            last_name='OPositive',
            email='female.opos@example.com',
            phone_number='1112223348',
            gender='FEMALE',
            date_of_birth='1990-01-01',
            blood_group='O+',
            role='MEMBER',
            is_active=True,
            is_active_donor=True
        )

        # Log in as a member to access blood search page
        self.client.login(username='member_user', password='Password123!')
        
        response = self.client.get(reverse('blood_search'))
        self.assertEqual(response.status_code, 200)
        
        donors = response.context['donors']
        
        # Get matching BloodDonor profiles
        male_donor_profile = BloodDonor.objects.get(member=male_donor)
        female_b_neg_profile = BloodDonor.objects.get(member=female_b_neg)
        female_ab_pos_profile = BloodDonor.objects.get(member=female_ab_pos)
        female_o_neg_profile = BloodDonor.objects.get(member=female_o_neg)
        female_o_pos_profile = BloodDonor.objects.get(member=female_o_pos)
        
        # Check that male_donor, female_b_neg, and female_ab_pos are in the queryset,
        # but female_o_neg and female_o_pos are excluded.
        self.assertIn(male_donor_profile, donors)
        self.assertIn(female_b_neg_profile, donors)
        self.assertIn(female_ab_pos_profile, donors)
        self.assertNotIn(female_o_neg_profile, donors)
        self.assertNotIn(female_o_pos_profile, donors)

    def test_blood_donor_signals_sync(self):
        # 1. Create a pending member, verify no BloodDonor profile is created
        pending_member = Member.objects.create_user(
            username='pending_sync',
            password='Password123!',
            first_name='Pending',
            last_name='Sync',
            email='pending.sync@example.com',
            phone_number='1122334455',
            gender='MALE',
            date_of_birth='1995-05-05',
            blood_group='A+',
            role='PENDING',
            is_active=False,
            is_active_donor=True
        )
        self.assertFalse(BloodDonor.objects.filter(member=pending_member).exists())

        # 2. Approve the member (role=MEMBER, is_active=True), verify BloodDonor is created
        pending_member.role = 'MEMBER'
        pending_member.is_active = True
        pending_member.save()
        self.assertTrue(BloodDonor.objects.filter(member=pending_member).exists())
        donor = BloodDonor.objects.get(member=pending_member)
        self.assertEqual(donor.first_name, 'Pending')
        self.assertEqual(donor.phone_number, '1122334455')
        self.assertEqual(donor.blood_group, 'A+')
        self.assertEqual(donor.gender, 'MALE')

        # 3. Toggle member's is_active_donor to False, verify BloodDonor is deleted
        pending_member.is_active_donor = False
        pending_member.save()
        self.assertFalse(BloodDonor.objects.filter(member=pending_member).exists())

        # 4. Toggle back to True, verify BloodDonor is recreated
        pending_member.is_active_donor = True
        pending_member.save()
        self.assertTrue(BloodDonor.objects.filter(member=pending_member).exists())

        # 5. Delete the member, verify BloodDonor is deleted
        pending_member_id = pending_member.id
        pending_member.delete()
        self.assertFalse(BloodDonor.objects.filter(member_id=pending_member_id).exists())

    def test_member_dob_field_on_form(self):
        # Verify date_of_birth is in MemberProfileForm fields
        form = MemberProfileForm(instance=self.member)
        self.assertIn('date_of_birth', form.fields)

        # Verify date_of_birth is in MemberAdminUpdateForm fields
        admin_form = MemberAdminUpdateForm(instance=self.member)
        self.assertIn('date_of_birth', admin_form.fields)

        # Submit form with valid date_of_birth
        data = {
            'first_name': 'John',
            'last_name': 'Doe Updated',
            'email': 'john.updated@example.com',
            'phone_number': '1234567890',
            'gender': 'MALE',
            'date_of_birth': '1996-06-16',
            'blood_group': 'O+',
            'is_active_donor': True
        }
        form = MemberProfileForm(data=data, instance=self.member)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.member.refresh_from_db()
        self.assertEqual(self.member.date_of_birth, datetime.date(1996, 6, 16))
        self.assertEqual(self.member.last_name, 'Doe Updated')

    def test_external_donor_crud_views(self):
        # Log in as executive member
        self.client.login(username='exec_user', password='Password123!')

        # 1. Verify date_of_birth is required in BloodDonorForm
        donor_data = {
            'first_name': 'External',
            'last_name': 'Donor',
            'email': 'external@example.com',
            'phone_number': '9998887776',
            'gender': 'MALE',
            'blood_group': 'O+',
            'date_of_birth': '',
            'is_active_donor': True
        }
        form = BloodDonorForm(data=donor_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

        # 2. Create an external donor direct entry with date_of_birth populated
        add_url = reverse('donor_add')
        donor_data['date_of_birth'] = '1992-02-02'
        response = self.client.post(add_url, data=donor_data)
        self.assertEqual(response.status_code, 302) # Redirects to blood_search
        
        # Verify created in DB and has no member link
        self.assertTrue(BloodDonor.objects.filter(phone_number='9998887776').exists())
        donor = BloodDonor.objects.get(phone_number='9998887776')
        self.assertIsNone(donor.member)
        self.assertEqual(donor.first_name, 'External')
        self.assertEqual(donor.email, 'external@example.com')

        # 2. View blood_search and confirm donor is visible
        search_url = reverse('blood_search')
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'External Donor')
        self.assertContains(response, 'Add External Donor') # Button for Executive

        # 3. Update donor details
        edit_url = reverse('donor_edit', kwargs={'pk': donor.pk})
        update_data = donor_data.copy()
        update_data['last_name'] = 'Donor-Updated'
        update_data['blood_group'] = 'A-'
        response = self.client.post(edit_url, data=update_data)
        self.assertEqual(response.status_code, 302)
        
        donor.refresh_from_db()
        self.assertEqual(donor.last_name, 'Donor-Updated')
        self.assertEqual(donor.blood_group, 'A-')

        # 4. Delete the external donor
        delete_url = reverse('donor_delete', kwargs={'pk': donor.pk})
        # Check confirmation page loads
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to remove')
        
        # Confirm delete
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BloodDonor.objects.filter(pk=donor.pk).exists())

    def test_member_donor_deletion_behavior(self):
        # Create an active member donor who has a BloodDonor profile
        member_donor = Member.objects.create_user(
            username='member_donor',
            password='Password123!',
            first_name='Member',
            last_name='Donor',
            email='member.donor@example.com',
            phone_number='9990001112',
            gender='MALE',
            date_of_birth='1990-10-10',
            blood_group='B+',
            role='MEMBER',
            is_active=True,
            is_active_donor=True
        )
        self.assertTrue(BloodDonor.objects.filter(member=member_donor).exists())
        donor_profile = BloodDonor.objects.get(member=member_donor)

        # Log in as Executive
        self.client.login(username='exec_user', password='Password123!')

        # Request to remove the donor from registry
        delete_url = reverse('donor_delete', kwargs={'pk': donor_profile.pk})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)

        # Verify that:
        # 1. The BloodDonor profile is deleted
        self.assertFalse(BloodDonor.objects.filter(pk=donor_profile.pk).exists())
        # 2. The Member still exists
        self.assertTrue(Member.objects.filter(pk=member_donor.pk).exists())
        # 3. The Member's is_active_donor flag has been updated to False
        member_donor.refresh_from_db()
        self.assertFalse(member_donor.is_active_donor)

    def test_external_donor_permissions(self):
        # 1. Try to view/add/edit/delete donors as Anonymous
        response = self.client.get(reverse('donor_add'))
        self.assertEqual(response.status_code, 302)
        
        # Create an external donor for testing permissions
        donor = BloodDonor.objects.create(
            first_name='Perm',
            last_name='Test',
            phone_number='8887776665',
            gender='FEMALE',
            blood_group='AB-'
        )
        edit_url = reverse('donor_edit', kwargs={'pk': donor.pk})
        delete_url = reverse('donor_delete', kwargs={'pk': donor.pk})
        
        self.assertEqual(self.client.get(edit_url).status_code, 302)
        self.assertEqual(self.client.post(delete_url).status_code, 302)

        # 2. Try to view/add/edit/delete as General Member
        self.client.login(username='member_user', password='Password123!')
        
        # General member can access blood search list, but NOT the Add button
        response = self.client.get(reverse('blood_search'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Add External Donor')
        
        # General member is blocked from accessing the Add view
        response = self.client.get(reverse('donor_add'))
        self.assertEqual(response.status_code, 302) # Redirect to home with error
        
        response = self.client.post(reverse('donor_add'), data={})
        self.assertEqual(response.status_code, 302)

        # General member is blocked from accessing Edit/Delete views
        self.assertEqual(self.client.get(edit_url).status_code, 302)
        self.assertEqual(self.client.post(delete_url).status_code, 302)

    def test_blood_donor_csv_export_and_tags(self):
        # 1. Log in as Executive
        self.client.login(username='exec_user', password='Password123!')
        
        # 2. Create an external donor (Outside Donor)
        outside_donor = BloodDonor.objects.create(
            first_name='Outside',
            last_name='DonorTest',
            phone_number='8881112223',
            gender='MALE',
            blood_group='O+',
            date_of_birth='1990-01-01'
        )

        # 3. Retrieve blood search page, assert badges exist
        response = self.client.get(reverse('blood_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'KCYM / Church Unit')
        self.assertContains(response, 'Outside Donor')

        # 4. Request CSV Export, check headers and row values
        export_url = reverse('blood_export_csv')
        response = self.client.get(export_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Read CSV content
        csv_content = response.content.decode('utf-8')
        lines = csv_content.splitlines()
        
        # Assert header contains Source
        self.assertIn('Source', lines[0])
        
        # Find outside donor in rows, assert they are marked as Outside Donor
        outside_row = [line for line in lines if 'Outside,DonorTest' in line]
        self.assertTrue(outside_row)
        self.assertIn('Outside Donor', outside_row[0])
        
        # Find member donor in rows, assert they are marked as KCYM / Church Unit
        member_row = [line for line in lines if 'Exec,User' in line or 'Fr. Joseph,Assistant' in line]
        self.assertTrue(member_row)
        self.assertIn('KCYM / Church Unit', member_row[0])


