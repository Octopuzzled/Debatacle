from email.iterators import _structure
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
import atexit
from models import register_user, login_user
from utils import create_password_hash, error_handling, valid_email, login_required
from db_connection import connection
import mysql.connector
from functools import wraps
from flask import jsonify

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Close the db connection when application shuts down
@atexit.register
def close_db_connection():
    connection.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/home')
@login_required
def home():
    user_id = session['user_id']
    
    try:
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        cursor.execute('''
            SELECT lesson_name, last_page 
            FROM user_progress
            WHERE user_id = %s
            ORDER BY last_page ASC
            LIMIT 1
        ''', (user_id,))
        
        progress = cursor.fetchone()
        
        if progress:
            lesson_name = progress['lesson_name']
            last_page = progress['last_page']
            
            # Map the database lesson_name to the correct route function name
            lesson_route_map = {
                'logical-structures': 'logical_structures',
                'vocabulary': 'vocabulary',
                # Add other mappings as needed
            }
            
            route_name = lesson_route_map.get(lesson_name)
            if route_name:
                continue_url = url_for(route_name, part=last_page)
            else:
                app.logger.error(f"No route found for lesson: {lesson_name}")
                continue_url = None
        else:
            continue_url = None
            lesson_name = None
            last_page = None

        return render_template('home.html', continue_url=continue_url, lesson_name=lesson_name, last_page=last_page)
    
    except mysql.connector.Error as e:
        app.logger.error(f"Database error: {e}")
        return render_template('home.html', error="An error occurred while fetching your progress. Please try again later."), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return render_template('home.html', error="An unexpected error occurred. Please contact support if this persists."), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        connection.commit()
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (submitting form)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
    
        # Ensure username was submitted
        if not username:
            return error_handling("Must provide username", 403)
        
        # Ensure password was submitted
        elif not password:
            return error_handling("Must provide password", 403)
        
        # Login user
        login_result = login_user(username, password)
        
       # Check if login was successful
        if login_result:  # assuming login_result is a redirect or a valid response
            return login_result
        else:
            return error_handling("Invalid username or password", 403)
    
    # User reached route via GET (just clicking link)
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Logout user"""
    
    # Forget any user_id
    session.clear()
    
    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # User reached route via POST (submitting form)
    if request.method == "POST":
        # Get the user info from register.html
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Error handling for user mistakes
        if not username:
            return error_handling("Invalid username", 400)
        if not password or not confirmation:
            return error_handling("Please enter a password and confirm it", 400)
        if not password == confirmation:
            return error_handling("Passwords don't match", 400)
        if len(password) < 8:
            return error_handling("Password must be at least 8 characters long.", 400)
        if not valid_email(email):
            return error_handling("Please enter a valid email address", 400)
          
        # Hash the password using the salt
        hashed_password, salt = create_password_hash(password)

        # Store the user info in the database
        result = register_user(username, email, salt, hashed_password)
        
        # Check if registration was successful or if there was an error
        if result:  # assuming register_user returns a response or redirect
            return result
        else:
            return error_handling("Registration failed", 400)
    
    # User reached route via GET (just clicking link)
    else:
        return render_template("register.html")
       
@app.route("/logical-structures")
def logical_structures():
    part = request.args.get('part', 0, type=int)
    return render_template("logical-structures.html", current_part=part)

@app.route('/save_progress', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    
    # Debugging logs
    app.logger.info(f"Received data: {data}")

    lesson_name = data.get('lesson_name')
    last_page = data.get('last_page')
    user_id = session.get('user_id')

    if not lesson_name or last_page is None or user_id is None:
        app.logger.error(f"Invalid data: lesson_name={lesson_name}, last_page={last_page}, user_id={user_id}")
        return jsonify({"error": "Invalid data"}), 400

    try:
        cursor = connection.cursor()
        # Debugging log to check if data is passed correctly
        app.logger.info(f"Inserting/Updating progress for user {user_id}, lesson: {lesson_name}, page: {last_page}")

        # Insert or update progress in database
        cursor.execute('''
            INSERT INTO user_progress (user_id, lesson_name, last_page)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE last_page = VALUES(last_page)
        ''', (user_id, lesson_name, last_page))

        connection.commit()

        app.logger.info(f"Progress saved successfully for user {user_id}")
        return jsonify({"message": "Progress saved successfully"}), 200

    except mysql.connector.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Unexpected error"}), 500
    finally:
        if cursor:
            cursor.close()

  
@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/vocabulary", methods=["GET"])
def vocabulary():
    part = request.args.get('part', 0, type=int)
    return render_template("vocabulary.html", current_part=part)


# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)