from flask import render_template, redirect, session
import re
import bcrypt
from functools import wraps

import bcrypt

def create_password_hash(password):
    # Generate a salt using bcrypt
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt with the generated salt
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password.decode(), salt.decode()

# Error handling
def error_handling(error_message, error_code):
    return render_template('error.html', error_message=error_message, error_code=error_code)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Email checking
def valid_email(email):
    # Regex pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    # Check if email matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False
    