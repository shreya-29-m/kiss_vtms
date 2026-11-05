import csv
import io
import random
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request, Response, abort
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import (
    db, User, StudentProfile, TrainerProfile, Category, Course,
    Enrollment, Attendance, Assessment, AssessmentResult, Certificate, AuditLog
)
from app.utils.decorators import role_required
from app.utils.audit import log_audit

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    stats = {
        'total_courses': Course.query.count(),
        'active_courses': Course.query.filter_by(status='active').count(),
        'total_categories': Category.query.count(),
        'total_students': StudentProfile.query.count(),
        'total_trainers': TrainerProfile.query.count(),
        'total_enrollments': Enrollment.query.count(),
        'active_enrollments': Enrollment.query.filter_by(status='enrolled').count(),
        'total_certificates': Certificate.query.count(),
    }

    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
    recent_enrollments = Enrollment.query.order_by(Enrollment.enrolled_at.desc()).limit(6).all()
    recent_certificates = Certificate.query.order_by(Certificate.issue_date.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_logs=recent_logs,
        recent_enrollments=recent_enrollments,
        recent_certificates=recent_certificates
    )


# --- CATEGORIES MANAGEMENT ---
@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = bool(request.form.get('is_active'))

        if not name:
            flash('Category name is required.', 'warning')
            return redirect(url_for('admin.categories'))

        if Category.query.filter_by(name=name).first():
            flash('A category with this name already exists.', 'danger')
            return redirect(url_for('admin.categories'))

        new_cat = Category(name=name, description=description, is_active=is_active)
        db.session.add(new_cat)
        db.session.commit()

        log_audit('Create Category', entity_type='Category', entity_id=new_cat.id,
                  details=f'Created training category: {name}')
        flash(f'Category "{name}" created successfully.', 'success')
        return redirect(url_for('admin.categories'))

    all_categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/categories.html', categories=all_categories)


@admin_bp.route('/categories/<int:category_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_category(category_id):
    cat = Category.query.get_or_404(category_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    status_str = "activated" if cat.is_active else "deactivated"
    log_audit('Toggle Category Status', entity_type='Category', entity_id=cat.id,
              details=f'Category "{cat.name}" {status_str}')
    flash(f'Category "{cat.name}" has been {status_str}.', 'info')
    return redirect(url_for('admin.categories'))


# --- COURSES MANAGEMENT ---
@admin_bp.route('/courses')
@login_required
@role_required('admin')
def courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=all_courses)


@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_course():
    if request.method == 'POST':
        course_code = request.form.get('course_code', '').strip().upper()
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        skills_covered = request.form.get('skills_covered', '').strip()
        duration_weeks = request.form.get('duration_weeks', 8, type=int)
        eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
        trainer_id = request.form.get('trainer_id', type=int) or None
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        training_schedule = request.form.get('training_schedule', '').strip()
        max_seats = request.form.get('max_seats', 30, type=int)
        status = request.form.get('status', 'active')
        assessment_method = request.form.get('assessment_method', 'Practical Project & Theory Exam')
        attendance_req = request.form.get('attendance_requirement', 75.0, type=float)
        pass_score = request.form.get('passing_score', 50.0, type=float)
        cert_available = bool(request.form.get('certificate_available'))

        # Validation
        if not course_code or not title or not category_id or not start_date_str or not end_date_str:
            flash('Course Code, Title, Category, Start Date, and End Date are required.', 'warning')
            return redirect(url_for('admin.create_course'))

        if Course.query.filter_by(course_code=course_code).first():
            flash(f'Course code "{course_code}" is already in use.', 'danger')
            return redirect(url_for('admin.create_course'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid start or end date format.', 'danger')
            return redirect(url_for('admin.create_course'))

        if end_date <= start_date:
            flash('Course end date must be after the start date.', 'danger')
            return redirect(url_for('admin.create_course'))

        new_course = Course(
            course_code=course_code,
            title=title,
            category_id=category_id,
            description=description,
            skills_covered=skills_covered,
            duration_weeks=duration_weeks,
            eligibility_criteria=eligibility_criteria,
            trainer_id=trainer_id,
            start_date=start_date,
            end_date=end_date,
            training_schedule=training_schedule,
            max_seats=max_seats,
            status=status,
            assessment_method=assessment_method,
            attendance_requirement=attendance_req,
            passing_score=pass_score,
            certificate_available=cert_available
        )
        db.session.add(new_course)
        db.session.commit()

        log_audit('Create Course', entity_type='Course', entity_id=new_course.id,
                  details=f'Created course: {title} ({course_code})')
        flash(f'Course "{title}" created successfully.', 'success')
        return redirect(url_for('admin.courses'))

    categories = Category.query.filter_by(is_active=True).all()
    trainers = TrainerProfile.query.all()
    return render_template('admin/course_form.html', course=None, categories=categories, trainers=trainers)


@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        course.title = request.form.get('title', course.title).strip()
        course.category_id = request.form.get('category_id', course.category_id, type=int)
        course.description = request.form.get('description', course.description).strip()
        course.skills_covered = request.form.get('skills_covered', course.skills_covered).strip()
        course.duration_weeks = request.form.get('duration_weeks', course.duration_weeks, type=int)
        course.eligibility_criteria = request.form.get('eligibility_criteria', course.eligibility_criteria).strip()
        course.trainer_id = request.form.get('trainer_id', type=int) or None
        course.training_schedule = request.form.get('training_schedule', course.training_schedule).strip()
        course.max_seats = request.form.get('max_seats', course.max_seats, type=int)
        course.status = request.form.get('status', course.status)
        course.assessment_method = request.form.get('assessment_method', course.assessment_method)
        course.attendance_requirement = request.form.get('attendance_requirement', course.attendance_requirement, type=float)
        course.passing_score = request.form.get('passing_score', course.passing_score, type=float)
        course.certificate_available = bool(request.form.get('certificate_available'))

        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        if start_date_str and end_date_str:
            try:
                course.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                course.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        db.session.commit()
        log_audit('Update Course', entity_type='Course', entity_id=course.id,
                  details=f'Updated course: {course.title} ({course.course_code})')
        flash(f'Course "{course.title}" updated successfully.', 'success')
        return redirect(url_for('admin.courses'))

    categories = Category.query.all()
    trainers = TrainerProfile.query.all()
    return render_template('admin/course_form.html', course=course, categories=categories, trainers=trainers)


@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    course_name = course.title
    db.session.delete(course)
    db.session.commit()
    log_audit('Delete Course', entity_type='Course', entity_id=course_id, details=f'Deleted course: {course_name}')
    flash(f'Course "{course_name}" and its associated records have been removed.', 'info')
    return redirect(url_for('admin.courses'))


# --- USERS MANAGEMENT ---
@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    role_filter = request.args.get('role', '')
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users, current_filter=role_filter)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        full_name = request.form.get('full_name', '').strip()

        if not username or not email or not password or not full_name:
            flash('Username, Email, Password, and Full Name are required.', 'warning')
            return redirect(url_for('admin.create_user'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('A user with this username or email already exists.', 'danger')
            return redirect(url_for('admin.create_user'))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        if role == 'student':
            student_id = f"KISS-STU-2026-{random.randint(1000, 9999)}"
            student_profile = StudentProfile(
                user_id=new_user.id,
                student_id_code=student_id,
                full_name=full_name,
                academic_level=request.form.get('academic_level', '+2 Arts'),
                contact_number=request.form.get('contact_number', ''),
                educational_qualification=request.form.get('qualification', '')
            )
            db.session.add(student_profile)
        elif role == 'trainer':
            trainer_id = f"KISS-TRN-{random.randint(100, 999)}"
            trainer_profile = TrainerProfile(
                user_id=new_user.id,
                trainer_id_code=trainer_id,
                full_name=full_name,
                department_or_trade=request.form.get('department_or_trade', 'Vocational Training'),
                contact_number=request.form.get('contact_number', ''),
                qualification=request.form.get('qualification', ''),
                experience_years=request.form.get('experience_years', 2, type=int)
            )
            db.session.add(trainer_profile)

        db.session.commit()
        log_audit('Create User', entity_type='User', entity_id=new_user.id,
                  details=f'Admin created user {username} with role {role}')
        flash(f'User "{username}" created successfully as {role.capitalize()}.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html')


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    if user_id == current_user.id:
        flash('You cannot deactivate your own administrative account.', 'warning')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    log_audit('Toggle User Status', entity_type='User', entity_id=user.id, details=f'User {user.username} {status_str}')
    flash(f'User "{user.username}" has been {status_str}.', 'info')
    return redirect(url_for('admin.users'))


# --- ENROLLMENTS MANAGEMENT ---
@admin_bp.route('/enrollments')
@login_required
@role_required('admin')
def enrollments():
    course_id = request.args.get('course_id', type=int)
    status_filter = request.args.get('status', '')

    query = Enrollment.query
    if course_id:
        query = query.filter_by(course_id=course_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    all_enrollments = query.order_by(Enrollment.enrolled_at.desc()).all()
    courses = Course.query.all()
    return render_template('admin/enrollments.html', enrollments=all_enrollments, courses=courses, selected_course=course_id)


@admin_bp.route('/enrollments/<int:enrollment_id>/status', methods=['POST'])
@login_required
@role_required('admin')
def update_enrollment_status(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    new_status = request.form.get('status', 'enrolled')
    if new_status in ['enrolled', 'completed', 'cancelled']:
        enrollment.status = new_status
        db.session.commit()
        log_audit('Update Enrollment Status', entity_type='Enrollment', entity_id=enrollment.id,
                  details=f'Enrollment status for student {enrollment.student.student_id_code} changed to {new_status}')
        flash('Enrollment status updated.', 'success')
    return redirect(url_for('admin.enrollments'))


# --- AUDIT LOGS ---
@admin_bp.route('/audit-logs')
@login_required
@role_required('admin')
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs)


# --- REPORTS & EXPORT ---
@admin_bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    categories = Category.query.all()
    courses = Course.query.all()

    category_stats = []
    for cat in categories:
        cat_courses = Course.query.filter_by(category_id=cat.id).all()
        course_ids = [c.id for c in cat_courses]
        enrollment_count = Enrollment.query.filter(Enrollment.course_id.in_(course_ids) if course_ids else False).count()
        cert_count = Certificate.query.filter(Certificate.course_id.in_(course_ids) if course_ids else False).count()
        category_stats.append({
            'category': cat,
            'course_count': len(cat_courses),
            'enrollment_count': enrollment_count,
            'certificate_count': cert_count
        })

    # Summary metrics
    total_enrollments = Enrollment.query.count()
    total_certs = Certificate.query.count()
    overall_completion_rate = round((total_certs / total_enrollments * 100), 1) if total_enrollments > 0 else 0.0

    return render_template(
        'admin/reports.html',
        category_stats=category_stats,
        courses=courses,
        total_enrollments=total_enrollments,
        total_certs=total_certs,
        overall_completion_rate=overall_completion_rate
    )


@admin_bp.route('/reports/export-csv')
@login_required
@role_required('admin')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Enrollment ID', 'Student ID', 'Student Name', 'Academic Level',
        'Course Code', 'Course Title', 'Category', 'Enrolled Date',
        'Attendance %', 'Assessment Avg %', 'Status', 'Certificate Issued'
    ])

    enrollments = Enrollment.query.all()
    for enr in enrollments:
        att = enr.student.get_attendance_stats(enr.course_id)
        ass = enr.student.get_assessment_stats(enr.course_id)
        has_cert = Certificate.query.filter_by(student_id=enr.student_id, course_id=enr.course_id).first() is not None
        writer.writerow([
            enr.id,
            enr.student.student_id_code,
            enr.student.full_name,
            enr.student.academic_level or 'N/A',
            enr.course.course_code,
            enr.course.title,
            enr.course.category.name,
            enr.enrolled_at.strftime('%Y-%m-%d'),
            att['percentage'],
            ass['average_percentage'],
            enr.status,
            'Yes' if has_cert else 'No'
        ])

    output.seek(0)
    log_audit('Export CSV Report', entity_type='Report', details='Admin exported system enrollments CSV')
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=kiss_vtms_enrollment_report_{date.today()}.csv"}
    )
