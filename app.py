from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import mysql.connector
import atexit
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import re

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to MySQL database and inizialize connection globally
load_dotenv

user = os.getenv["MYSQL_USER"]
password = os.getenv["MYSQL_PASSWORD"]

connection = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    database="debatacle"
)

# Error handling
def error_handling(error_message, error_code):
    return render_template('error.html', error_message=error_message, error_code=error_code)

# Email checking
def valid_email(email):
    # Regex pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    # Check if email matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False

# Close the db connection when application shuts down
@atexit.register
def close_db_connection():
    connection.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
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
        error_handling("Password must be at least 8 characters lon.", 400)
    if not valid_email(email):
        return error_handling("Please enter a valid email address", 400)
    
    # Check if user already exists
    cursor = connection.cursor()
    cursor.execute( "SELECT * FROM users WHERE username = ?", (username,))
    rows = cursor.fetchall()
    if len(rows) > 0:
        return error("User already exists", 400)
    else:
        try:
            hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, hash) VALUES(%s, %s)", (username, hash))
            connection.commit()
            return redirect("/login")
        except ValueError as e:
            return error("User already exists", 400)
        finally:
            cursor.close()
    
    
@app.route("/logical-structures")
def structures():
    return render_template("logical-structures.html")

@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/vocabulary", methods=["GET"])
def vocab():
    return render_template("vocabulary.html")


# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)