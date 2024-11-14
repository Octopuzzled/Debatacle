from flask import Blueprint, render_template, request, session, redirect, url_for
from . import auth_bp
from app.utils.error_handling import error_handling
from app.utils.validation import valid_email
from app.blueprints.auth.utils import  create_password_hash, login_user, register_user

auth_bp = Blueprint('auth', __name__)

# Generally, I asked a lot of questions to ChatGPT and Claude to get this right.

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username:
            return error_handling("Must provide username", 403)
        
        elif not password:
            return error_handling("Must provide password", 403)
        
        login_result = login_user(username, password)
        
        if login_result and isinstance(login_result, dict):
            # Set session variables
            session["user_id"] = login_result["user_id"]
            session["is_admin"] = login_result["is_admin"]
            return redirect(url_for('main.index'))  # Adjust 'main.index' to your actual home route
        else:
            return error_handling("Invalid username or password", 403)
    
    # GET request
    return render_template("login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Logout user"""
    session.clear()
    return redirect("/")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get form data with stripped whitespace
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate required fields
        if not username:
            return error_handling("Invalid username", 400)

        if not password or not confirmation:
            return error_handling("Please enter a password and confirm it", 400)

        if password != confirmation:
            return error_handling("Passwords don't match", 400)

        if len(password) < 8:
            return error_handling("Password must be at least 8 characters long.", 400)

        if not valid_email(email):
            return error_handling("Please enter a valid email address", 400)

        # Register user
        try:
            result = register_user(username, email, password)
            if isinstance(result, str):  # If it's an error message
                return error_handling(result, 400)
            return result  # Should be the redirect
        except Exception as e:
            return error_handling("Registration failed", 400)

    # GET request
    return render_template("register.html")  # Update template path if needed