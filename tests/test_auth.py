def test_login_success_student(client, init_database):
    response = client.post('/auth/login', data={
        'username': 'student_test1',
        'password': 'Student@12345'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Trainee Learning Portal' in response.data or b'student1' in response.data

def test_login_success_trainer(client, init_database):
    response = client.post('/auth/login', data={
        'username': 'trainer_test',
        'password': 'Trainer@12345'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Trainer Instruction Portal' in response.data

def test_login_success_admin(client, init_database):
    response = client.post('/auth/login', data={
        'username': 'admin_test',
        'password': 'Admin@12345'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Administrator Control Center' in response.data

def test_login_invalid_password(client, init_database):
    response = client.post('/auth/login', data={
        'username': 'student_test1',
        'password': 'WrongPassword999'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_login_nonexistent_user(client, init_database):
    response = client.post('/auth/login', data={
        'username': 'ghost_user',
        'password': 'SomePassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_student_self_registration(client, init_database):
    response = client.post('/auth/register', data={
        'username': 'new_trainee',
        'email': 'new.trainee@kiss.ac.in',
        'password': 'SecurePass123',
        'confirm_password': 'SecurePass123',
        'full_name': 'New Tribal Trainee',
        'academic_level': '+2 Arts',
        'contact_number': '9876543210',
        'skills_and_interests': 'Tailoring and handicraft'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    assert b'New Tribal Trainee' in response.data

def test_student_registration_duplicate_username(client, init_database):
    response = client.post('/auth/register', data={
        'username': 'student_test1',
        'email': 'different.email@kiss.ac.in',
        'password': 'Password123',
        'confirm_password': 'Password123',
        'full_name': 'Duplicate User',
        'academic_level': '+2 Science'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username is already taken' in response.data

def test_student_cannot_access_admin_portal(client, init_database):
    # Log in as student
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Access denied' in response.data
    assert b'Trainee Learning Portal' in response.data

def test_trainer_cannot_access_admin_portal(client, init_database):
    # Log in as trainer
    client.post('/auth/login', data={'username': 'trainer_test', 'password': 'Trainer@12345'})
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Access denied' in response.data
    assert b'Trainer Instruction Portal' in response.data

def test_unauthenticated_redirect(client):
    response = client.get('/student/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page' in response.data

def test_logout(client, init_database):
    client.post('/auth/login', data={'username': 'student_test1', 'password': 'Student@12345'})
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out securely' in response.data
