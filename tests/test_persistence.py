import os
import tempfile
from app import create_app
from app.config import Config
from app.models import db, User, Category, Course
from datetime import date, timedelta

def test_database_persistence_across_app_restart():
    # Create a temporary SQLite file
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_persistence.db")

    class PersistenceConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        WTF_CSRF_ENABLED = False

    # 1. First app instance: Create tables and insert records
    app1 = create_app(PersistenceConfig)
    with app1.app_context():
        db.create_all()
        user = User(username='persistent_user', email='persist@kiss.ac.in', role='student')
        user.set_password('Secret@123')
        db.session.add(user)

        cat = Category(name='Persistence Craft', description='Testing persistence', is_active=True)
        db.session.add(cat)
        db.session.commit()
        user_id = user.id
        cat_id = cat.id

    # 2. Simulate complete application shutdown and restart with a new instance
    del app1

    app2 = create_app(PersistenceConfig)
    with app2.app_context():
        # Verify data still exists in SQLite database file without re-creating
        retrieved_user = User.query.get(user_id)
        assert retrieved_user is not None
        assert retrieved_user.username == 'persistent_user'
        assert retrieved_user.check_password('Secret@123') is True

        retrieved_cat = Category.query.get(cat_id)
        assert retrieved_cat is not None
        assert retrieved_cat.name == 'Persistence Craft'

    # Clean up temporary test file
    try:
        os.remove(db_path)
        os.rmdir(temp_dir)
    except Exception:
        pass
