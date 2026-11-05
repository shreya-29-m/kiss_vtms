from flask import request
from flask_login import current_user
from app.models import db, AuditLog

def log_audit(action, entity_type=None, entity_id=None, details=None, user_id=None):
    """
    Records an action in the audit log for traceability and system governance.
    """
    try:
        actual_user_id = user_id
        if actual_user_id is None and current_user and current_user.is_authenticated:
            actual_user_id = current_user.id
            
        ip = request.remote_addr if request else '127.0.0.1'
        
        log_entry = AuditLog(
            user_id=actual_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        # Avoid crashing primary operations if audit logging encounters a transient issue
        db.session.rollback()
