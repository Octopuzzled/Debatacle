from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/vocabulary", methods=["GET"])
def vocab():
    return render_template("vocabulary.html")

# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)