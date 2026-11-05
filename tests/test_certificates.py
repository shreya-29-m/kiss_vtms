from datetime import date, timedelta
from app.models import Course, Enrollment, Attendance, Assessment, AssessmentResult, Certificate, StudentProfile, db
from app.utils.certificate_gen import generate_certificate_pdf

def test_certificate_ineligible_due_to_attendance(client, init_database, app):
    with app.app_context():
        st = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        course = init_database['course']
        course_id = course.id
        db.session.add(Enrollment(student_id=st.id, course_id=course_id, status='enrolled'))

        # Add 2 sessions: 1 absent, 1 present -> 50% attendance (required: 75%)
        db.session.add(Attendance(course_id=course_id, student_id=st.id, attendance_date=date.today() - timedelta(days=2), status='present'))
        db.session.add(Attendance(course_id=course_id, student_id=st.id, attendance_date=date.today() - timedelta(days=1), status='absent'))

        # Assessment passed: 90%
        ass = Assessment(course_id=course_id, title='Exam', max_marks=100.0)
        db.session.add(ass)
        db.session.flush()
        db.session.add(AssessmentResult(assessment_id=ass.id, student_id=st.id, marks_obtained=90.0))
        db.session.commit()

        eligible, reason = st.is_eligible_for_certificate(course)
        assert eligible is False
        assert "below the required" in reason

def test_certificate_ineligible_due_to_score(client, init_database, app):
    with app.app_context():
        st = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        course = init_database['course']
        course_id = course.id
        db.session.add(Enrollment(student_id=st.id, course_id=course_id, status='enrolled'))

        # Attendance 100% (present)
        db.session.add(Attendance(course_id=course_id, student_id=st.id, attendance_date=date.today() - timedelta(days=1), status='present'))

        # Assessment failed: 35% (pass required: 50%)
        ass = Assessment(course_id=course_id, title='Exam', max_marks=100.0)
        db.session.add(ass)
        db.session.flush()
        db.session.add(AssessmentResult(assessment_id=ass.id, student_id=st.id, marks_obtained=35.0))
        db.session.commit()

        eligible, reason = st.is_eligible_for_certificate(course)
        assert eligible is False
        assert "below passing threshold" in reason

def test_certificate_eligible_and_generated(client, init_database, app):
    with app.app_context():
        st = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        course = init_database['course']
        course_id = course.id
        db.session.add(Enrollment(student_id=st.id, course_id=course_id, status='enrolled'))

        # Attendance 100%
        db.session.add(Attendance(course_id=course_id, student_id=st.id, attendance_date=date.today() - timedelta(days=1), status='present'))

        # Assessment passed: 88%
        ass = Assessment(course_id=course_id, title='Exam', max_marks=100.0)
        db.session.add(ass)
        db.session.flush()
        db.session.add(AssessmentResult(assessment_id=ass.id, student_id=st.id, marks_obtained=88.0))
        db.session.commit()

        eligible, reason = st.is_eligible_for_certificate(course)
        assert eligible is True

    # Test downloading certificate through HTTP endpoint
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    response = client.get(f'/student/certificate/{course_id}')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    # ReportLab PDF magic header
    assert response.data.startswith(b'%PDF-')

    # Verify certificate record is created in database
    with app.app_context():
        cert = Certificate.query.filter_by(student_id=st.id, course_id=course_id).first()
        assert cert is not None
        assert cert.final_score == 88.0
        assert cert.grade == 'A+'
        # Enrollment status updated to completed
        enr = Enrollment.query.filter_by(student_id=st.id, course_id=course_id).first()
        assert enr.status == 'completed'

def test_raw_pdf_certificate_generator():
    pdf_bytes = generate_certificate_pdf(
        student_name="Ramesh Majhi",
        student_id_code="KISS-STU-2026-101",
        course_title="Computer Hardware & Networking",
        course_code="VT-IT-101",
        category_name="Computer and Information Technology",
        duration_weeks=8,
        attendance_pct=95.0,
        final_score=88.0,
        grade="A+",
        certificate_code="KISS-CERT-2026-99999",
        issue_date_str="06 October 2026",
        trainer_name="Er. Deepak Mohapatra"
    )
    assert pdf_bytes is not None
    assert pdf_bytes.startswith(b'%PDF-')
    assert len(pdf_bytes) > 1000
