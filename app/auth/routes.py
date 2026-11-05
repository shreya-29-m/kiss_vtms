import os
import random
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.auth import auth_bp
from app.models import db, User, StudentProfile, TrainerProfile
from app.utils.audit import log_audit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_trainer():
            return redirect(url_for('trainer.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('auth/login.html')

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            log_audit('User Login', entity_type='User', entity_id=user.id, details=f'Successful login by {user.username}')
            flash(f'Welcome back, {user.username}!', 'success')

            # Role redirection
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_trainer():
                return redirect(url_for('trainer.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        academic_level = request.form.get('academic_level', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        skills_and_interests = request.form.get('skills_and_interests', '').strip()

        # Validation
        if not username or not email or not password or not full_name:
            flash('Full Name, Username, Email, and Password are required fields.', 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please login or use another email.', 'danger')
            return render_template('auth/register.html')

        # Generate unique Student ID code e.g., KISS-STU-2026-XXXX
        random_suffix = random.randint(1000, 9999)
        student_id_code = f"KISS-STU-2026-{random_suffix}"
        while StudentProfile.query.filter_by(student_id_code=student_id_code).first():
            random_suffix = random.randint(1000, 9999)
            student_id_code = f"KISS-STU-2026-{random_suffix}"

        # Create user & student profile
        new_user = User(username=username, email=email, role='student')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        student_profile = StudentProfile(
            user_id=new_user.id,
            student_id_code=student_id_code,
            full_name=full_name,
            academic_level=academic_level,
            contact_number=contact_number,
            skills_and_interests=skills_and_interests
        )
        db.session.add(student_profile)
        db.session.commit()

        log_audit('Student Self-Registration', entity_type='User', entity_id=new_user.id,
                  details=f'New student registered: {username} ({student_id_code})', user_id=new_user.id)

        login_user(new_user)
        flash(f'Registration successful! Welcome to KISS Vocational Training Management System. Your Student ID is {student_id_code}.', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_audit('User Logout', entity_type='User', entity_id=current_user.id, details=f'Logout by {current_user.username}')
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    student_profile = current_user.student_profile
    trainer_profile = current_user.trainer_profile

    if request.method == 'POST':
        # Update permitted profile fields
        if current_user.is_student() and student_profile:
            student_profile.full_name = request.form.get('full_name', student_profile.full_name).strip()
            student_profile.academic_level = request.form.get('academic_level', student_profile.academic_level).strip()
            student_profile.contact_number = request.form.get('contact_number', student_profile.contact_number).strip()
            student_profile.educational_qualification = request.form.get('educational_qualification', student_profile.educational_qualification).strip()
            student_profile.skills_and_interests = request.form.get('skills_and_interests', student_profile.skills_and_interests).strip()
            student_profile.previous_training = request.form.get('previous_training', student_profile.previous_training).strip()

            # Handle optional document upload
            if 'document' in request.files:
                file = request.files['document']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(f"doc_{current_user.id}_{file.filename}")
                    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
                    os.makedirs(upload_dir, exist_ok=True)
                    file.save(os.path.join(upload_dir, filename))
                    student_profile.document_filename = filename

            db.session.commit()
            log_audit('Update Profile', entity_type='StudentProfile', entity_id=student_profile.id,
                      details=f'Profile updated by student {student_profile.student_id_code}')
            flash('Your student profile has been updated successfully.', 'success')

        elif current_user.is_trainer() and trainer_profile:
            trainer_profile.full_name = request.form.get('full_name', trainer_profile.full_name).strip()
            trainer_profile.contact_number = request.form.get('contact_number', trainer_profile.contact_number).strip()
            trainer_profile.qualification = request.form.get('qualification', trainer_profile.qualification).strip()
            trainer_profile.department_or_trade = request.form.get('department_or_trade', trainer_profile.department_or_trade).strip()
            trainer_profile.bio = request.form.get('bio', trainer_profile.bio).strip()

            db.session.commit()
            log_audit('Update Profile', entity_type='TrainerProfile', entity_id=trainer_profile.id,
                      details=f'Profile updated by trainer {trainer_profile.trainer_id_code}')
            flash('Your trainer profile has been updated successfully.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', student=student_profile, trainer=trainer_profile)
