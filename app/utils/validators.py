import re

def validate_phone_number(phone_str):
    """
    Accepts:
    - Empty or None (optional field)
    - Exactly 10-digit Indian mobile numbers starting with 6, 7, 8, or 9

    Returns:
    - (is_valid, message)
    """
    if not phone_str or not phone_str.strip():
        return True, ""

    cleaned = phone_str.strip()

    if re.fullmatch(r'[6-9][0-9]{9}', cleaned):
        return True, ""

    return False, "Enter a valid 10-digit Indian mobile number."


def validate_username(username):
    """
    Validates a username:
    - Length between 3 and 30 characters
    - Must only contain alphanumeric characters, underscores, and dots
    - Must start with an alphanumeric character
    """
    if not username:
        return False, "Username is required."
    
    cleaned = username.strip()
    if len(cleaned) < 3 or len(cleaned) > 30:
        return False, "Username must be between 3 and 30 characters."
    
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_\.]*$', cleaned):
        return False, "Username must start with a letter or digit and can only contain letters, numbers, underscores, or dots."
    
    return True, cleaned


def validate_email_format(email):
    """
    Validates email format using RFC-compliant pattern.
    """
    if not email:
        return False, "Email address is required."
    
    cleaned = email.strip().lower()
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, cleaned):
        return False, "Please enter a valid email address (e.g. student@kiss.ac.in)."
    
    return True, cleaned



