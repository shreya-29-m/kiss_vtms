# KISS Vocational Training Management System (VTMS)
### College Software Engineering (SE) Subject Project &bull; Academic Year 2026

An end-to-end, functional, professional web application designed for students of **Kalinga Institute of Social Sciences (KISS)** to organize vocational training programs, facilitate skill-development course discovery, manage hands-on workshop instruction, and award verified digital completion certificates.

---

## 📌 Key Capabilities & Features

### 👨‍🎓 1. Student Trainee Portal
- **Self-Registration & Profile:** Auto-generates unique Student ID (`KISS-STU-2026-XXXX`), tracks academic stream, trades of interest, and uploaded qualification documents.
- **Course Catalog & Filtering:** Search by keyword or filter by vocational trade (Computer & IT, Agriculture, Tailoring, Handicrafts, Electrical, Hospitality, Beauty, Entrepreneurship).
- **Capacity-Enforced Enrollment:** Instantly enrolls in eligible courses, prevents duplicate enrollments, and blocks registration when seat limits are reached.
- **Training Schedule & Calendar:** View upcoming practical lab sessions, timing, topics, and lab venues.
- **Verifiable Attendance:** Real-time percentage tracking against the course threshold (e.g. 75%).
- **Assessments & Coaching:** View practical test results, project percentages, and qualitative trainer feedback.
- **Downloadable PDF Certificate:** Programmatically generates landscape PDF completion certificates once both attendance and passing score criteria are met.

### 👨‍🏫 2. Vocational Trainer Portal
- **Assigned Course Roster:** View all batches assigned by the administrator and enrolled student cohorts.
- **Training Session Scheduling:** Add upcoming workshop dates, start/end times, topics, and lab rooms.
- **Daily Attendance Marking:** Record attendance (`Present`, `Late`, `Excused`, `Absent`) by date with automatic percentage recalculation and correction support.
- **Course Learning Materials:** Upload workshop handbooks, blueprint documents, and external reference links.
- **Practical Assessments & Rubric Grading:** Create practical tasks with maximum scores, enter marks obtained, and provide constructive improvement coaching.
- **Course Readiness Reports:** Monitor trainee completion readiness and certification eligibility.

### 🛡️ 3. Administrator Control Center
- **Institutional Analytics:** Live metrics on active courses, student trainees, faculty trainers, seat occupancy rates, and certificate issuances.
- **Course & Category Management:** Create and edit vocational categories and courses with custom capacities, schedules, and completion thresholds.
- **User & Access Control:** Provision student, trainer, and administrator accounts, with account deactivation/activation controls.
- **Capacity & Enrollment Oversight:** Monitor and update enrollment statuses (`enrolled`, `completed`, `cancelled`).
- **Security Audit Logs:** Chronological trace of system authentication, mutations, and certificate issuances with IP tracking.
- **Report Export:** Generate and download comprehensive CSV enrollment reports for institutional accreditation.

---

## 🛠️ Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | Python & Flask | 3.14 / 3.1.3 | Modular Application Factory & Blueprints |
| **Database** | SQLite + SQLAlchemy | 2.1.3 | Relational database with normalized schema & constraints |
| **Authentication** | Flask-Login & Werkzeug | 0.6.3 / 3.1.9 | Session management & salted PBKDF2 password hashing |
| **PDF Engine** | ReportLab | 5.0.1 | Pixel-precise, vector-drawn landscape completion certificates |
| **Frontend** | HTML5, CSS3, ES6 JS | Native / Modern | Responsive, institutional layout; zero build tools required |
| **Testing** | Pytest | 9.1.1 | Automated testing across unit, integration, and security |

---

## 📂 Project Directory Structure

```
kiss-vtms/
├── app/
│   ├── __init__.py           # Application factory, extensions, and blueprint registration
│   ├── config.py             # Config classes (development, file uploads, testing)
│   ├── models.py             # Normalized SQLAlchemy database models
│   ├── auth/                 # Authentication blueprint (Login, Register, Profile, Logout)
│   ├── student/              # Student trainee portal blueprint
│   ├── trainer/              # Vocational trainer portal blueprint
│   ├── admin/                # Administrator control center blueprint
│   ├── utils/
│   │   ├── decorators.py     # Role-based access control (@role_required)
│   │   ├── audit.py          # Audit logging helper
│   │   └── certificate_gen.py# ReportLab landscape PDF certificate generator
│   ├── static/
│   │   ├── css/style.css     # Institutional design stylesheet (responsive, accessible)
│   │   ├── js/main.js        # Client-side filtering, alerts, and confirmation dialogs
│   │   └── uploads/          # Secure file storage (certificates, materials, documents)
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html         # Base template with responsive navigation & role badges
│       ├── index.html        # Institutional landing page & course showcase
│       ├── auth/             # Login, registration, and profile templates
│       ├── student/          # Dashboard, catalog, schedule, attendance, assessments
│       ├── trainer/          # Dashboard, courses, attendance sheet, grading, reports
│       └── admin/            # Dashboard, categories, courses, users, audit logs, reports
├── docs/                     # Comprehensive Software Engineering Documentation
│   ├── SRS.md                # Software Requirements Specification (FR, NFR, Feasibility)
│   ├── SYSTEM_DESIGN.md      # Architecture, DFD Level-0/1, ERD, UML Diagrams & Schema
│   ├── TEST_PLAN_RESULTS.md  # 25 executed test cases, verification table & bug fixes
│   └── USER_MANUAL.md        # Step-by-step user guide for all 3 roles
├── tests/                    # Pytest automated test suite (25 test cases, 100% pass)
│   ├── conftest.py           # Fixtures for in-memory SQLite and mock users
│   ├── test_auth.py          # Authentication, password hashing, and RBAC tests
│   ├── test_courses.py       # Course CRUD, seat limits, duplicate enrollment tests
│   ├── test_attendance.py    # Attendance entry and automatic percentage calculation tests
│   ├── test_assessments.py   # Assessment creation, grading, and result privacy tests
│   ├── test_certificates.py  # Certification eligibility rules & PDF generator tests
│   └── test_persistence.py   # SQLite database persistence across application restarts
├── seed_data.py              # Realistic fictional demonstration data seeder
├── run.py                    # Application launch entry point
├── requirements.txt          # Python package dependencies
└── README.md                 # Complete project setup and operation guide
```

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Install Required Dependencies
Open PowerShell or your terminal in the `kiss-vtms` directory and run:
```bash
py -m pip install -r requirements.txt
```
*(Or use `python -m pip install -r requirements.txt` depending on your environment).*

### 3. Initialize Database & Populate Realistic Demo Data
Run the database seed script:
```bash
py seed_data.py
```
This initializes the SQLite database schema, creates the directory hierarchy, seeds 8 vocational trade categories, 6 structured courses, scheduled sessions, realistic trainees and trainers, attendance logs, practical assessments, and pre-generates a sample official PDF completion certificate.

### 4. Start the Web Server
Launch the application:
```bash
py run.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000/`**

---

## 🔑 Demonstration Login Credentials

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `Admin@12345` | Full administrative control |
| **Vocational Trainer** | `trainer_it` | `Trainer@12345` | Assigned to Computer & IT Course (`VT-IT-101`) |
| **Vocational Trainer** | `trainer_agri` | `Trainer@12345` | Assigned to Organic Farming Course (`VT-AG-201`) |
| **Student Trainee 1** | `student1` | `Student@12345` | Enrolled in `VT-IT-101` &bull; **Eligible for Certificate** |
| **Student Trainee 4** | `student4` | `Student@12345` | Enrolled in `VT-IT-101` &bull; **60% Attendance (Ineligible)** |

*(You can also use the **"Register as Student"** link on the login page to register a brand new trainee account at any time).*

---

## 🧪 Running the Automated Test Suite

To execute all 25 automated tests with detailed verbose output:
```bash
py -m pytest tests/ -v
```

### Test Verification Summary:
```text
tests/test_assessments.py::test_trainer_create_assessment_and_grade PASSED   [  4%]
tests/test_assessments.py::test_student_view_own_assessment_results PASSED   [  8%]
tests/test_attendance.py::test_record_attendance_and_calculate_percentage PASSED [ 12%]
tests/test_attendance.py::test_attendance_correction_updates_percentage PASSED [ 16%]
tests/test_auth.py::test_login_success_student PASSED                      [ 20%]
tests/test_auth.py::test_login_success_trainer PASSED                      [ 24%]
tests/test_auth.py::test_login_success_admin PASSED                        [ 28%]
tests/test_auth.py::test_login_invalid_password PASSED                     [ 32%]
tests/test_auth.py::test_login_nonexistent_user PASSED                     [ 36%]
tests/test_auth.py::test_student_self_registration PASSED                  [ 40%]
tests/test_auth.py::test_student_registration_duplicate_username PASSED    [ 44%]
tests/test_auth.py::test_student_cannot_access_admin_portal PASSED         [ 48%]
tests/test_auth.py::test_trainer_cannot_access_admin_portal PASSED         [ 52%]
tests/test_auth.py::test_unauthenticated_redirect PASSED                   [ 56%]
tests/test_auth.py::test_logout PASSED                                     [ 60%]
tests/test_certificates.py::test_certificate_ineligible_due_to_attendance PASSED [ 64%]
tests/test_certificates.py::test_certificate_ineligible_due_to_score PASSED [ 68%]
tests/test_certificates.py::test_certificate_eligible_and_generated PASSED [ 72%]
tests/test_certificates.py::test_raw_pdf_certificate_generator PASSED      [ 76%]
tests/test_courses.py::test_admin_create_course PASSED                     [ 80%]
tests/test_courses.py::test_student_enrollment_success PASSED              [ 84%]
tests/test_courses.py::test_duplicate_enrollment_prevention PASSED         [ 88%]
tests/test_courses.py::test_seat_capacity_limit_enforcement PASSED         [ 92%]
tests/test_courses.py::test_admin_category_toggle PASSED                   [ 96%]
tests/test_persistence.py::test_database_persistence_across_app_restart PASSED [100%]

====================== 25 passed in 21.25s ======================
```

---

## 📜 Software Engineering Deliverables

Detailed project documentation has been prepared in the `docs/` directory:
- 📄 **[Software Requirements Specification (SRS)](docs/SRS.md):** Abstract, Problem Statement, Objectives, Scope, Existing Systems Study, Feasibility, FR-1 to FR-15, NFRs, and Access Control Matrix.
- 📐 **[System Design & Architecture](docs/SYSTEM_DESIGN.md):** MVC System Architecture, Context Diagram (Level-0 DFD), Level-1 DFD, Normalized ER Diagram (Mermaid), UML Use Case, Activity Diagram (Course Enrollment), Sequence Diagram (Evaluation & Certification), and Data Dictionary.
- 🧪 **[Test Plan & Verification Report](docs/TEST_PLAN_RESULTS.md):** Test strategy, Traceability Matrix, all 25 test specifications with inputs, expected vs actual outputs, and bug fix logs.
- 📖 **[User Operations Manual](docs/USER_MANUAL.md):** Complete operational manual for Students, Trainers, and Administrators with screenshots and workflows.

---

## ⚖️ Academic Project Disclaimer
*This project is an academic Software Engineering demonstration application built to illustrate educational systems architecture for vocational training scenarios. Demonstration student names, course records, and sample certificates are fictional evaluation data and do not represent official records of Kalinga Institute of Social Sciences (KISS).*
