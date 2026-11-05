import os
import random
from datetime import date, datetime
from flask import render_template, redirect, url_for, flash, request, current_app, send_file, abort
from flask_login import login_required, current_user
from app.student import student_bp
from app.models import (
    db, Course, Category, Enrollment, SessionSchedule, Attendance,
    LearningMaterial, Assessment, AssessmentResult, Certificate, StudentProfile
)
from app.utils.decorators import role_required
from app.utils.audit import log_audit
from app.utils.certificate_gen import generate_certificate_pdf

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    student = current_user.student_profile
    if not student:
        flash('Student profile not found. Please contact support.', 'danger')
        return redirect(url_for('auth.logout'))

    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    enrolled_course_ids = [e.course_id for e in enrollments]

    # Calculate overall stats
    total_enrolled = len(enrollments)
    active_courses = [e for e in enrollments if e.status == 'enrolled']
    completed_courses = [e for e in enrollments if e.status == 'completed']
    certificates_count = Certificate.query.filter_by(student_id=student.id).count()

    # Upcoming sessions
    today = date.today()
    upcoming_sessions = SessionSchedule.query.filter(
        SessionSchedule.course_id.in_(enrolled_course_ids) if enrolled_course_ids else False,
        SessionSchedule.session_date >= today
    ).order_by(SessionSchedule.session_date.asc(), SessionSchedule.start_time.asc()).limit(5).all()

    # Per-course summary data for quick view
    course_summaries = []
    for enr in enrollments:
        att = student.get_attendance_stats(enr.course_id)
        ass = student.get_assessment_stats(enr.course_id)
        eligible, reason = student.is_eligible_for_certificate(enr.course)
        cert = Certificate.query.filter_by(student_id=student.id, course_id=enr.course_id).first()
        course_summaries.append({
            'enrollment': enr,
            'course': enr.course,
            'attendance': att,
            'assessment': ass,
            'eligible': eligible,
            'certificate': cert
        })

    return render_template(
        'student/dashboard.html',
        student=student,
        total_enrolled=total_enrolled,
        active_count=len(active_courses),
        completed_count=len(completed_courses),
        certificates_count=certificates_count,
        upcoming_sessions=upcoming_sessions,
        course_summaries=course_summaries
    )


@student_bp.route('/courses')
@login_required
@role_required('student')
def courses():
    student = current_user.student_profile
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)

    query = Course.query.filter_by(status='active')

    if search_query:
        query = query.filter(
            (Course.title.ilike(f'%{search_query}%')) |
            (Course.description.ilike(f'%{search_query}%')) |
            (Course.skills_covered.ilike(f'%{search_query}%')) |
            (Course.course_code.ilike(f'%{search_query}%'))
        )

    if category_id:
        query = query.filter_by(category_id=category_id)

    courses_list = query.order_by(Course.start_date.asc()).all()
    categories = Category.query.filter_by(is_active=True).all()

    # Track student's currently enrolled course IDs
    enrolled_course_ids = [
        e.course_id for e in Enrollment.query.filter_by(student_id=student.id).all()
    ]

    return render_template(
        'student/courses.html',
        courses=courses_list,
        categories=categories,
        search_query=search_query,
        selected_category=category_id,
        enrolled_course_ids=enrolled_course_ids
    )


@student_bp.route('/courses/<int:course_id>')
@login_required
@role_required('student')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    student = current_user.student_profile
    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
    schedules = SessionSchedule.query.filter_by(course_id=course.id).order_by(SessionSchedule.session_date.asc()).all()
    materials = LearningMaterial.query.filter_by(course_id=course.id).all() if enrollment else []

    attendance_stats = student.get_attendance_stats(course.id) if enrollment else None
    assessment_stats = student.get_assessment_stats(course.id) if enrollment else None
    certificate = Certificate.query.filter_by(student_id=student.id, course_id=course.id).first() if enrollment else None

    return render_template(
        'student/course_detail.html',
        course=course,
        enrollment=enrollment,
        schedules=schedules,
        materials=materials,
        attendance_stats=attendance_stats,
        assessment_stats=assessment_stats,
        certificate=certificate
    )


@student_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
@role_required('student')
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    student = current_user.student_profile

    # Business Rule: Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
    if existing_enrollment:
        flash(f'You are already enrolled in {course.title}.', 'info')
        return redirect(url_for('student.course_detail', course_id=course.id))

    # Business Rule: Check if course is active
    if course.status != 'active':
        flash('This course is currently not accepting new enrollments.', 'warning')
        return redirect(url_for('student.courses'))

    # Business Rule: Check seat availability
    if course.is_full:
        flash(f'Enrollment failed: The course {course.title} has reached its maximum capacity of {course.max_seats} seats.', 'danger')
        return redirect(url_for('student.course_detail', course_id=course.id))

    # Create enrollment
    new_enrollment = Enrollment(student_id=student.id, course_id=course.id, status='enrolled')
    db.session.add(new_enrollment)
    db.session.commit()

    log_audit('Course Enrollment', entity_type='Course', entity_id=course.id,
              details=f'Student {student.student_id_code} enrolled in {course.course_code}')

    flash(f'Congratulations! You have successfully enrolled in {course.title}. Check your schedule to attend sessions.', 'success')
    return redirect(url_for('student.course_detail', course_id=course.id))


@student_bp.route('/my-enrollments')
@login_required
@role_required('student')
def my_enrollments():
    student = current_user.student_profile
    enrollments = Enrollment.query.filter_by(student_id=student.id).order_by(Enrollment.enrolled_at.desc()).all()

    items = []
    for enr in enrollments:
        att = student.get_attendance_stats(enr.course_id)
        ass = student.get_assessment_stats(enr.course_id)
        cert = Certificate.query.filter_by(student_id=student.id, course_id=enr.course_id).first()
        eligible, reason = student.is_eligible_for_certificate(enr.course)
        items.append({
            'enrollment': enr,
            'attendance': att,
            'assessment': ass,
            'certificate': cert,
            'eligible': eligible,
            'reason': reason
        })

    return render_template('student/my_enrollments.html', items=items, student=student)


@student_bp.route('/schedule')
@login_required
@role_required('student')
def schedule():
    student = current_user.student_profile
    enrolled_course_ids = [e.course_id for e in Enrollment.query.filter_by(student_id=student.id).all()]

    if not enrolled_course_ids:
        schedules = []
    else:
        schedules = SessionSchedule.query.filter(
            SessionSchedule.course_id.in_(enrolled_course_ids)
        ).order_by(SessionSchedule.session_date.asc(), SessionSchedule.start_time.asc()).all()

    return render_template('student/schedule.html', schedules=schedules)


@student_bp.route('/attendance')
@login_required
@role_required('student')
def attendance():
    student = current_user.student_profile
    enrolled_courses = [e.course for e in Enrollment.query.filter_by(student_id=student.id).all()]

    selected_course_id = request.args.get('course_id', type=int)
    if not selected_course_id and enrolled_courses:
        selected_course_id = enrolled_courses[0].id

    selected_course = None
    records = []
    stats = {'total': 0, 'present': 0, 'percentage': 0.0}

    if selected_course_id:
        selected_course = Course.query.get(selected_course_id)
        records = Attendance.query.filter_by(
            student_id=student.id, course_id=selected_course_id
        ).order_by(Attendance.attendance_date.desc()).all()
        stats = student.get_attendance_stats(selected_course_id)

    return render_template(
        'student/attendance.html',
        enrolled_courses=enrolled_courses,
        selected_course=selected_course,
        records=records,
        stats=stats
    )


@student_bp.route('/materials')
@login_required
@role_required('student')
def materials():
    student = current_user.student_profile
    enrolled_courses = [e.course for e in Enrollment.query.filter_by(student_id=student.id).all()]
    enrolled_course_ids = [c.id for c in enrolled_courses]

    selected_course_id = request.args.get('course_id', type=int)
    if selected_course_id:
        if selected_course_id not in enrolled_course_ids:
            abort(403)
        materials_list = LearningMaterial.query.filter_by(course_id=selected_course_id).order_by(LearningMaterial.uploaded_at.desc()).all()
    else:
        materials_list = LearningMaterial.query.filter(
            LearningMaterial.course_id.in_(enrolled_course_ids) if enrolled_course_ids else False
        ).order_by(LearningMaterial.uploaded_at.desc()).all()

    return render_template(
        'student/materials.html',
        enrolled_courses=enrolled_courses,
        selected_course_id=selected_course_id,
        materials=materials_list
    )


@student_bp.route('/assessments')
@login_required
@role_required('student')
def assessments():
    student = current_user.student_profile
    enrolled_courses = [e.course for e in Enrollment.query.filter_by(student_id=student.id).all()]
    enrolled_course_ids = [c.id for c in enrolled_courses]

    assessments_data = []
    if enrolled_course_ids:
        all_assessments = Assessment.query.filter(
            Assessment.course_id.in_(enrolled_course_ids)
        ).order_by(Assessment.created_at.desc()).all()

        for a in all_assessments:
            result = AssessmentResult.query.filter_by(assessment_id=a.id, student_id=student.id).first()
            assessments_data.append({
                'assessment': a,
                'result': result,
                'is_submitted': result is not None
            })

    return render_template(
        'student/assessments.html',
        assessments_data=assessments_data,
        enrolled_courses=enrolled_courses
    )


@student_bp.route('/certificate/<int:course_id>')
@login_required
@role_required('student')
def download_certificate(course_id):
    course = Course.query.get_or_404(course_id)
    student = current_user.student_profile

    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
    if not enrollment:
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('student.my_enrollments'))

    # Check certificate eligibility
    eligible, reason = student.is_eligible_for_certificate(course)
    if not eligible:
        flash(f'Cannot generate certificate: {reason}', 'warning')
        return redirect(url_for('student.my_enrollments'))

    # Check or create certificate record
    cert = Certificate.query.filter_by(student_id=student.id, course_id=course.id).first()
    att_stats = student.get_attendance_stats(course.id)
    ass_stats = student.get_assessment_stats(course.id)

    # Determine grade
    avg_score = ass_stats['average_percentage']
    if avg_score >= 85:
        grade = 'A+'
    elif avg_score >= 70:
        grade = 'A'
    elif avg_score >= 60:
        grade = 'B'
    else:
        grade = 'Pass'

    cert_filename = f"cert_{student.student_id_code}_{course.course_code}.pdf".replace('/', '_').replace('-', '_')
    cert_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates', cert_filename)

    if not cert:
        random_cert_code = f"KISS-CERT-2026-{random.randint(10000, 99999)}"
        cert = Certificate(
            certificate_code=random_cert_code,
            student_id=student.id,
            course_id=course.id,
            issue_date=date.today(),
            attendance_percentage=att_stats['percentage'],
            final_score=avg_score,
            grade=grade,
            pdf_filename=cert_filename
        )
        db.session.add(cert)
        # Update enrollment status to completed
        enrollment.status = 'completed'
        db.session.commit()
        log_audit('Certificate Generated', entity_type='Certificate', entity_id=cert.id,
                  details=f'Certificate {cert.certificate_code} issued to {student.student_id_code}')

    # Generate PDF if not yet generated or missing on disk
    trainer_name = course.trainer.full_name if course.trainer else "Vocational Faculty"
    generate_certificate_pdf(
        student_name=student.full_name,
        student_id_code=student.student_id_code,
        course_title=course.title,
        course_code=course.course_code,
        category_name=course.category.name,
        duration_weeks=course.duration_weeks,
        attendance_pct=cert.attendance_percentage,
        final_score=cert.final_score,
        grade=cert.grade,
        certificate_code=cert.certificate_code,
        issue_date_str=cert.issue_date.strftime('%d %B %Y'),
        trainer_name=trainer_name,
        output_filepath=cert_path
    )

    return send_file(
        cert_path,
        as_attachment=True,
        download_name=f"KISS_Certificate_{student.student_id_code}_{course.course_code}.pdf",
        mimetype='application/pdf'
    )
