from flask import Blueprint, render_template, request, session, redirect
from . import auth_bp
from app.utils.error_handling import error_handling
from app.utils.validation import valid_email
from app.blueprints.auth.utils import  create_password_hash, login_user, register_user

auth_bp = Blueprint('auth', __name__)



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
        
        if login_result:
            return login_result
        else:
            return error_handling("Invalid username or password", 403)
    else:
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
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

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

        hashed_password, salt = create_password_hash(password)
        result = register_user(username, email, salt, hashed_password)
        
        if result:
            return result
        else:
            return error_handling("Registration failed", 400)
    else:
        return render_template("register.html")