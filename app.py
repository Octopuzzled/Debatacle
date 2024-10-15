from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_login import current_user
import atexit
from models import register_user, login_user
from utils import create_password_hash, error_handling, is_admin, valid_email, login_required
from db_connection import get_connection


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Close the db connection when application shuts down
#@atexit.register
#def close_db_connection():
#    connection.close()

# Routes for admin (adding content)
@app.route('/admin')
@is_admin
def admin_panel():
    return render_template('admin.html')

@app.route('/admin/add_lesson', methods=['POST'])
@is_admin
def add_lesson():
    lesson_name = request.form['lesson_name']
    description = request.form['description']
    
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO lessons (lesson_name, description) VALUES (%s, %s)",
                       (lesson_name, description))
        connection.commit()
        return redirect(url_for('admin_panel'))
    except Exception as e:
        return str(e), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/admin/add_slide', methods=['POST'])
@is_admin
def add_slide():
    lesson_id = request.form['lesson_id']
    content = request.form['content']
    slide_order = request.form['slide_order']
    
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO slides (lesson_id, content, slide_order) VALUES (%s, %s, %s)",
                       (lesson_id, content, slide_order))
        connection.commit()
        return redirect(url_for('admin_panel'))
    except Exception as e:
        return str(e), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Routes for all the user pages  
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home", methods=["GET"])
@login_required
def home():
    return render_template("home.html", current_user=current_user)

@app.route("/learn-logic")
def learn():
    return render_template("/learn-logic.html")
        
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
@app.route('/api/lessons')
def get_lessons():
    connection = get_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT lesson_id, lesson_name FROM lessons")
        lessons = cursor.fetchall()
        return jsonify(lessons)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/slides')
def get_slides():
    lesson_id = request.args.get('lesson_id')
    if not lesson_id:
        return jsonify({"error": "Lesson ID is required"}), 400

    connection = get_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT slide_id, content FROM slides WHERE lesson_id = %s ORDER BY slide_order", (lesson_id,))
        slides = cursor.fetchall()
        return jsonify(slides)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/progress', methods=['GET', 'POST'])
def handle_progress():
    if request.method == 'POST':
        data = request.json
        user_id = 1  # Replace with actual user authentication
        lesson_id = data.get('lesson_id')
        slide_id = data.get('slide_id')

        if not lesson_id or not slide_id:
            return jsonify({"error": "Lesson ID and Slide ID are required"}), 400

        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO user_progress (user_id, lesson_id, last_slide_id) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE last_slide_id = %s
            """, (user_id, lesson_id, slide_id, slide_id))
            connection.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:  # GET request
        user_id = 1  # Replace with actual user authentication

        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT lesson_id, last_slide_id FROM user_progress WHERE user_id = %s", (user_id,))
            progress = cursor.fetchone()
            return jsonify(progress) if progress else jsonify({})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

@app.route('/api/progress/<int:user_id>')
def get_progress(user_id):
    connection = get_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT last_slide_id FROM user_progress WHERE user_id = %s", (user_id,))
        progress = cursor.fetchone()
        if progress:
            return jsonify({"lastSlideId": progress['last_slide_id']})
        return jsonify({"lastSlideId": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)