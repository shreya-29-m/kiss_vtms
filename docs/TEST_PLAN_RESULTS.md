# Test Plan & Verification Results
## KISS Vocational Training Management System (VTMS)

**Project:** Kalinga Institute of Social Sciences (KISS) Vocational Training Management System  
**Test Framework:** Pytest 9.1.1 on Python 3.14  
**Date Executed:** 06 October 2026  
**Total Test Cases:** 25  
**Passed:** 25 (100%)  
**Failed:** 0 (0%)  

---

### 1. Test Strategy & Objectives

The testing strategy follows a rigorous multi-tier verification process:
1. **Unit & Integration Testing:** Verify that models, relationships, custom constraints, and application helpers function correctly.
2. **Authentication & Authorization Testing:** Verify role-based access control (RBAC) ensuring students cannot access trainer or admin routes, trainers cannot access admin endpoints, and unauthenticated traffic is redirected.
3. **Business Rule Enforcement Testing:** Verify capacity limits, duplicate enrollment prevention, dynamic attendance calculations, score boundaries, and certificate eligibility gates.
4. **Output Integrity Testing:** Verify ReportLab PDF generation, HTTP binary headers, and filesystem persistence.
5. **Regression & Persistence Testing:** Verify that system restart preserves all SQLite tables and state.

---

### 2. Comprehensive Test Execution Results Table

| Test Case ID | Test Function | Module / Component | Input Scenario / Description | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | `test_login_success_student` | `auth` | Valid credentials for student user (`student_test1`) | Successful login; redirect to Trainee Portal | HTTP 200; rendered Trainee Learning Portal | **PASS** |
| **TC-02** | `test_login_success_trainer` | `auth` | Valid credentials for trainer user (`trainer_test`) | Successful login; redirect to Trainer Portal | HTTP 200; rendered Trainer Instruction Portal | **PASS** |
| **TC-03** | `test_login_success_admin` | `auth` | Valid credentials for admin user (`admin_test`) | Successful login; redirect to Admin Control Center | HTTP 200; rendered Administrator Control Center | **PASS** |
| **TC-04** | `test_login_invalid_password` | `auth` | Correct username, incorrect password string | Authentication failure; flash warning message | HTTP 200; displayed "Invalid username or password" | **PASS** |
| **TC-05** | `test_login_nonexistent_user` | `auth` | Non-existent username (`ghost_user`) | Authentication failure; flash warning message | HTTP 200; displayed "Invalid username or password" | **PASS** |
| **TC-06** | `test_student_self_registration` | `auth` | Valid student registration payload | Account created; student ID generated; auto-login | HTTP 200; student ID assigned; welcome alert displayed | **PASS** |
| **TC-07** | `test_student_registration_duplicate_username` | `auth` | Registering with existing username | Request rejected; duplicate warning displayed | HTTP 200; displayed "Username is already taken" | **PASS** |
| **TC-08** | `test_student_cannot_access_admin_portal` | `auth` / `decorators` | Student session accessing `/admin/dashboard` | Route denied; redirect to student dashboard with error | HTTP 200; access denied alert rendered | **PASS** |
| **TC-09** | `test_trainer_cannot_access_admin_portal` | `auth` / `decorators` | Trainer session accessing `/admin/dashboard` | Route denied; redirect to trainer dashboard with error | HTTP 200; access denied alert rendered | **PASS** |
| **TC-10** | `test_unauthenticated_redirect` | `auth` / `login_required` | Anonymous user accessing `/student/dashboard` | Redirect to login page with prompt message | HTTP 200; redirected to `/auth/login` | **PASS** |
| **TC-11** | `test_logout` | `auth` | Active session requesting `/auth/logout` | Session destroyed; redirected to home | HTTP 200; flash message "logged out securely" | **PASS** |
| **TC-12** | `test_admin_create_course` | `admin` / `courses` | Admin creating course with all required fields | Course persisted in DB; visible in catalog | HTTP 200; course displayed in admin course list | **PASS** |
| **TC-13** | `test_admin_category_toggle` | `admin` / `categories` | Admin toggling category active status | Status toggled; flash message rendered | HTTP 200; category deactivated/activated | **PASS** |
| **TC-14** | `test_student_enrollment_success` | `student` / `enrollment` | Student enrolling in available active course | Enrollment created; seat count decreased | HTTP 200; "successfully enrolled" alert displayed | **PASS** |
| **TC-15** | `test_duplicate_enrollment_prevention` | `student` / `enrollment` | Enrolling twice in identical course | Second attempt rejected with informational message | HTTP 200; "already enrolled" alert displayed | **PASS** |
| **TC-16** | `test_seat_capacity_limit_enforcement` | `student` / `enrollment` | 3rd student attempting enrollment when `max_seats=2` | Enrollment rejected; capacity error displayed | HTTP 200; "reached its maximum capacity" displayed | **PASS** |
| **TC-17** | `test_record_attendance_and_calculate_percentage` | `trainer` / `attendance` | Marking 1 present and 1 absent session | 50.0% attendance calculated automatically | Stats evaluated: Total=2, Present=1, Pct=50.0% | **PASS** |
| **TC-18** | `test_attendance_correction_updates_percentage` | `trainer` / `attendance` | Updating previously absent record to present | Attendance percentage recalculates to 100.0% | Stats evaluated: Total=1, Present=1, Pct=100.0% | **PASS** |
| **TC-19** | `test_trainer_create_assessment_and_grade` | `trainer` / `assessments` | Creating assessment and recording 85/100 score | Assessment created; score & feedback saved; avg=85% | HTTP 200; score persisted; stats average=85.0% | **PASS** |
| **TC-20** | `test_student_view_own_assessment_results` | `student` / `assessments` | Student viewing published test results | Marks and instructor feedback visible to student | HTTP 200; score 45.0 and feedback rendered | **PASS** |
| **TC-21** | `test_certificate_ineligible_due_to_attendance` | `models` / `certificates` | Student with 50% attendance (requirement: 75%) | `is_eligible_for_certificate` returns False | Returned `False, "Attendance is 50.0%..."` | **PASS** |
| **TC-22** | `test_certificate_ineligible_due_to_score` | `models` / `certificates` | Student with 35% score (passing threshold: 50%) | `is_eligible_for_certificate` returns False | Returned `False, "Assessment score average is 35.0%..."`| **PASS** |
| **TC-23** | `test_certificate_eligible_and_generated` | `student` / `certificates` | Student meeting attendance (100%) and score (88%) | Certificate record inserted; HTTP binary PDF stream | HTTP 200; mimetype application/pdf; begins `%PDF-` | **PASS** |
| **TC-24** | `test_raw_pdf_certificate_generator` | `utils` / `certificate_gen`| Generating certificate PDF stream via ReportLab | Non-empty byte sequence conforming to PDF standard | Generated >1000 bytes starting with `%PDF-` | **PASS** |
| **TC-25** | `test_database_persistence_across_app_restart`| `persistence` | Re-instantiating app with existing SQLite database | Retains previously committed records | Successfully retrieved user and category | **PASS** |

---

### 3. Bug Fixes & Regression Log

1. **DetachedInstanceError in Test Cases:**
   - *Issue:* In `test_attendance.py` and `test_assessments.py`, objects retrieved inside an application context were referenced after context teardown, causing SQLAlchemy `DetachedInstanceError`.
   - *Fix:* Extracted primitive IDs (`st1_id = st1.id`) within the context block and passed primitives to test payloads.
   - *Verification:* Both tests re-executed and passed with zero errors.

2. **Cross-Dialect Distinct Query:**
   - *Issue:* In `app/__init__.py:48`, `Enrollment.query.distinct(Enrollment.student_id)` raised an SQLAlchemy deprecation warning because PostgreSQL-specific syntax was evaluated on SQLite.
   - *Fix:* Replaced with standard cross-dialect query: `db.session.query(Enrollment.student_id).distinct().count()`.
   - *Verification:* Deprecation warning resolved; index statistics verified.
