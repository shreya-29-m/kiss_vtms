
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'kiss-vtms-local-development-only'
)

    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "kiss_vtms.db")}'
    )

    # Use psycopg 3 for PostgreSQL connections
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace(
            'postgres://', 'postgresql+psycopg://', 1
        )
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace(
            'postgresql://', 'postgresql+psycopg://', 1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'zip'}

    DEFAULT_ATTENDANCE_THRESHOLD = 75.0
    DEFAULT_PASSING_SCORE = 50.0


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
