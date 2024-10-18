from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_login import current_user
import atexit
from models import register_user, login_user
from utils import create_password_hash, error_handling, valid_email, is_admin, login_required
from db_connection import get_connection
import bleach

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
    content =  bleach.clean(request.form['content'])  # Sanitize HTML
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
    user_id = session["user_id"]
    last_slide = None
    all_lessons = []

    connection = get_connection()
    if connection is None:
        return render_template('home.html', error="Database connection failed"), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            # Fetch the user's progress
            cursor.execute("""
                SELECT up.lesson_id, up.last_slide_id, l.lesson_name, s.slide_order
                FROM user_progress up
                JOIN lessons l ON up.lesson_id = l.lesson_id
                JOIN slides s ON up.last_slide_id = s.slide_id
                WHERE up.user_id = %s
            """, (user_id,))
            progress = cursor.fetchone()

            if progress:
                last_lesson = {
                    'lesson_id': progress['lesson_id'],
                    'lesson_name': progress['lesson_name'],
                    'slide_id': progress['last_slide_id'],
                    'slide_order': progress['slide_order']
                }

            # Fetch all lessons for progress display
            cursor.execute("SELECT lesson_id, lesson_name FROM lessons ORDER BY lesson_id")
            all_lessons = cursor.fetchall()

    except Exception as e:
        return render_template('home.html', error=f"An error occurred: {str(e)}"), 500

    finally:
        if connection.is_connected():
            connection.close()

    return render_template('home.html', last_lesson=last_lesson, all_lessons=all_lessons)
        

@app.route('/learn-logic/<int:lesson_id>')
@app.route('/learn-logic/<int:lesson_id>/<int:slide_order>')
def learn_logic(lesson_id, slide_order=None):
    user_id = session.get('user_id')  # Get user_id from session if logged in
    connection = get_connection()
    if connection is None:
        return render_template('learn-logic.html', error="Database connection failed"), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            # Fetch lesson information
            cursor.execute("SELECT lesson_name FROM lessons WHERE lesson_id = %s", (lesson_id,))
            lesson = cursor.fetchone()
            if not lesson:
                return render_template('learn-logic.html', error="Lesson not found"), 404

            # Determine slide order
            if slide_order is None:
                if user_id:
                    cursor.execute("""
                        SELECT COALESCE(up.last_slide_id, (SELECT MIN(slide_id) FROM slides WHERE lesson_id = %s)) as slide_id
                        FROM user_progress up
                        WHERE up.user_id = %s AND up.lesson_id = %s
                    """, (lesson_id, user_id, lesson_id))
                    result = cursor.fetchone()
                    slide_id = result['slide_id'] if result else None
                else:
                    cursor.execute("SELECT MIN(slide_id) as slide_id FROM slides WHERE lesson_id = %s", (lesson_id,))
                    slide_id = cursor.fetchone()['slide_id']

                if slide_id:
                    cursor.execute("SELECT slide_order FROM slides WHERE slide_id = %s", (slide_id,))
                    slide_order = cursor.fetchone()['slide_order']
                else:
                    slide_order = 1
            
            # Fetch current slide
            cursor.execute("""
                SELECT slide_id, content
                FROM slides
                WHERE lesson_id = %s AND slide_order = %s
            """, (lesson_id, slide_order))
            slide = cursor.fetchone()
            if not slide:
                return render_template('learn-logic.html', error="Slide not found"), 404

            # Get total number of slides
            cursor.execute("SELECT COUNT(*) as total FROM slides WHERE lesson_id = %s", (lesson_id,))
            total_slides = cursor.fetchone()['total']

            # Update user progress if logged in
            if user_id:
                cursor.execute("""
                    INSERT INTO user_progress (user_id, lesson_id, last_slide_id)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE last_slide_id = %s
                """, (user_id, lesson_id, slide['slide_id'], slide['slide_id']))
                connection.commit()

    except Exception as e:
        return render_template('learn-logic.html', error=f"An error occurred: {str(e)}"), 500
    finally:
        if connection.is_connected():
            connection.close()

    return render_template('learn-logic.html',
                           lesson_name=lesson['lesson_name'],
                           lesson_id=lesson_id,
                           slide=slide,
                           slide_order=slide_order,
                           total_slides=total_slides)

    
@app.route('/lessons')
def lessons():
    connection = get_connection()
    if connection is None:
        return render_template('lessons.html', error="Database connection failed"), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT lesson_id, lesson_name FROM lessons ORDER BY lesson_id")
            all_lessons = cursor.fetchall()
    except Exception as e:
        return render_template('lessons.html', error=f"An error occurred: {str(e)}"), 500
    finally:
        if connection.is_connected():
            connection.close()

    return render_template('lessons.html', lessons=all_lessons)

        
@app.route("/logical-structures")
def logical_structures():
    return render_template("logical-structures.html")
  
@app.route("/start")
def start():
    return render_template("learn-logic.html")

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
            
@app.route('/api/slide/<int:lesson_id>/<int:slide_order>')  # For JavaScript
def get_slide(lesson_id, slide_order):
    connection = get_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT content
                FROM slides
                WHERE lesson_id = %s AND slide_order = %s
            """, (lesson_id, slide_order))
            slide = cursor.fetchone()
            
            if not slide:
                return jsonify({"error": "Slide not found"}), 404

            return jsonify({"content": slide['content']})
    except Exception as e:
        return jsonify({"error": "An error occurred: " + str(e)}), 500
    finally:
        if connection.is_connected():
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    if request.method == 'POST':
        data = request.json
        lesson_id = data.get('lesson_id')
        slide_id = data.get('slide_id')

        if not lesson_id or not slide_id:
            return jsonify({"error": "Lesson ID and Slide ID are required"}), 400

        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_progress (user_id, lesson_id, last_slide_id) 
                    VALUES (%s, %s, %s) 
                    ON DUPLICATE KEY UPDATE last_slide_id = %s
                """, (user_id, lesson_id, slide_id, slide_id))
                connection.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": "An error occurred: " + str(e)}), 500
        finally:
            if connection.is_connected():
                connection.close()
    else:  # GET request
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT lesson_id, last_slide_id FROM user_progress WHERE user_id = %s", (user_id,))
                progress = cursor.fetchone()
                return jsonify(progress) if progress else jsonify({})
        except Exception as e:
            return jsonify({"error": "An error occurred: " + str(e)}), 500
        finally:
            if connection.is_connected():
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

# Also for JS
@app.route('/api/update-progress/<int:lesson_id>/<int:slide_order>', methods=['POST'])
def update_progress(lesson_id, slide_order):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    connection = get_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with connection.cursor() as cursor:
            # Get slide_id once
            cursor.execute("""
                SELECT slide_id FROM slides WHERE lesson_id = %s AND slide_order = %s
            """, (lesson_id, slide_order))
            slide = cursor.fetchone()

            if not slide:
                return jsonify({"error": "Slide not found"}), 404
            
            slide_id = slide['slide_id']
            
            cursor.execute("""
                INSERT INTO user_progress (user_id, lesson_id, last_slide_id)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE last_slide_id = %s
            """, (user_id, lesson_id, slide_id, slide_id))
            connection.commit()

        return jsonify({"message": "Progress updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred: " + str(e)}), 500
    finally:
        if connection.is_connected():
            connection.close()

# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)