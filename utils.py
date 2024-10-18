from flask import render_template, redirect, session
import re
import bcrypt
from functools import wraps
from db_connection import get_connection

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

def get_user_progress(user_id):
    connection = get_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT lesson_id, slide_order 
            FROM user_progress 
            WHERE user_id = %s
            ORDER BY last_viewed DESC
            LIMIT 1
        """, (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def is_admin(f):
    """
    Decorate routes to require admin status.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("is_admin") != 1:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

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
    