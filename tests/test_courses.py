from datetime import date, timedelta
from app.models import Course, Enrollment, Category, StudentProfile, User, db

def test_admin_create_course(client, init_database):
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@12345'})
    response = client.post('/admin/courses/create', data={
        'course_code': 'VT-NEW-999',
        'title': 'Solar Panel Repair & Maintenance',
        'category_id': init_database['category'].id,
        'description': 'Comprehensive hands-on training on solar rooftop cells and inverter maintenance.',
        'skills_covered': 'Inverter diagnostics, solar mounting',
        'duration_weeks': 6,
        'start_date': date.today().strftime('%Y-%m-%d'),
        'end_date': (date.today() + timedelta(days=42)).strftime('%Y-%m-%d'),
        'training_schedule': 'Tue, Thu 10:00 AM',
        'max_seats': 20,
        'status': 'active',
        'attendance_requirement': 75.0,
        'passing_score': 50.0,
        'certificate_available': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Solar Panel Repair &amp; Maintenance' in response.data or b'Solar Panel Repair' in response.data

def test_student_enrollment_success(client, init_database):
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    course_id = init_database['course'].id
    response = client.post(f'/student/courses/{course_id}/enroll', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have successfully enrolled' in response.data

def test_duplicate_enrollment_prevention(client, init_database):
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    course_id = init_database['course'].id
    # First enrollment
    client.post(f'/student/courses/{course_id}/enroll')
    # Second enrollment attempt
    response = client.post(f'/student/courses/{course_id}/enroll', follow_redirects=True)
    assert response.status_code == 200
    assert b'already enrolled' in response.data

def test_seat_capacity_limit_enforcement(client, init_database, app):
    # Course max_seats is 2.
    # Enroll student 1
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    client.post(f"/student/courses/{init_database['course'].id}/enroll")
    client.get('/auth/logout')

    # Enroll student 2
    client.post('/auth/login', data={'username': 'student_test2', 'password': 'Student@12345'})
    client.post(f"/student/courses/{init_database['course'].id}/enroll")
    client.get('/auth/logout')

    # Register and try to enroll student 3
    with app.app_context():
        u3 = User(username='student_test3', email='student3@kiss.ac.in', role='student')
        u3.set_password('Student@12345')
        db.session.add(u3)
        db.session.flush()
        sp3 = StudentProfile(user_id=u3.id, student_id_code='TEST-STU-03', full_name='Student Three')
        db.session.add(sp3)
        db.session.commit()

    client.post('/auth/login', data={'username': 'student_test3', 'password': 'Student@12345'})
    response = client.post(f"/student/courses/{init_database['course'].id}/enroll", follow_redirects=True)
    assert response.status_code == 200
    assert b'reached its maximum capacity' in response.data or b'capacity' in response.data.lower()

def test_admin_category_toggle(client, init_database):
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@12345'})
    cat_id = init_database['category'].id
    response = client.post(f'/admin/categories/{cat_id}/toggle', follow_redirects=True)
    assert response.status_code == 200
    assert b'deactivated' in response.data or b'activated' in response.data
