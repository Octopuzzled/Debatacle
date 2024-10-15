from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_login import current_user
import atexit
from models import register_user, login_user
from utils import create_password_hash, error_handling, valid_email, login_required
from db_connection import get_connection as connection


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



# Routes for all the pages  
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home", methods=["GET"])
@login_required
def home():
    return render_template("home.html", current_user=current_user)
        
@app.route("/logical-structures")
def logical_structures():
    return render_template("logical-structures.html")
  
@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/vocabulary", methods=["GET"])
def vocabulary():
    return render_template("vocabulary.html")   
    
    
    
# Routes for handling user accounts
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



# Routes for progress tracking of lessons for logged in users
@app.route("/update_progress", methods=["POST"])
def update_progress():
    user_id = request.form["user_id"]
    lesson_name = request.form["lesson_name"]
    page_number = request.form["page_number"]
    # Update the user_progress table
    query = "UPDATE user_progress SET last_page = %s WHERE user_id = %s AND lesson_name = %s"
    cursor = connection.cursor()
    cursor.execute(query, (page_number, user_id, lesson_name))
    connection.commit()
    cursor.close()
    return "Progress updated"

@app.route("/get_progress", methods=["GET"])
def get_progress():
    user_id = request.args.get("user_id")
    # Retrieve the user's progress for each lesson
    query = "SELECT lesson_name, last_page FROM user_progress WHERE user_id = %s"
    cursor = connection.cursor()
    cursor.execute(query, (user_id,))
    progress = cursor.fetchall()
    cursor.close()
    return jsonify([{"lesson_name": p[0], "last_page": p[1]} for p in progress])

@app.route("/continue_lesson/<user_id>/<lesson_name>", methods=["GET"])
def continue_lesson(user_id, lesson_name):
    if not user_id:
        return "Error: User ID is required", 400
    
    query = "SELECT last_page FROM user_progress WHERE user_id = %s AND lesson_name = %s"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (user_id, lesson_name))
        user_progress = cursor.fetchone()
        
        if not user_progress:
            return "Error: No progress found", 404
        
        return redirect(url_for("lesson_page", lesson_name=lesson_name, page_number=user_progress[0]))
    finally:
        cursor.close()

@app.route("/lesson/<lesson_name>/<int:page_number>", methods=["GET"])
def lesson_page(lesson_name, page_number):
    query = "SELECT content FROM lessons WHERE name = %s AND page_number = %s"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (lesson_name, page_number))
        lesson_content = cursor.fetchone()
        
        if not lesson_content:
            return "Error: Lesson not found", 404
        
        return render_template("lesson.html", lesson_content=lesson_content[0])
    finally:
        cursor.close()

# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)