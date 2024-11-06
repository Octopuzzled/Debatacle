from app.utils import error_handling
from flask import redirect, session, jsonify
from app.db_connection import get_connection
import bcrypt

def create_password_hash(password):
    # Generate a salt using bcrypt
    salt = bcrypt.gensalt()
    # Hash the password using bcrypt with the generated salt
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode(), salt.decode()

def login_required(f):
    """
    Decorate routes to require login.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def is_admin(f):
    """
    Decorate routes to require admin status.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("is_admin") != 1:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def login_user(username, password):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if connection is None:
            return False

        cursor = connection.cursor()
        cursor.execute("SELECT password_hash, user_id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            stored_hash, user_id = user
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Retrieve is_admin value
                cursor.execute("SELECT is_admin FROM users WHERE username = %s", (username,))
                is_admin = cursor.fetchone()[0]
                
                # Return successful login data instead of redirecting
                return {
                    "success": True,
                    "user_id": user_id,
                    "is_admin": is_admin
                }
        return False

    except Exception as e:
        print(f"Login error: {str(e)}")  # For debugging
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def register_user(username, email, password):
    # Check if user already exists
    connection = get_connection()
    if connection is None:
            return error_handling("Failed to connect to database", 500)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    rows = cursor.fetchall()
    
    if len(rows) > 0:
        cursor.close()
        return error_handling("User already exists", 400)

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt)

    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES(%s, %s, %s)", (username, email, password_hash))
        connection.commit()
        return redirect("/login")
    except Exception as e:
        return error_handling("Error registering user", 400)
    finally:
        cursor.close()