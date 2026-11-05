from app.models import Assessment, AssessmentResult, Enrollment, StudentProfile, db

def test_trainer_create_assessment_and_grade(client, init_database, app):
    # Enroll student
    with app.app_context():
        st1 = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        st1_id = st1.id
        course_id = init_database['course'].id
        db.session.add(Enrollment(student_id=st1_id, course_id=course_id, status='enrolled'))
        db.session.commit()

    # Log in as trainer
    client.post('/auth/login', data={'username': 'trainer_test', 'password': 'Trainer@12345'})

    # Create assessment
    res = client.post(f'/trainer/courses/{course_id}/assessments', data={
        'title': 'Test Practical Exam',
        'assessment_type': 'practical',
        'max_marks': '100',
        'description': 'Practical test on hardware'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Assessment created successfully' in res.data

    # Find created assessment
    with app.app_context():
        ass = Assessment.query.filter_by(course_id=course_id, title='Test Practical Exam').first()
        ass_id = ass.id

    # Grade student: 85 marks
    grade_res = client.post(f'/trainer/assessments/{ass_id}/grade', data={
        f'score_{st1_id}': '85',
        f'feedback_{st1_id}': 'Great work on circuit wiring'
    }, follow_redirects=True)
    assert grade_res.status_code == 200
    assert b'Assessment marks and feedback updated' in grade_res.data

    # Verify score in database and calculation
    with app.app_context():
        st_profile = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        stats = st_profile.get_assessment_stats(course_id)
        assert stats['count'] == 1
        assert stats['completed'] == 1
        assert stats['average_percentage'] == 85.0

def test_student_view_own_assessment_results(client, init_database, app):
    with app.app_context():
        st1 = StudentProfile.query.filter_by(student_id_code='TEST-STU-01').first()
        course_id = init_database['course'].id
        db.session.add(Enrollment(student_id=st1.id, course_id=course_id, status='enrolled'))
        ass = Assessment(course_id=course_id, title='Quiz 1', max_marks=50.0, assessment_type='quiz')
        db.session.add(ass)
        db.session.flush()
        db.session.add(AssessmentResult(assessment_id=ass.id, student_id=st1.id, marks_obtained=45.0, feedback='Well done!'))
        db.session.commit()

    # Log in as student
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    response = client.get('/student/assessments')
    assert response.status_code == 200
    assert b'Quiz 1' in response.data
    assert b'45.0' in response.data or b'45' in response.data
    assert b'Well done!' in response.data
