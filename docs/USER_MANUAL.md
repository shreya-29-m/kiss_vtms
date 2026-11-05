# User Guide & Operational Manual
## KISS Vocational Training Management System (VTMS)

---

### 1. Introduction & User Roles Overview

The KISS Vocational Training Management System (VTMS) is a dedicated web portal designed to organize, conduct, and certify vocational skill training programs for students of Kalinga Institute of Social Sciences (KISS).

The system supports three user roles:
1. **Student Trainee:** Discovers vocational courses, enrolls in eligible trades, tracks personal attendance and assessments, and downloads verified digital completion certificates.
2. **Vocational Trainer:** Manages batch instruction, schedules workshops, records daily trainee attendance, designs practical assessments, enters rubric marks with feedback, and reviews cohort progress.
3. **Administrator:** Configures trades, manages course capacity, provisions user roles, oversees system security audit trails, and exports compliance data.

---

### 2. Demonstration User Accounts

| Role | Username | Password | Full Name / Description |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@12345` | System Directorate Admin |
| **Trainer (IT)** | `trainer_it` | `Trainer@12345` | Er. Deepak Kumar Mohapatra (Computer & IT) |
| **Trainer (Agriculture)** | `trainer_agri` | `Trainer@12345` | Dr. Santosh Patra (Sustainable Farming) |
| **Trainer (Tailoring)** | `trainer_tailor`| `Trainer@12345` | Ms. Ananya Barik (Garment & Pattern Design) |
| **Trainer (Handicrafts)**| `trainer_craft` | `Trainer@12345` | Sri Biswanath Murmu (Dokra & Terracotta Art) |
| **Trainer (Electrical)** | `trainer_electric`| `Trainer@12345`| Er. Subash Chandra Jena (Domestic & Solar) |
| **Student 1 (Eligible)** | `student1` | `Student@12345` | Ramesh Majhi (`KISS-STU-2026-101`) &bull; *Certificate Ready* |
| **Student 2** | `student2` | `Student@12345` | Sunita Soren (`KISS-STU-2026-102`) |
| **Student 3** | `student3` | `Student@12345` | Bikram Kiskoo (`KISS-STU-2026-103`) |
| **Student 4 (Incomplete)**| `student4` | `Student@12345` | Laxmi Marndi (`KISS-STU-2026-104`) &bull; *60% Attendance (Ineligible)* |

---

### 3. Student Trainee Walkthrough

#### 3.1 Self-Registration & Sign In
1. Visit the portal homepage (`http://127.0.0.1:5000/`).
2. Click **"Student Registration"** in the top navigation.
3. Provide your Full Name, Academic Stream (e.g. `+2 Arts`, `+2 Science`), Username, Email, and Password.
4. Upon submission, the system generates your unique formatted Student ID (e.g., `KISS-STU-2026-XXXX`) and redirects you to your **Trainee Learning Portal**.

#### 3.2 Browsing & Enrolling in Courses
1. Click **"Courses"** in the top navigation bar.
2. Filter trades by category dropdown (e.g., *Computer and Information Technology*, *Tailoring*, *Agriculture*) or search by keywords.
3. Click **"View Details & Enroll"** on any course card to inspect the curriculum, trainer bio, weekly schedule, and certification requirements.
4. Click **"Enroll Now"**. The system checks seat availability and confirms your enrollment immediately.

#### 3.3 Tracking Attendance & Assessments
1. Navigate to **"Attendance"** to see your cumulative percentage against the minimum institutional requirement (e.g., 75%).
2. Open **"Assessments"** to review your scored practical projects, test percentages, and qualitative coaching feedback from faculty.
3. View **"Materials"** to download workshop blueprints, lab handbooks, and reference cheat sheets.

#### 3.4 Downloading Your Certificate
1. When your attendance $\ge$ required threshold AND your assessment average $\ge$ passing threshold, an active **"Generate / Download Official Certificate"** button appears on your dashboard and under **"My Enrollments"**.
2. Click the button to download your authenticated ReportLab landscape PDF certificate containing your name, Student ID, course title, grade, and unique validation code.

---

### 4. Vocational Trainer Walkthrough

#### 4.1 Accessing Assigned Batches
1. Log in with trainer credentials (e.g., `trainer_it` / `Trainer@12345`).
2. The **Trainer Instruction Portal** presents summary statistics and your active assigned training programs.
3. Click **"Manage Course & Students"** to view your enrolled trainee roster.

#### 4.2 Scheduling Workshop Sessions
1. In the course detail view, locate the **"+ Add Session to Schedule"** form.
2. Select the session date, start time, end time, workshop topic (e.g., *Crimping Cat6 Ethernet Cables*), and lab venue.
3. Click **"Add to Schedule"** to publish the date to your trainees' calendars.

#### 4.3 Marking Daily Attendance
1. Click **"Attendance"** on your assigned course.
2. Pick the date from the date picker (defaults to today).
3. For each trainee on the roster, set status to `Present`, `Late`, `Excused`, or `Absent`, and add optional remarks.
4. Click **"Save Attendance Records"**. Trainees' cumulative percentages update automatically.

#### 4.4 Creating Practical Assessments & Grading
1. Click **"Assessments"** on your course card.
2. Enter the assessment title, type (*Practical Workshop Test*, *Capstone Project*, *Quiz*, *Theory*), maximum marks, and due date.
3. Once created, click **"Grade & Enter Marks"**.
4. Input each student's obtained marks (e.g., `85` out of `100`) and coaching feedback.
5. Click **"Save Assessment Results & Feedback"**.

---

### 5. Administrator Walkthrough

#### 5.1 System Control Center
1. Sign in with administrator credentials (`admin` / `Admin@12345`).
2. The dashboard displays macro-level metrics: total active courses, registered students, faculty trainers, seat occupancies, and recent audit logs.

#### 5.2 Managing Categories & Courses
1. Click **"Categories"** to create new vocational trades or toggle active/inactive status.
2. Click **"Courses"** to configure new training batches, set duration, assign faculty instructors, set maximum seat limits, and define completion rules (e.g., attendance percentage requirement and pass score).

#### 5.3 User Account Provisioning & Role Management
1. Click **"Users"** to inspect all registered accounts.
2. Filter users by role (`Student`, `Trainer`, `Administrator`).
3. Click **"+ Register New User"** to provision new accounts with role-specific profiles.
4. Toggle active status to suspend or reactivate accounts as needed.

#### 5.4 Audit Logs & Compliance Reporting
1. Click **"Audit Logs"** to view a tamper-evident audit trail of all system mutations with client IP addresses and timestamps.
2. Click **"Reports"** to view cross-domain analytics and click **"Export Full Enrollments CSV"** to generate downloadable reports for university review.
