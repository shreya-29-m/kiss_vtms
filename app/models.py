from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'trainer', 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 1-to-1 relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    trainer_profile = db.relationship('TrainerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_trainer(self):
        return self.role == 'trainer'

    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    student_id_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    academic_level = db.Column(db.String(50))  # e.g., '+2 Arts', '+3 Science', 'Diploma'
    contact_number = db.Column(db.String(20))
    educational_qualification = db.Column(db.String(100))
    skills_and_interests = db.Column(db.Text)
    previous_training = db.Column(db.Text)
    profile_photo = db.Column(db.String(255))
    document_filename = db.Column(db.String(255))

    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    assessment_results = db.relationship('AssessmentResult', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def get_attendance_stats(self, course_id):
        total = Attendance.query.filter_by(student_id=self.id, course_id=course_id).count()
        if total == 0:
            return {'total': 0, 'present': 0, 'percentage': 0.0}
        present_count = Attendance.query.filter(
            Attendance.student_id == self.id,
            Attendance.course_id == course_id,
            Attendance.status.in_(['present', 'late', 'excused'])
        ).count()
        percentage = round((present_count / total) * 100, 1)
        return {'total': total, 'present': present_count, 'percentage': percentage}

    def get_assessment_stats(self, course_id):
        # All assessments for this course
        assessments = Assessment.query.filter_by(course_id=course_id).all()
        if not assessments:
            return {'count': 0, 'completed': 0, 'average_percentage': 0.0}
        
        assessment_ids = [a.id for a in assessments]
        results = AssessmentResult.query.filter(
            AssessmentResult.student_id == self.id,
            AssessmentResult.assessment_id.in_(assessment_ids)
        ).all()
        
        if not results:
            return {'count': len(assessments), 'completed': 0, 'average_percentage': 0.0}
        
        # Calculate percentage per assessment
        percentages = []
        for r in results:
            if r.assessment.max_marks > 0:
                pct = (r.marks_obtained / r.assessment.max_marks) * 100.0
                percentages.append(pct)
        avg_pct = round(sum(percentages) / len(percentages), 1) if percentages else 0.0
        return {'count': len(assessments), 'completed': len(results), 'average_percentage': avg_pct}

    def is_eligible_for_certificate(self, course):
        att_stats = self.get_attendance_stats(course.id)
        ass_stats = self.get_assessment_stats(course.id)
        
        # Must have completed all assessments if assessments exist
        assessments_count = Assessment.query.filter_by(course_id=course.id).count()
        if assessments_count > 0 and ass_stats['completed'] < assessments_count:
            return False, "Not all course assessments have been completed and evaluated."
            
        # Attendance condition
        if att_stats['total'] > 0 and att_stats['percentage'] < course.attendance_requirement:
            return False, f"Attendance is {att_stats['percentage']}%, which is below the required {course.attendance_requirement}%."
            
        # Score condition
        if assessments_count > 0 and ass_stats['average_percentage'] < course.passing_score:
            return False, f"Assessment score average is {ass_stats['average_percentage']}%, below passing threshold {course.passing_score}%."
            
        # If no attendance or assessment was recorded yet
        if att_stats['total'] == 0:
            return False, "No attendance sessions have been conducted yet."
            
        return True, "Eligible for certificate"


class TrainerProfile(db.Model):
    __tablename__ = 'trainer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    trainer_id_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    department_or_trade = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    qualification = db.Column(db.String(100))
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)

    assigned_courses = db.relationship('Course', backref='trainer', lazy='dynamic')

    def __repr__(self):
        return f'<Trainer {self.full_name} ({self.trainer_id_code})>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses = db.relationship('Course', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_covered = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer, default=8, nullable=False)
    eligibility_criteria = db.Column(db.String(200), default='Open to all KISS students')
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer_profiles.id'), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    training_schedule = db.Column(db.String(100), nullable=False)  # e.g., 'Mon, Wed, Fri 10:00 AM - 12:00 PM'
    max_seats = db.Column(db.Integer, default=30, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # 'active', 'inactive', 'completed'
    assessment_method = db.Column(db.String(100), default='Practical Assignments & Practical Exam')
    attendance_requirement = db.Column(db.Float, default=75.0, nullable=False)
    passing_score = db.Column(db.Float, default=50.0, nullable=False)
    certificate_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    schedules = db.relationship('SessionSchedule', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    materials = db.relationship('LearningMaterial', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='course', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def enrolled_count(self):
        return Enrollment.query.filter_by(course_id=self.id, status='enrolled').count()

    @property
    def available_seats(self):
        return max(0, self.max_seats - self.enrolled_count)

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_seats

    def __repr__(self):
        return f'<Course {self.course_code}: {self.title}>'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='enrolled', nullable=False)  # 'enrolled', 'completed', 'cancelled'

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uq_student_course_enrollment'),
    )

    def __repr__(self):
        return f'<Enrollment Student:{self.student_id} Course:{self.course_id}>'


class SessionSchedule(db.Model):
    __tablename__ = 'session_schedules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    room_or_lab = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SessionSchedule {self.course_id} on {self.session_date}: {self.topic}>'


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='present', nullable=False)  # 'present', 'absent', 'late', 'excused'
    remarks = db.Column(db.String(200))
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'student_id', 'attendance_date', name='uq_course_student_date_att'),
    )

    def __repr__(self):
        return f'<Attendance Course:{self.course_id} Student:{self.student_id} Date:{self.attendance_date} Status:{self.status}>'


class LearningMaterial(db.Model):
    __tablename__ = 'learning_materials'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    material_type = db.Column(db.String(50), default='notes', nullable=False)  # 'notes', 'guide', 'assignment', 'syllabus'
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship('User', foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f'<LearningMaterial {self.title}>'


class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    assessment_type = db.Column(db.String(50), default='practical', nullable=False)  # 'practical', 'project', 'quiz', 'theory'
    max_marks = db.Column(db.Float, default=100.0, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('AssessmentResult', backref='assessment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assessment {self.title} Max:{self.max_marks}>'


class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text)
    evaluated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    evaluator = db.relationship('User', foreign_keys=[evaluated_by_id])

    __table_args__ = (
        db.UniqueConstraint('assessment_id', 'student_id', name='uq_assessment_student_result'),
    )

    @property
    def percentage(self):
        if self.assessment and self.assessment.max_marks > 0:
            return round((self.marks_obtained / self.assessment.max_marks) * 100, 1)
        return 0.0

    def __repr__(self):
        return f'<AssessmentResult Student:{self.student_id} Score:{self.marks_obtained}>'


class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    certificate_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    issue_date = db.Column(db.Date, default=date.today, nullable=False)
    attendance_percentage = db.Column(db.Float, nullable=False)
    final_score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(10), default='Pass', nullable=False)
    issued_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    pdf_filename = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=True, nullable=False)

    admin_issuer = db.relationship('User', foreign_keys=[issued_by_admin_id])

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uq_student_course_certificate'),
    )

    def __repr__(self):
        return f'<Certificate {self.certificate_code} for Student {self.student_id}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type} at {self.timestamp}>'
