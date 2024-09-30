from utils import error_handling
from flask import redirect, session
from db_connection import connection
import bcrypt

def login_user(username, password):
    # Query database for username
    cursor = connection.cursor()
    cursor.execute("SELECT password_hash, user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user:
        stored_hash, user_id = user
        # Check if the provided password matches the stored hash
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            session["user_id"] = user_id
            return redirect("/")  # Successful login
        else:
            return None  # Invalid password
    else:
        return None  # User not found

def register_user(username, email, salt, password_hash):
    # Check if user already exists
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    rows = cursor.fetchall()
    
    if len(rows) > 0:
        cursor.close()
        return error_handling("User already exists", 400)

    # Store the salt and hashed password in your database
    try:
        cursor.execute("INSERT INTO users (username, email, password_salt, password_hash) VALUES(%s, %s, %s, %s)", (username, email, salt, password_hash))
        connection.commit()
        return redirect("/login")
    except ValueError as e:
        return error_handling("Error registering user", 400)
    finally:
        cursor.close()