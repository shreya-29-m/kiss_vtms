import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from app.config import Config
from app.models import db, User, Course, Category, Enrollment

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'certificates'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'materials'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.trainer.routes import trainer_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(trainer_bp, url_prefix='/trainer')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Landing page and institutional overview
    @app.route('/')
    def index():
        featured_courses = Course.query.filter_by(status='active').order_by(Course.created_at.desc()).limit(6).all()
        categories = Category.query.filter_by(is_active=True).all()
        stats = {
            'total_courses': Course.query.count(),
            'active_students': db.session.query(Enrollment.student_id).filter_by(status='enrolled').distinct().count(),
            'categories_count': Category.query.count(),
        }
        return render_template('index.html', featured_courses=featured_courses, categories=categories, stats=stats)

    # Custom Jinja template filters
    @app.template_filter('format_date')
    def format_date_filter(value, fmt='%d %b %Y'):
        if value is None:
            return '—'
        return value.strftime(fmt)

    @app.context_processor
    def inject_global_data():
        return {
            'system_name': 'KISS Vocational Training Management System',
            'system_short': 'KISS VTMS',
            'current_year': 2026
        }

    return app
