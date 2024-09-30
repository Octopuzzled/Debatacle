from email.iterators import _structure
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
import atexit
from models import register_user, login_user
from utils import create_password_hash, error_handling, valid_email, login_required
from db_connection import connection
import mysql.connector
from functools import wraps

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
        
        # Modified query to fetch the most recent progress without using updated_at
        cursor.execute('''
            SELECT lesson_name, last_page 
            FROM user_progress
            WHERE user_id = %s
            ORDER BY last_page DESC  -- Assuming higher page numbers are more recent
            LIMIT 1
        ''', (user_id,))
        
        progress = cursor.fetchone()
        
        lesson_name = progress['lesson_name'] if progress else None
        last_page = progress['last_page'] if progress else None

        return render_template('home.html', lesson_name=lesson_name, last_page=last_page)
    
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
def logical_structure():
    return render_template("logical-structures.html")

@app.route('/save_progress', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    user_id = session['user_id']
    lesson_name = data['lesson_name']
    last_page = data['last_page']

    # Upsert the user's progress into the database
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT lesson_name, last_page 
            FROM user_progress
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (user_id,))
        progress = cursor.fetchone()

        lesson_name = progress['lesson_name'] if progress else None
        last_page = progress['last_page'] if progress else None

        return render_template('home.html', lesson_name=lesson_name, last_page=last_page)
    except Exception as e:
        app.logger.error(f"Error fetching user progress: {str(e)}")
        return render_template('home.html', error="An error occurred. Please try again later."), 500
    finally:
        cursor.close()
  
@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/vocabulary", methods=["GET"])
def vocabulary():
    return render_template("vocabulary.html")


# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)