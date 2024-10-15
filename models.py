from utils import error_handling
from flask import redirect, session, jsonify
from db_connection import get_connection
import bcrypt

def login_user(username, password):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500

        cursor = connection.cursor()
        cursor.execute("SELECT password_hash, user_id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            stored_hash, user_id = user
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                session["user_id"] = user_id
                return redirect("/")  # Successful login
            else:
                return jsonify({"error": "Invalid password"}), 401  # Invalid password
        else:
            return jsonify({"error": "User not found"}), 404  # User not found

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()

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