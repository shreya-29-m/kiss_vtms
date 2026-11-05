# Software Requirements Specification (SRS)
## KISS Vocational Training Management System (VTMS)

**Project Name:** Vocational Training Management System for Kalinga Institute of Social Sciences (KISS)  
**Academic Context:** College Software Engineering (SE) Subject Project (2026)  
**Author:** Student Engineering Team  
**Status:** Implemented, Tested, and Verified  

---

### 1. Project Title & Abstract

#### 1.1 Project Title
**KISS Vocational Training Management System (KISS-VTMS)**: A Centralized Web-Based Platform for Vocational Skill Discovery, Attendance Tracking, Practical Evaluation, and Verifiable Certification for Tribal Trainees.

#### 1.2 Abstract
Kalinga Institute of Social Sciences (KISS) provides free residential education and comprehensive life-skills to over 30,000 indigenous and tribal students in Odisha. While formal academic education provides foundational literacy, vocational training is vital for imparting practical livelihoods, artisan craftsmanship, technical competence, and micro-entrepreneurship skills. Previously, vocational courses, student rosters, physical workshop logs, and paper-based completion records were dispersed across separate departments without a unified registry.

The KISS Vocational Training Management System (VTMS) is a centralized, role-based web application developed using Python, Flask, SQLAlchemy, and ReportLab. The system orchestrates the complete vocational education lifecycle: student trainee registration, trade and course catalog exploration, capacity-constrained seat enrollment, scheduled session monitoring, date-wise attendance tracking, practical rubric evaluation with instructor feedback, progress calculation, automated tamper-evident PDF completion certificate generation, and an immutable security audit trail. By providing tailored portals for Students, Trainers, and Administrators, the system establishes transparent institutional governance and verifiable skill credentials.

---

### 2. Problem Statement

At large residential institutions serving socio-economically marginalized and tribal youth:
1. **Fragmented Vocational Records:** Skill training programs spanning agriculture, tailoring, information technology, electronics, and indigenous handicrafts operate in departmental silos, making it difficult to track a student's cumulative competencies.
2. **Attendance Leakage & Inaccurate Completion:** Paper-based register attendance fails to provide automatic percentage tracking, frequently leading to premature certification before meeting requisite practical thresholds.
3. **Manual Assessment & Delay in Feedback:** Practical workbench tasks and project assessments lack centralized score logs and structured coaching remarks.
4. **Certificate Tampering & Verification Bottlenecks:** Paper certificates risk misplacement or tampering and lack a centralized verification code linking to the student's actual performance history.
5. **Capacity Management Issues:** Workshops have limited bench space, tooling, and safety equipment. Without automated capacity enforcement, batches either suffer from overcrowding or under-enrollment.

---

### 3. Objectives of the Project

1. **Centralize the Vocational Training Lifecycle:** Implement a unified pipeline from trainee registration, trade browsing, and capacity-enforced enrollment to attendance, assessment, and certification.
2. **Empower Three Core User Roles:**
   - **Students:** Self-discover trade offerings, monitor attendance percentage against thresholds, submit/review practical assignments, and download authentic digital completion certificates.
   - **Trainers:** Manage batch schedules, record date-based presence/absence, design practical assessments, enter scores with qualitative feedback, and review cohort completion readiness.
   - **Administrators:** Oversee trade categories, configure courses with seat limits and certification rules, manage user accounts, inspect audit logs, and export institutional compliance reports.
3. **Automate Business Rule Enforcement:** Prevent duplicate enrollments, block registration when course capacity is reached, enforce dynamic attendance requirements (e.g. $\ge 75\%$), and ensure certificates are issued only when attendance and passing score criteria are met.
4. **Deliver Verified Digital Credentials:** Integrate a programmatic PDF generation engine that renders institutional certificates with student identification, performance indicators, and unique validation codes.
5. **Ensure Software Engineering Rigor:** Deliver modular, maintainable, fully tested code conforming to SE design principles with a 100% automated test pass rate.

---

### 4. Scope

#### 4.1 In Scope (Version 1.0)
- User authentication with secure password hashing (`werkzeug.security`) and server-side session management (`Flask-Login`).
- Role-Based Access Control (RBAC) across `student`, `trainer`, and `admin` roles.
- Dynamic vocational category management (IT, Agriculture, Tailoring, Handicrafts, Electrical, Hospitality, Beauty, Entrepreneurship).
- Course catalog with live keyword search, domain filtering, seat tracking, and eligibility display.
- Capacity-limited enrollment engine with duplicate enrollment prevention.
- Date-wise session attendance recording with percentage calculation (`present`, `late`, `excused`, `absent`).
- Practical assessments creation, score recording, and qualitative coaching feedback.
- Configurable completion criteria (attendance threshold $\ge 75\%$, passing score $\ge 50\%$).
- Automated ReportLab landscape PDF certificate generator with sample academic watermark.
- Administrative audit logging of all significant events.
- Institutional reporting with CSV export.

#### 4.2 Out of Scope (Intentionally Excluded from V1)
- Biometric hardware scanner integration (fingerprint/facial recognition hardware).
- Commercial payment gateway integration (training is free for KISS students).
- Mobile push notifications via native iOS/Android apps (responsive web design utilized instead).
- Video conference streaming (practical trades are conducted in physical workshops).

---

### 5. Existing System Study & Comparative Analysis

| Feature / Dimension | Traditional Institutional Logbooks | Generic Learning Management Systems (e.g. Moodle) | Proposed KISS-VTMS |
| :--- | :--- | :--- | :--- |
| **Primary Focus** | Manual physical documentation | Academic video lectures & online quizzes | Practical vocational trades, hands-on workshop training, and livelihoods |
| **Capacity Management** | Manual sheet counting | Often unlimited virtual seats | Hard capacity enforcement based on physical workshop benches |
| **Attendance Verification** | Paper register, error-prone | Login-based or self-reported | Assigned faculty-recorded session attendance with percentage calculations |
| **Completion Criteria** | Subjective, unverified | Quiz score only | Combined threshold: Minimum verified attendance % AND assessment score |
| **Certificate Delivery** | Printed card paper | Generic HTML/PDF template | Formal landscape institutional PDF with unique verification code |
| **Deployment Simplicity** | N/A | Heavy PHP/MySQL stack requiring complex servers | Lightweight, zero-config Python/Flask with SQLite ORM |

---

### 6. Feasibility Study

#### 6.1 Technical Feasibility
- **Language & Framework:** Python 3.14 with Flask 3.1 micro-framework.
- **ORM & Database:** SQLAlchemy 2.1 ORM with SQLite file-based persistence. Ensures portable, zero-configuration local deployment for academic evaluation and simple migration to PostgreSQL for institutional servers.
- **PDF Generation:** Industry-standard ReportLab 5.0 graphics engine for pixel-precise, vector-drawn PDF certificates.
- **Frontend Architecture:** Standard semantic HTML5, modern CSS3 (custom CSS variables, responsive Grid/Flexbox), and vanilla ES6 JavaScript without heavy build pipelines.
- **Conclusion:** High technical feasibility.

#### 6.2 Operational Feasibility
- The system mirrors actual KISS vocational training workflows (Trainee $\rightarrow$ Workshop Faculty $\rightarrow$ Vocational Directorate).
- Minimal training required: Clean, high-contrast, accessible UI tailored for student trainees and vocational trainers.
- **Conclusion:** High operational feasibility.

#### 6.3 Economic Feasibility
- Developed completely using open-source, permissive technologies (Python, Flask, SQLite, ReportLab).
- Requires zero commercial licenses or external cloud subscriptions.
- **Conclusion:** High economic feasibility.

---

### 7. Functional Requirements (FR)

- **FR-1 [Authentication]:** The system shall authenticate users via username/email and password with secure cryptographic hashing.
- **FR-2 [Role Access Control]:** The system shall restrict page routes and API actions based on the logged-in user's role (`student`, `trainer`, `admin`).
- **FR-3 [Student Self-Registration]:** Eligible students shall be able to register an account, automatically receiving a formatted Student ID code (e.g., `KISS-STU-2026-XXXX`).
- **FR-4 [Profile Management]:** Users shall be able to view and update permitted profile details and upload qualification documents.
- **FR-5 [Category Management]:** Administrators shall create, edit, activate, and deactivate vocational trade categories.
- **FR-6 [Course Configuration]:** Administrators shall configure courses with code, title, duration, schedule, max seat capacity, trainer assignment, and certification thresholds.
- **FR-7 [Course Discovery & Search]:** Students shall search courses by title, code, or skill keyword and filter by trade category.
- **FR-8 [Course Enrollment]:** The system shall permit students to enroll in active courses only when seats are available and reject duplicate enrollments.
- **FR-9 [Session Scheduling]:** Assigned trainers shall create training session records with date, start/end time, topic, and lab/room details.
- **FR-10 [Attendance Recording]:** Trainers shall record daily session attendance (`present`, `late`, `excused`, `absent`) for enrolled students.
- **FR-11 [Attendance Calculation]:** The system shall automatically compute cumulative attendance percentages per student per course.
- **FR-12 [Assessment & Grading]:** Trainers shall create practical assessments, enter marks obtained (bounded between 0 and max marks), and provide qualitative feedback.
- **FR-13 [Certificate Verification & Issuance]:** The system shall verify whether a student meets the configured attendance threshold AND passing score before allowing certificate generation.
- **FR-14 [PDF Generation]:** The system shall programmatically generate downloadable, authenticated PDF certificates with unique certificate codes.
- **FR-15 [Audit Logging & Export]:** The system shall record administrative events in an audit log and allow administrators to export enrollment reports in CSV format.

---

### 8. Non-Functional Requirements (NFR)

1. **Security:** Passwords salted and hashed with PBKDF2/SHA-256 via Werkzeug. CSRF protection on forms. Strict role validation decorators on routes. Safe file upload extension allowlisting (`pdf`, `png`, `jpg`, `jpeg`, `doc`, `docx`).
2. **Reliability & Consistency:** Atomic database transactions with rollback on exceptions. Unique database constraints preventing duplicate enrollments, duplicate attendance entries on the same date, and duplicate certificate issuance.
3. **Performance:** Sub-second page load times on local machines; lightweight server footprint requiring less than 50MB RAM during standard operation.
4. **Usability & Accessibility:** Clean institutional design with intuitive typography, responsive layout adapting from mobile phones to high-resolution desktop displays, and WCAG-compliant color contrast.
5. **Maintainability:** Modular architecture adhering to Flask application factory and blueprint separation (`auth`, `student`, `trainer`, `admin`).

---

### 9. User Roles & Access Control Matrix

| System Module / Route | Guest (Unauthenticated) | Student Trainee | Vocational Trainer | System Administrator |
| :--- | :---: | :---: | :---: | :---: |
| **Landing Page & Public Catalog** | Read | Read | Read | Read |
| **Student Registration** | Create | Denied | Denied | Create |
| **User Sign In / Sign Out** | Execute | Execute | Execute | Execute |
| **Student Dashboard & Schedule** | Denied | Read (Own) | Denied | Denied |
| **Course Enrollment** | Denied | Execute (Own) | Denied | Manage All |
| **View Attendance & Scores** | Denied | Read (Own) | Read (Assigned Cohort) | Read All |
| **Mark Session Attendance** | Denied | Denied | Create / Update (Assigned) | Manage All |
| **Create & Grade Assessments** | Denied | Denied | Create / Update (Assigned) | Manage All |
| **Upload Learning Materials** | Denied | Denied | Create / Manage (Assigned) | Manage All |
| **Generate & Download Certificate**| Denied | Execute (If Eligible) | Read Status | Manage & Re-issue |
| **Category & Course CRUD** | Denied | Denied | Denied | Full Control |
| **User Account Management** | Denied | Denied | Denied | Full Control |
| **Security Audit Logs** | Denied | Denied | Denied | Read All |
| **Export System CSV Reports** | Denied | Denied | Denied | Execute |
