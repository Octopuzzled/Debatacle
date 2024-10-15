from utils import error_handling
from flask import redirect, session
from db_connection import get_connection as connection
import bcrypt

def login_user(username, password):
    # Query database for username
    cursor = connection.cursor()
    cursor.execute("SELECT password_hash, salt, user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user:
        password_hash, salt, user_id = user

        # Recreate the hashed password using the salt and check against stored hash
        salted_password = password.encode()  # The raw password
        hashed_password = bcrypt.hashpw(salted_password, password_hash.encode())
        
        # Check if the provided password matches the stored hash
        if hashed_password == password_hash.encode():
            # Remember which user has logged in
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
        cursor.execute("INSERT INTO users (username, email, salt, password_hash) VALUES(%s, %s, %s, %s)", (username, email, salt, password_hash))
        connection.commit()
        return redirect("/login")
    except ValueError as e:
        return error_handling("Error registering user", 400)
    finally:
        cursor.close()