from app.utils import error_handling
from flask import redirect, session, jsonify, url_for
from app.db_connection import get_connection
import bcrypt

# Generally, I asked a lot of questions to ChatGPT and Claude to get this right. Also, I oriented myslef on CS50 stock project

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
                
                # Return successful login data for route
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
        return "Failed to connect to database"
    
    try:
        cursor = connection.cursor()
        
        # Check for existing user
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return "User already exists"
            
        # Check for existing email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Email already registered"

        # Generate salt and hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)

        # Insert new user with both hash and salt
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, password_salt) VALUES(%s, %s, %s, %s)", 
            (username, email, password_hash, salt)
        )
        connection.commit()
        
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        return f"Error registering user: {str(e)}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        connection.close()