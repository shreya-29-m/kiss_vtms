# System Architecture & Technical Design Document
## KISS Vocational Training Management System (VTMS)

---

### 1. System Architecture

The application adopts an MVC (Model-View-Controller) multi-layered architecture implemented via Flask Blueprints, Jinja2 template rendering, and SQLAlchemy ORM.

```mermaid
flowchart TD
    subgraph ClientLayer ["Client Layer (Presentation)"]
        Browser["Modern Web Browser (Desktop / Tablet / Mobile)"]
        UI["HTML5 + Modern CSS3 + Vanilla ES6 JS"]
    end

    subgraph AppLayer ["Application Layer (Flask Controller & Business Logic)"]
        Factory["Flask App Factory (create_app)"]
        AuthBP["Auth Blueprint (/auth)"]
        StudentBP["Student Blueprint (/student)"]
        TrainerBP["Trainer Blueprint (/trainer)"]
        AdminBP["Admin Blueprint (/admin)"]
        Decorators["Role Decorators (@role_required)"]
        PDFGen["ReportLab PDF Engine"]
        AuditEngine["Audit Log Utility"]
    end

    subgraph DataLayer ["Data Persistence Layer (SQLAlchemy ORM)"]
        ORM["SQLAlchemy Models"]
        SQLiteDB[("SQLite Database File: kiss_vtms.db")]
        FileStorage["Secure Static Uploads (Certificates / Materials)"]
    end

    Browser <--> UI
    UI <--> |HTTP Requests / Form Posts| Factory
    Factory --> AuthBP
    Factory --> StudentBP
    Factory --> TrainerBP
    Factory --> AdminBP
    
    StudentBP -.-> Decorators
    TrainerBP -.-> Decorators
    AdminBP -.-> Decorators

    StudentBP --> PDFGen
    PDFGen --> FileStorage
    
    AuthBP --> AuditEngine
    AdminBP --> AuditEngine

    AuthBP --> ORM
    StudentBP --> ORM
    TrainerBP --> ORM
    AdminBP --> ORM
    AuditEngine --> ORM
    
    ORM <--> SQLiteDB
```

---

### 2. Data Flow Diagrams (DFD)

#### 2.1 Context Diagram (Level-0 DFD)
The context diagram models the system boundary, external entities (Student, Trainer, Administrator), and major input/output data flows.

```mermaid
flowchart LR
    Student["Student Trainee"]
    Trainer["Vocational Trainer"]
    Admin["System Administrator"]
    VTMS["KISS-VTMS\n(Centralized Vocational Training Management System)"]

    Student --> |"Registration, Course Enrollment, Document Upload"| VTMS
    VTMS --> |"Course Catalog, Attendance Status, Results, PDF Certificate"| Student

    Trainer --> |"Session Schedules, Attendance Records, Assessments, Marks, Materials"| VTMS
    VTMS --> |"Assigned Batches, Enrolled Student Rosters, Course Reports"| Trainer

    Admin --> |"Category & Course CRUD, User Management, Policy Settings"| VTMS
    VTMS --> |"System Analytics, Audit Logs, Exported Reports"| Admin
```

#### 2.2 Level-1 Data Flow Diagram
The Level-1 DFD decomposes the system into its primary operational processes and persistent data stores.

```mermaid
flowchart TD
    Student["Student Entity"]
    Trainer["Trainer Entity"]
    Admin["Administrator Entity"]

    P1["1.0 Authentication & User Management"]
    P2["2.0 Course & Category Management"]
    P3["3.0 Capacity & Enrollment Engine"]
    P4["4.0 Attendance Tracking"]
    P5["5.0 Assessment & Evaluation"]
    P6["6.0 Verification & Certificate Generation"]

    D1[("D1: Users & Profiles")]
    D2[("D2: Categories & Courses")]
    D3[("D3: Enrollments & Schedules")]
    D4[("D4: Attendance Records")]
    D5[("D5: Assessments & Results")]
    D6[("D6: Certificates")]
    D7[("D7: Audit Logs")]

    Student --> |Credentials| P1
    Trainer --> |Credentials| P1
    Admin --> |Credentials & User Admin| P1
    P1 <--> D1
    P1 --> |Log Event| D7

    Admin --> |Manage Trades & Courses| P2
    P2 <--> D2
    P2 --> |Log Event| D7

    Student --> |Enrollment Request| P3
    D2 --> |Seat Limit & Eligibility| P3
    P3 --> |Save Allocation| D3
    P3 --> |Log Event| D7

    Trainer --> |Mark Session Presence| P4
    D3 --> |Enrolled Student List| P4
    P4 --> |Store Date & Status| D4

    Trainer --> |Create Task & Enter Scores| P5
    D3 --> |Enrolled Student List| P5
    P5 --> |Store Rubric & Marks| D5

    Student --> |Certificate Request| P6
    D4 --> |Attendance % Check| P6
    D5 --> |Passing Score Check| P6
    D2 --> |Threshold Criteria| P6
    P6 --> |Issue Verified Record| D6
    P6 --> |Downloadable PDF| Student
```

---

### 3. Entity-Relationship (ER) Diagram

The normalized database schema ensures referential integrity, cascading updates, and data consistency.

```mermaid
erDiagram
    USERS ||--o| STUDENT_PROFILES : "has one"
    USERS ||--o| TRAINER_PROFILES : "has one"
    USERS ||--o{ AUDIT_LOGS : "generates"
    CATEGORIES ||--o{ COURSES : "groups"
    TRAINER_PROFILES ||--o{ COURSES : "instructs"
    COURSES ||--o{ ENROLLMENTS : "has"
    STUDENT_PROFILES ||--o{ ENROLLMENTS : "registers"
    COURSES ||--o{ SESSION_SCHEDULES : "schedules"
    COURSES ||--o{ ATTENDANCE : "tracks"
    STUDENT_PROFILES ||--o{ ATTENDANCE : "attends"
    COURSES ||--o{ LEARNING_MATERIALS : "contains"
    COURSES ||--o{ ASSESSMENTS : "evaluates"
    ASSESSMENTS ||--o{ ASSESSMENT_RESULTS : "yields"
    STUDENT_PROFILES ||--o{ ASSESSMENT_RESULTS : "receives"
    COURSES ||--o{ CERTIFICATES : "awards"
    STUDENT_PROFILES ||--o{ CERTIFICATES : "earns"

    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }

    STUDENT_PROFILES {
        int id PK
        int user_id FK
        string student_id_code UK
        string full_name
        string academic_level
        string contact_number
        string educational_qualification
        text skills_and_interests
        text previous_training
        string document_filename
    }

    TRAINER_PROFILES {
        int id PK
        int user_id FK
        string trainer_id_code UK
        string full_name
        string department_or_trade
        string contact_number
        string qualification
        int experience_years
        text bio
    }

    CATEGORIES {
        int id PK
        string name UK
        text description
        boolean is_active
    }

    COURSES {
        int id PK
        string course_code UK
        string title
        int category_id FK
        int trainer_id FK
        text description
        text skills_covered
        int duration_weeks
        string training_schedule
        int max_seats
        string status
        float attendance_requirement
        float passing_score
        boolean certificate_available
        date start_date
        date end_date
    }

    ENROLLMENTS {
        int id PK
        int student_id FK
        int course_id FK
        string status
        datetime enrolled_at
    }

    ATTENDANCE {
        int id PK
        int course_id FK
        int student_id FK
        date attendance_date
        string status
        string remarks
        int recorded_by_id FK
    }

    ASSESSMENTS {
        int id PK
        int course_id FK
        string title
        string assessment_type
        float max_marks
        date due_date
        text description
    }

    ASSESSMENT_RESULTS {
        int id PK
        int assessment_id FK
        int student_id FK
        float marks_obtained
        text feedback
        int evaluated_by_id FK
    }

    CERTIFICATES {
        int id PK
        string certificate_code UK
        int student_id FK
        int course_id FK
        date issue_date
        float attendance_percentage
        float final_score
        string grade
        string pdf_filename
        boolean is_verified
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string entity_type
        int entity_id
        text details
        string ip_address
        datetime timestamp
    }
```

---

### 4. UML Use Case Diagram

```mermaid
flowchart LR
    subgraph Actors
        S["Student Trainee"]
        T["Vocational Trainer"]
        A["Administrator"]
    end

    subgraph UseCases ["KISS-VTMS Use Cases"]
        UC1["UC-1: Register / Log In"]
        UC2["UC-2: Manage Trainee Profile"]
        UC3["UC-3: Search & Browse Courses"]
        UC4["UC-4: Enroll in Course (Capacity Checked)"]
        UC5["UC-5: View Schedule & Materials"]
        UC6["UC-6: View Attendance & Scores"]
        UC7["UC-7: Download PDF Certificate"]
        UC8["UC-8: Manage Batch Schedules"]
        UC9["UC-9: Record Daily Attendance"]
        UC10["UC-10: Create Practical Assessments"]
        UC11["UC-11: Enter Marks & Qualitative Feedback"]
        UC12["UC-12: Manage Trade Categories"]
        UC13["UC-13: Create & Edit Courses"]
        UC14["UC-14: Manage Users & Roles"]
        UC15["UC-15: Inspect Audit Logs & Export Reports"]
    end

    S --> UC1
    S --> UC2
    S --> UC3
    S --> UC4
    S --> UC5
    S --> UC6
    S --> UC7

    T --> UC1
    T --> UC8
    T --> UC9
    T --> UC10
    T --> UC11

    A --> UC1
    A --> UC12
    A --> UC13
    A --> UC14
    A --> UC15
```

---

### 5. UML Activity Diagram: Course Enrollment

```mermaid
flowchart TD
    Start([Student initiates Course Enrollment]) --> CheckAuth{Is Student Logged In?}
    CheckAuth -- No --> RedirectLogin[Redirect to Login Page]
    CheckAuth -- Yes --> FetchCourse[Fetch Course Details & Status]
    FetchCourse --> CheckActive{Is Course Active?}
    CheckActive -- No --> RejectInactive[Display: Course Inactive]
    CheckActive -- Yes --> CheckDuplicate{Is Student Already Enrolled?}
    CheckDuplicate -- Yes --> RejectDuplicate[Display: Already Enrolled]
    CheckDuplicate -- No --> CheckCapacity{Are Seats Available?\nEnrolled < Max Seats}
    CheckCapacity -- No --> RejectFull[Display: Course Capacity Full]
    CheckCapacity -- Yes --> CreateEnrollment[Insert Enrollment Record]
    CreateEnrollment --> LogAudit[Write to Audit Log]
    LogAudit --> FlashSuccess[Display Enrollment Success Message]
    FlashSuccess --> End([Enrollment Active on Dashboard])
```

---

### 6. UML Sequence Diagram: Assessment Evaluation & Certificate Issuance

```mermaid
sequenceDiagram
    autonumber
    actor Trainer as Vocational Trainer
    actor Student as Student Trainee
    participant Web as Web Application (Flask)
    participant DB as SQLite Database
    participant Engine as ReportLab PDF Engine

    Note over Trainer, Web: Assessment Grading Phase
    Trainer->>Web: POST /trainer/assessments/{id}/grade (Marks & Feedback)
    Web->>DB: Validate marks <= max_marks & update AssessmentResult
    DB-->>Web: Confirmation
    Web->>DB: Write AuditLog entry
    Web-->>Trainer: Render success alert

    Note over Student, Web: Certificate Request Phase
    Student->>Web: GET /student/certificate/{course_id}
    Web->>DB: Query Attendance records for Student & Course
    DB-->>Web: Total sessions, sessions present
    Web->>Web: Calculate Attendance % (e.g. 100%)
    Web->>DB: Query AssessmentResults for Student & Course
    DB-->>Web: Assessment scores
    Web->>Web: Calculate Average Score % (e.g. 90%)
    Web->>DB: Fetch Course thresholds (Req: 75%, Pass: 50%)

    alt Meets All Criteria (Att >= 75% AND Score >= 50%)
        Web->>DB: Insert Certificate Record (KISS-CERT-2026-XXXX)
        Web->>DB: Update Enrollment status to 'completed'
        Web->>Engine: generate_certificate_pdf(...)
        Engine-->>Web: PDF File Stream
        Web-->>Student: Serve authenticated PDF certificate file
    else Criteria Not Met
        Web-->>Student: Flash reason: Below attendance or score threshold
    end
```

---

### 7. Database Data Dictionary

| Table Name | Column Name | Data Type | Nullable | Constraints & Key | Description |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **users** | `id` | INTEGER | No | PK, Auto-increment | Internal unique user ID |
| | `username` | VARCHAR(64) | No | Unique, Index | Unique username |
| | `email` | VARCHAR(120) | No | Unique, Index | User contact email |
| | `password_hash` | VARCHAR(256) | No | | Werkzeug salted hash |
| | `role` | VARCHAR(20) | No | Check ('student','trainer','admin') | User access role |
| | `is_active` | BOOLEAN | No | Default: TRUE | Account operational status |
| | `created_at` | DATETIME | No | Default: UTC Now | Account creation timestamp |
| **student_profiles**| `id` | INTEGER | No | PK, Auto-increment | Profile ID |
| | `user_id` | INTEGER | No | FK(users.id), Unique | 1:1 link to User |
| | `student_id_code`| VARCHAR(30) | No | Unique, Index | Formatted KISS Trainee ID |
| | `full_name` | VARCHAR(100) | No | | Trainee full legal name |
| | `academic_level` | VARCHAR(50) | Yes | | Class/stream (+2 Arts/Sci, etc.) |
| | `contact_number` | VARCHAR(20) | Yes | | Phone contact |
| | `educational_qualification` | VARCHAR(100) | Yes | | Previous qualification |
| | `skills_and_interests` | TEXT | Yes | | Free text trade interests |
| **trainer_profiles**| `id` | INTEGER | No | PK, Auto-increment | Profile ID |
| | `user_id` | INTEGER | No | FK(users.id), Unique | 1:1 link to User |
| | `trainer_id_code`| VARCHAR(30) | No | Unique, Index | Formatted Trainer ID |
| | `full_name` | VARCHAR(100) | No | | Faculty name |
| | `department_or_trade` | VARCHAR(100) | Yes | | Trade domain |
| | `experience_years`| INTEGER | No | Default: 0 | Years of teaching experience |
| **categories** | `id` | INTEGER | No | PK, Auto-increment | Category ID |
| | `name` | VARCHAR(100) | No | Unique | Trade title (e.g. IT, Agriculture) |
| | `is_active` | BOOLEAN | No | Default: TRUE | Public visibility toggle |
| **courses** | `id` | INTEGER | No | PK, Auto-increment | Course ID |
| | `course_code` | VARCHAR(30) | No | Unique, Index | Unique course code (e.g. VT-IT-101) |
| | `title` | VARCHAR(150) | No | | Full course title |
| | `category_id` | INTEGER | No | FK(categories.id) | Linked category |
| | `trainer_id` | INTEGER | Yes | FK(trainer_profiles.id) | Assigned instructor |
| | `max_seats` | INTEGER | No | Default: 30 | Seat capacity limit |
| | `attendance_requirement` | FLOAT | No | Default: 75.0 | Minimum attendance % required |
| | `passing_score` | FLOAT | No | Default: 50.0 | Minimum passing score % |
| **enrollments** | `id` | INTEGER | No | PK, Auto-increment | Enrollment ID |
| | `student_id` | INTEGER | No | FK(student_profiles.id) | Student trainee |
| | `course_id` | INTEGER | No | FK(courses.id) | Enrolled course |
| | `status` | VARCHAR(20) | No | Default: 'enrolled' | 'enrolled', 'completed', 'cancelled' |
| | *Composite Unique* | | No | Unique(student_id, course_id) | Prevents duplicate enrollments |
| **attendance** | `id` | INTEGER | No | PK, Auto-increment | Attendance record ID |
| | `course_id` | INTEGER | No | FK(courses.id) | Training batch |
| | `student_id` | INTEGER | No | FK(student_profiles.id) | Trainee |
| | `attendance_date`| DATE | No | | Session date |
| | `status` | VARCHAR(20) | No | Default: 'present' | 'present', 'late', 'absent', 'excused' |
| | *Composite Unique* | | No | Unique(course_id, student_id, date) | Prevents duplicate logging |
| **assessments** | `id` | INTEGER | No | PK, Auto-increment | Assessment ID |
| | `course_id` | INTEGER | No | FK(courses.id) | Linked course |
| | `title` | VARCHAR(150) | No | | Assessment title |
| | `max_marks` | FLOAT | No | Default: 100.0 | Maximum achievable score |
| **assessment_results** | `id` | INTEGER | No | PK, Auto-increment | Result ID |
| | `assessment_id` | INTEGER | No | FK(assessments.id) | Linked assessment |
| | `student_id` | INTEGER | No | FK(student_profiles.id) | Evaluated trainee |
| | `marks_obtained`| FLOAT | No | | Points awarded |
| | `feedback` | TEXT | Yes | | Trainer coaching feedback |
| **certificates** | `id` | INTEGER | No | PK, Auto-increment | Certificate ID |
| | `certificate_code` | VARCHAR(50) | No | Unique, Index | Validation code |
| | `student_id` | INTEGER | No | FK(student_profiles.id) | Trainee recipient |
| | `course_id` | INTEGER | No | FK(courses.id) | Completed course |
| | `grade` | VARCHAR(10) | No | | Earned grade ('A+', 'A', etc.) |
| | `pdf_filename` | VARCHAR(255) | Yes | | Generated filename |
| **audit_logs** | `id` | INTEGER | No | PK, Auto-increment | Log record ID |
| | `user_id` | INTEGER | Yes | FK(users.id) | Initiating user |
| | `action` | VARCHAR(100) | No | | Action type |
| | `details` | TEXT | Yes | | Audit metadata |
| | `ip_address` | VARCHAR(45) | Yes | | Client IP address |
| | `timestamp` | DATETIME | No | Default: UTC Now | Timestamp |
