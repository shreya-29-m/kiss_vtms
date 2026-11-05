from datetime import date, timedelta
from app.models import Attendance, Enrollment, StudentProfile, db

def test_record_attendance_and_calculate_percentage(client, init_database, app):
    # Enroll student 1
    with app.app_context():
        st1 = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        st1_id = st1.id
        course_id = init_database['course'].id
        enr = Enrollment(student_id=st1_id, course_id=course_id, status='enrolled')
        db.session.add(enr)
        db.session.commit()

    # Log in as trainer
    client.post('/auth/login', data={'username': 'trainer_test', 'password': 'Trainer@12345'})

    # Record attendance for date 1 (Present)
    d1 = date.today() - timedelta(days=2)
    client.post(f'/trainer/courses/{course_id}/attendance', data={
        'attendance_date': d1.strftime('%Y-%m-%d'),
        f'status_{st1_id}': 'present',
        f'remarks_{st1_id}': 'On time'
    }, follow_redirects=True)

    # Record attendance for date 2 (Absent)
    d2 = date.today() - timedelta(days=1)
    client.post(f'/trainer/courses/{course_id}/attendance', data={
        'attendance_date': d2.strftime('%Y-%m-%d'),
        f'status_{st1_id}': 'absent',
        f'remarks_{st1_id}': 'Sick leave'
    }, follow_redirects=True)

    # Verify calculations in database
    with app.app_context():
        st_profile = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        stats = st_profile.get_attendance_stats(course_id)
        assert stats['total'] == 2
        assert stats['present'] == 1
        assert stats['percentage'] == 50.0

def test_attendance_correction_updates_percentage(client, init_database, app):
    with app.app_context():
        st1 = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        st1_id = st1.id
        course_id = init_database['course'].id
        enr = Enrollment(student_id=st1_id, course_id=course_id, status='enrolled')
        db.session.add(enr)
        db.session.commit()

    client.post('/auth/login', data={'username': 'trainer_test', 'password': 'Trainer@12345'})
    target_date = date.today().strftime('%Y-%m-%d')

    # Initially mark absent
    client.post(f'/trainer/courses/{course_id}/attendance', data={
        'attendance_date': target_date,
        f'status_{st1_id}': 'absent',
        f'remarks_{st1_id}': 'Absent initially'
    })

    # Correct to present
    client.post(f'/trainer/courses/{course_id}/attendance', data={
        'attendance_date': target_date,
        f'status_{st1_id}': 'present',
        f'remarks_{st1_id}': 'Corrected upon proof'
    })

    with app.app_context():
        st_profile = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        stats = st_profile.get_attendance_stats(course_id)
        assert stats['total'] == 1
        assert stats['present'] == 1
        assert stats['percentage'] == 100.0
