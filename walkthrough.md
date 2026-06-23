# Walkthrough - KCYM Pulluvazhy Management Application

We have successfully built and verified the complete **KCYM Pulluvazhy Management Application** utilizing Python, Django, and Bootstrap 5. The app implements role-based access control, an emergency blood donor search engine, an events timeline tracker, and a comprehensive unified History Hub dashboard.

---

## What We Built

### 1. Custom Member Authentication, Gender Fields, & RBAC
- Created a custom user model `Member` in [models.py](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/management/models.py) to store profile attributes (phone number, date of birth, gender, blood group, last donation date, active donor status, and roles) in a single integrated model.
- Added a `gender` selection choice field (Male, Female, Other) which is:
  - Required and integrated into public registration requests in [register.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/registration/register.html).
  - Integrated into user profile settings updates in [profile.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/profile.html).
  - Editable by the Executive Committee on admin parameter forms in [member_form.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/member_form.html).
- Seeded a default developer superuser account automatically via migration [0002_seed_admin.py](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/management/migrations/0002_seed_admin.py):
  - **Username**: `KCYM@P`
  - **Password**: `Pulluvazhy@Admin123`
- Implemented **Profile Picture Upload option**: Enabled file upload inputs on user profile settings and admin parameters update forms. Supports file type (`.png`, `.jpg`, `.jpeg`, `.gif`) and size (Max 5MB) validators.
- Integrated **Client-Side File Validator & Instant Preview**: Programmed [main.js](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/static/js/main.js) to intercept file uploads. It validates format extensions and sizes directly in the browser, showing custom error feedback, clearing inputs, and disabling form submissions on failures. It also provides an instant image preview.
- Implemented four authorization roles:
  1. **Vicar (VICAR)** & **Assistant Vicar (ASSISTANT_VICAR)**: Clergy oversight permissions to view the Member directory, manage approvals, post notices, schedule events, and view dashboards.
  2. **Executive Committee (EXECUTIVE)**: Full CRUD on members, approval of pending registration requests, event scheduling, notice posting, and blood donor CSV exports.
  3. **General Member (MEMBER)**: View timeline, update personal donor status/last donation date, and submit event RSVPs.
  4. **Public/Anonymous (PUBLIC)**: View public events, read notices, submit registration requests (defaulting to PENDING role), and post emergency blood requests.

### 2. Emergency Blood Donors Search Engine & Requests Board
- Developed a search panel in [views.py](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/management/views.py) filtering members by blood group and donor availability.
- **Medical/Gender Filter Integration**: Due to medical criteria where females are generally excluded from blood donation, the search panel and CSV exports are filtered to only return:
  - All **Male** donors (and users with unset/other genders).
  - Only **Female** donors carrying **B-negative (B-) or AB-positive (AB+)** blood groups.
- **Donor Age & Tag Display**: Configured [blood_search.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/blood_search.html) to render:
  - Calculated age (e.g. `Age: 24`) next to the donor name.
  - Helper badge under the donor names indicating gender: `Male Donor` or `Female Donor`.
  - Helper source badge indicating registration type: `KCYM / Church Unit` (for member donors) or `Outside Donor` (for external donor direct entries).
- **CSV Export utility**: Created a CSV export utility in [views.py](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/management/views.py) for Executives to download list of matching donors (synchronized with the gender filter logic, including donor age, details, and a dedicated `Source` column).
- Integrated a public **Emergency Blood Requests** bulletin board to register urgent blood needs at specific hospitals.

### 3. Homepage Connect Leadership Directory
- Developed a beautiful dedicated grid section on the landing page [home.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/home.html) under **"Connect with Our Leaders"** displaying the parish clergy, active committee members, and active Executive members.
- Renders their:
  - Profile Image (or initials circle fallback)
  - Full Name
  - Portfolio/Role Title (Vicar, Assistant Vicar, President, Executive Member, etc.)
  - Primary contact phone number (with a clickable `tel:` button for direct calling)
  - Professional email address (with a clickable `mailto:` link)

### 4. Committee Management & Role Elevations
- Created `Committee` model representing a specific year's elected committee (e.g., "2025 - 26 KCYM Committee").
- Created `CommitteeMember` model linking members to a specific committee with specific elected portfolio roles (President, Vice President, Secretary, Joint Secretary, Treasurer, Committee Member).
- Added helper `current_position()` to `Member` which dynamically fetches the position held by a member for the currently active committee term.
- Updated `is_executive()` so that general members elected to active committee positions are automatically granted Executive credentials and dashboard permissions during their tenure.

### 5. Unified History Hub
- Developed a central **History Hub** dashboard in [views.py](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/management/views.py) and [history_hub.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/history_hub.html) that houses three tabs:
  1. **Committees History**: Scrollable view of past committees, election years, and portfolios held.
  2. **Completed Events**: Filtered list of past events (filtering out private events for public users).
  3. **Arranged Blood Requests**: Archived list of successfully arranged/fulfilled emergency blood requests showing patient name, hospital, blood group, contact, and details.
- Integrated statistics summary cards at the top of the History Hub showing total seeded committees, completed events, and arranged blood requests.
- Integrated History link in [base.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/base.html) navigation header and footer.

### 6. Church & KCYM Leadership sliding marquee
- Implemented an **infinite scrolling running marquee** on the landing page displaying circular profile images of all active leaders (Vicar, Assistant Vicar, active Committee members, and active Executive members).
- Integrated a **dynamic initial-based avatar fallback** to display leaders' initials inside gradient circles when custom profile images are not uploaded.

### 7. Events Tracker & Interactive RSVP
- Created a reverse-chronological events timeline.
- Added **Event Poster attachment options**: Allowed upload of optional image posters (stored in `event_posters/` folder via Django media storage) and configured template rendering on the timeline.
- Added interactive RSVP buttons (Going, Maybe, No) which record responses without reloading pages.

### 8. Premium Aesthetic Layout (Bootstrap 5 & Vanilla CSS)
- Set up a style guide in [style.css](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/static/css/style.css) featuring Outfit (headers) and Inter (body) fonts, Catholic Royal Blue and Warm Gold accent variables, glassmorphism cards, stats cards, and timeline designs.
- Built root responsive templates in [templates/](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/):
  - [base.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/base.html) (Navbar, alert banners, footers)
  - [home.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/home.html) (Landing page showing announcements and blood requests)
  - [blood_search.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/blood_search.html) (Filter panel)
  - [event_timeline.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/event_timeline.html) (Events lists and RSVPs)
  - [dashboard.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/dashboard.html) (Executive panel)
  - [profile.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/profile.html) (User settings)
  - [history_hub.html](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/templates/management/history_hub.html) (Committees, events, and blood history view)

---

## Validation Results

We wrote and executed automated test suites in [tests.py](file:///c:/Users/alanb/Desktop/Projects/KCYM_Pulluvazhy/management/tests.py) verifying:
1. **Age limits**: Verifies registration is rejected if age is under 18.
2. **Phone validation**: Verifies registration is rejected if the number of digits is not 10 or 12.
3. **Gender profile data**: Verifies model creation, choices, and registration form submission parameters for gender.
4. **Blood donor filters**: Verifies that only male donors and rare-group female donors are returned in searches, and common-group females are excluded.
5. **Query ordering**: Verifies events are retrieved newest-first.
6. **RBAC limits**: Verifies that anonymous users are blocked from donor directories, general members can view but not CRUD, and executives have complete access.
7. **Clergy permissions**: Verifies that Vicar and Assistant Vicar accounts receive administrative access.
8. **Committees and member assignments**: Verifies that members assigned to an active committee receive executive permissions automatically.
9. **History Hub access**: Verifies that the unified History Hub is successfully accessible to anonymous users.
10. **Date of Birth & total_donations validation**: Verifies form submission when optional fields are omitted or populated.

### Test Output:
```
Creating test database for alias 'default'...
.................
----------------------------------------------------------------------
Ran 17 tests in 44.077s

OK
Destroying test database for alias 'default'...
```

---

## 9. Blood Donor External Registry & Date of Birth
- **Date of Birth Field**: Included the `date_of_birth` input field within the member profile settings form and the administrative member parameters edit form.
- **External Donor Registry**: Created a separate `BloodDonor` model. This model permits direct donor entries that are **not** linked to KCYM Member accounts.
- **Auto-Sync Signals**: Implemented Django signals to automatically synchronize changes to a KCYM Member's status or availability to their corresponding `BloodDonor` profile.
- **External Donor CRUD & Views**: Added forms and templates allowing Executive Committee members to add, update, and remove external donors directly.
- **Cascading Deletes & Safety**: Overrode the deletion method to ensure that if a member-linked donor is removed from the directory, their `is_active_donor` flag is deactivated on the member profile rather than deleting the member account itself.
- **Optional total_donations**: Marked the `total_donations` field on both `Member` and `BloodDonor` models as `blank=True` so that it is optional on forms and correctly defaults to `0` if not provided.

---

## How to Run & Verify Locally

1. **Start the Development Server**:
   ```powershell
   python manage.py runserver
   ```
2. **Log in as Developer Admin**:
   - Navigate to `http://127.0.0.1:8000/login/`
   - Use the pre-seeded admin credentials:
     - **Username**: `KCYM@P`
     - **Password**: `Pulluvazhy@Admin123`
3. **Test the Workflows**:
   - Visit the **Dashboard** at `http://127.0.0.1:8000/dashboard/` to view registrations.
   - Go to `http://127.0.0.1:8000/history/` to view the unified history hub tabs.
   - Go to `http://127.0.0.1:8000/blood-search/` to filter members by blood group, click "Add External Donor" to add a non-member donor, or edit/delete existing donors.
   - Access `http://127.0.0.1:8000/events/` to post events and RSVP to them.

