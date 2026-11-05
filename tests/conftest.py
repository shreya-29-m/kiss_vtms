import pytest
from datetime import date, timedelta
from app import create_app
from app.config import TestConfig
from app.models import (
    db, User, StudentProfile, TrainerProfile, Category, Course,
    Enrollment, Attendance, Assessment, AssessmentResult, Certificate
)

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        # Admin
        admin = User(username='admin_test', email='admintest@kiss.ac.in', role='admin')
        admin.set_password('Admin@12345')
        db.session.add(admin)

        # Trainer
        trainer_user = User(username='trainer_test', email='trainertest@kiss.ac.in', role='trainer')
        trainer_user.set_password('Trainer@12345')
        db.session.add(trainer_user)
        db.session.flush()

        trainer_profile = TrainerProfile(
            user_id=trainer_user.id,
            trainer_id_code='TEST-TRN-01',
            full_name='Trainer Test Faculty',
            department_or_trade='Computer & IT',
            qualification='M.Tech',
            experience_years=5
        )
        db.session.add(trainer_profile)

        # Student 1
        student_user1 = User(username='student_test1', email='studenttest1@kiss.ac.in', role='student')
        student_user1.set_password('Student@12345')
        db.session.add(student_user1)
        db.session.flush()

        student_profile1 = StudentProfile(
            user_id=student_user1.id,
            student_id_code='TEST-STU-01',
            full_name='Student One',
            academic_level='+2 Science'
        )
        db.session.add(student_profile1)

        # Student 2
        student_user2 = User(username='student_test2', email='studenttest2@kiss.ac.in', role='student')
        student_user2.set_password('Student@12345')
        db.session.add(student_user2)
        db.session.flush()

        student_profile2 = StudentProfile(
            user_id=student_user2.id,
            student_id_code='TEST-STU-02',
            full_name='Student Two',
            academic_level='+2 Arts'
        )
        db.session.add(student_profile2)

        # Category
        category = Category(name='Information Technology', description='Computer skills', is_active=True)
        db.session.add(category)
        db.session.flush()

        # Course
        course = Course(
            course_code='TEST-IT-101',
            title='Test Computer Hardware Course',
            category_id=category.id,
            trainer_id=trainer_profile.id,
            description='Test course description for verification.',
            skills_covered='Hardware assembly, networking',
            duration_weeks=4,
            training_schedule='Mon, Wed 10 AM',
            max_seats=2,  # Low capacity to easily test capacity limit
            status='active',
            attendance_requirement=75.0,
            passing_score=50.0,
            certificate_available=True,
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() + timedelta(days=10)
        )
        db.session.add(course)
        db.session.commit()

        yield {
            'admin': admin,
            'trainer': trainer_user,
            'student1': student_user1,
            'student2': student_user2,
            'course': course,
            'category': category
        }
