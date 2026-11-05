import os
from datetime import date, datetime
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.trainer import trainer_bp
from app.models import (
    db, Course, Enrollment, SessionSchedule, Attendance,
    LearningMaterial, Assessment, AssessmentResult, StudentProfile
)
from app.utils.decorators import role_required
from app.utils.audit import log_audit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@trainer_bp.route('/dashboard')
@login_required
@role_required('trainer')
def dashboard():
    trainer = current_user.trainer_profile
    if not trainer:
        flash('Trainer profile not configured. Contact admin.', 'danger')
        return redirect(url_for('auth.logout'))

    courses = Course.query.filter_by(trainer_id=trainer.id).all()
    course_ids = [c.id for c in courses]

    total_courses = len(courses)
    total_students = Enrollment.query.filter(
        Enrollment.course_id.in_(course_ids) if course_ids else False,
        Enrollment.status.in_(['enrolled', 'completed'])
    ).count()

    total_sessions = SessionSchedule.query.filter(
        SessionSchedule.course_id.in_(course_ids) if course_ids else False
    ).count()

    total_assessments = Assessment.query.filter(
        Assessment.course_id.in_(course_ids) if course_ids else False
    ).count()

    # Upcoming sessions for trainer
    upcoming_sessions = SessionSchedule.query.filter(
        SessionSchedule.course_id.in_(course_ids) if course_ids else False,
        SessionSchedule.session_date >= date.today()
    ).order_by(SessionSchedule.session_date.asc()).limit(5).all()

    return render_template(
        'trainer/dashboard.html',
        trainer=trainer,
        courses=courses,
        total_courses=total_courses,
        total_students=total_students,
        total_sessions=total_sessions,
        total_assessments=total_assessments,
        upcoming_sessions=upcoming_sessions
    )


@trainer_bp.route('/courses')
@login_required
@role_required('trainer')
def courses():
    trainer = current_user.trainer_profile
    assigned_courses = Course.query.filter_by(trainer_id=trainer.id).order_by(Course.created_at.desc()).all()
    return render_template('trainer/courses.html', courses=assigned_courses)


@trainer_bp.route('/courses/<int:course_id>')
@login_required
@role_required('trainer')
def course_detail(course_id):
    trainer = current_user.trainer_profile
    course = Course.query.filter_by(id=course_id, trainer_id=trainer.id).first_or_404()

    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    schedules = SessionSchedule.query.filter_by(course_id=course.id).order_by(SessionSchedule.session_date.asc()).all()
    assessments = Assessment.query.filter_by(course_id=course.id).order_by(Assessment.created_at.desc()).all()
    materials = LearningMaterial.query.filter_by(course_id=course.id).order_by(LearningMaterial.uploaded_at.desc()).all()

    # Calculate student metrics
    student_metrics = []
    for enr in enrollments:
        att = enr.student.get_attendance_stats(course.id)
        ass = enr.student.get_assessment_stats(course.id)
        eligible, reason = enr.student.is_eligible_for_certificate(course)
        student_metrics.append({
            'student': enr.student,
            'enrollment': enr,
            'attendance': att,
            'assessment': ass,
            'eligible': eligible,
            'reason': reason
        })

    return render_template(
        'trainer/course_detail.html',
        course=course,
        student_metrics=student_metrics,
        schedules=schedules,
        assessments=assessments,
        materials=materials
    )


@trainer_bp.route('/courses/<int:course_id>/schedule/add', methods=['POST'])
@login_required
@role_required('trainer')
def add_schedule(course_id):
    trainer = current_user.trainer_profile
    course = Course.query.filter_by(id=course_id, trainer_id=trainer.id).first_or_404()

    session_date_str = request.form.get('session_date')
    start_time = request.form.get('start_time', '').strip()
    end_time = request.form.get('end_time', '').strip()
    topic = request.form.get('topic', '').strip()
    room_or_lab = request.form.get('room_or_lab', '').strip()

    if not session_date_str or not start_time or not topic:
        flash('Date, Start Time, and Topic are required.', 'warning')
        return redirect(url_for('trainer.course_detail', course_id=course.id))

    try:
        session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('trainer.course_detail', course_id=course.id))

    schedule_item = SessionSchedule(
        course_id=course.id,
        session_date=session_date,
        start_time=start_time,
        end_time=end_time,
        topic=topic,
        room_or_lab=room_or_lab
    )
    db.session.add(schedule_item)
    db.session.commit()

    log_audit('Add Session Schedule', entity_type='SessionSchedule', entity_id=schedule_item.id,
              details=f'New session scheduled for {course.course_code} on {session_date}')
    flash('Training session added to schedule.', 'success')
    return redirect(url_for('trainer.course_detail', course_id=course.id))


@trainer_bp.route('/courses/<int:course_id>/attendance', methods=['GET', 'POST'])
@login_required
@role_required('trainer')
def attendance(course_id):
    trainer = current_user.trainer_profile
    course = Course.query.filter_by(id=course_id, trainer_id=trainer.id).first_or_404()
    enrollments = Enrollment.query.filter_by(course_id=course.id, status='enrolled').all()

    # Selected date
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        att_date = date.today()

    if request.method == 'POST':
        # Batch record attendance
        target_date_str = request.form.get('attendance_date')
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            target_date = att_date

        for enr in enrollments:
            status_val = request.form.get(f'status_{enr.student.id}', 'present')
            remarks_val = request.form.get(f'remarks_{enr.student.id}', '').strip()

            existing_record = Attendance.query.filter_by(
                course_id=course.id,
                student_id=enr.student.id,
                attendance_date=target_date
            ).first()

            if existing_record:
                existing_record.status = status_val
                existing_record.remarks = remarks_val
                existing_record.recorded_by_id = current_user.id
                existing_record.recorded_at = datetime.utcnow()
            else:
                att_record = Attendance(
                    course_id=course.id,
                    student_id=enr.student.id,
                    attendance_date=target_date,
                    status=status_val,
                    remarks=remarks_val,
                    recorded_by_id=current_user.id
                )
                db.session.add(att_record)

        db.session.commit()
        log_audit('Record Attendance', entity_type='Course', entity_id=course.id,
                  details=f'Attendance recorded for {len(enrollments)} students on {target_date}')
        flash(f'Attendance recorded successfully for {target_date.strftime("%d %B %Y")}.', 'success')
        return redirect(url_for('trainer.attendance', course_id=course.id, date=target_date.strftime('%Y-%m-%d')))

    # Existing records for selected date
    existing_records = {
        a.student_id: a for a in Attendance.query.filter_by(course_id=course.id, attendance_date=att_date).all()
    }

    # Distinct dates with recorded attendance
    recorded_dates = db.session.query(Attendance.attendance_date).filter_by(course_id=course.id).distinct().order_by(Attendance.attendance_date.desc()).all()
    distinct_dates = [d[0] for d in recorded_dates]

    return render_template(
        'trainer/attendance.html',
        course=course,
        enrollments=enrollments,
        selected_date=att_date,
        existing_records=existing_records,
        distinct_dates=distinct_dates
    )


@trainer_bp.route('/courses/<int:course_id>/materials', methods=['GET', 'POST'])
@login_required
@role_required('trainer')
def materials(course_id):
    trainer = current_user.trainer_profile
    course = Course.query.filter_by(id=course_id, trainer_id=trainer.id).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        material_type = request.form.get('material_type', 'notes')
        description = request.form.get('description', '').strip()
        link_url = request.form.get('link_url', '').strip()

        if not title:
            flash('Title is required for learning materials.', 'warning')
            return redirect(url_for('trainer.materials', course_id=course.id))

        saved_filename = None
        if 'material_file' in request.files:
            file = request.files['material_file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"mat_{course.id}_{file.filename}")
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'materials')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                saved_filename = filename

        material = LearningMaterial(
            course_id=course.id,
            title=title,
            material_type=material_type,
            description=description,
            file_path=saved_filename,
            link_url=link_url,
            uploaded_by_id=current_user.id
        )
        db.session.add(material)
        db.session.commit()

        log_audit('Upload Learning Material', entity_type='LearningMaterial', entity_id=material.id,
                  details=f'Uploaded material "{title}" for course {course.course_code}')
        flash('Learning material uploaded successfully.', 'success')
        return redirect(url_for('trainer.materials', course_id=course.id))

    materials_list = LearningMaterial.query.filter_by(course_id=course.id).order_by(LearningMaterial.uploaded_at.desc()).all()
    return render_template('trainer/materials.html', course=course, materials=materials_list)


@trainer_bp.route('/courses/<int:course_id>/assessments', methods=['GET', 'POST'])
@login_required
@role_required('trainer')
def assessments(course_id):
    trainer = current_user.trainer_profile
    course = Course.query.filter_by(id=course_id, trainer_id=trainer.id).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        assessment_type = request.form.get('assessment_type', 'practical')
        max_marks = request.form.get('max_marks', 100, type=float)
        due_date_str = request.form.get('due_date')
        description = request.form.get('description', '').strip()

        if not title:
            flash('Assessment title is required.', 'warning')
            return redirect(url_for('trainer.assessments', course_id=course.id))

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        new_ass = Assessment(
            course_id=course.id,
            title=title,
            assessment_type=assessment_type,
            max_marks=max_marks,
            due_date=due_date,
            description=description
        )
        db.session.add(new_ass)
        db.session.commit()

        log_audit('Create Assessment', entity_type='Assessment', entity_id=new_ass.id,
                  details=f'Created assessment "{title}" for {course.course_code}')
        flash('Assessment created successfully.', 'success')
        return redirect(url_for('trainer.assessments', course_id=course.id))

    assessments_list = Assessment.query.filter_by(course_id=course.id).order_by(Assessment.created_at.desc()).all()
    return render_template('trainer/assessments.html', course=course, assessments=assessments_list)


@trainer_bp.route('/assessments/<int:assessment_id>/grade', methods=['GET', 'POST'])
@login_required
@role_required('trainer')
def grade_assessment(assessment_id):
    trainer = current_user.trainer_profile
    assessment = Assessment.query.get_or_404(assessment_id)
    course = Course.query.filter_by(id=assessment.course_id, trainer_id=trainer.id).first_or_404()

    enrollments = Enrollment.query.filter_by(course_id=course.id).all()

    if request.method == 'POST':
        for enr in enrollments:
            score_str = request.form.get(f'score_{enr.student.id}')
            feedback_val = request.form.get(f'feedback_{enr.student.id}', '').strip()

            if score_str is not None and score_str != '':
                try:
                    score = float(score_str)
                    if score < 0 or score > assessment.max_marks:
                        flash(f'Score for {enr.student.full_name} must be between 0 and {assessment.max_marks}.', 'warning')
                        continue

                    existing_res = AssessmentResult.query.filter_by(
                        assessment_id=assessment.id,
                        student_id=enr.student.id
                    ).first()

                    if existing_res:
                        existing_res.marks_obtained = score
                        existing_res.feedback = feedback_val
                        existing_res.evaluated_by_id = current_user.id
                        existing_res.evaluated_at = datetime.utcnow()
                    else:
                        new_res = AssessmentResult(
                            assessment_id=assessment.id,
                            student_id=enr.student.id,
                            marks_obtained=score,
                            feedback=feedback_val,
                            evaluated_by_id=current_user.id
                        )
                        db.session.add(new_res)
                except ValueError:
                    continue

        db.session.commit()
        log_audit('Grade Assessment', entity_type='Assessment', entity_id=assessment.id,
                  details=f'Evaluation saved for assessment "{assessment.title}"')
        flash('Assessment marks and feedback updated successfully.', 'success')
        return redirect(url_for('trainer.grade_assessment', assessment_id=assessment.id))

    # Existing results
    existing_results = {
        r.student_id: r for r in AssessmentResult.query.filter_by(assessment_id=assessment.id).all()
    }

    return render_template(
        'trainer/assessment_grade.html',
        course=course,
        assessment=assessment,
        enrollments=enrollments,
        existing_results=existing_results
    )


@trainer_bp.route('/courses/<int:course_id>/reports')
@login_required
@role_required('trainer')
def course_report(course_id):
    trainer = current_user.trainer_profile
    course = Course.query.filter_by(id=course_id, trainer_id=trainer.id).first_or_404()
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()

    report_data = []
    for enr in enrollments:
        att = enr.student.get_attendance_stats(course.id)
        ass = enr.student.get_assessment_stats(course.id)
        eligible, reason = enr.student.is_eligible_for_certificate(course)
        report_data.append({
            'student': enr.student,
            'attendance': att,
            'assessment': ass,
            'eligible': eligible,
            'reason': reason,
            'status': enr.status
        })

    return render_template('trainer/reports.html', course=course, report_data=report_data)
