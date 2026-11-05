from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*allowed_roles):
    """
    Decorator to restrict view access to specific user roles.
    Usage: @role_required('admin') or @role_required('trainer', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in allowed_roles:
                flash('Access denied: You do not have permission to view this resource.', 'danger')
                # Redirect to appropriate home page depending on role
                if current_user.is_student():
                    return redirect(url_for('student.dashboard'))
                elif current_user.is_trainer():
                    return redirect(url_for('trainer.dashboard'))
                elif current_user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
