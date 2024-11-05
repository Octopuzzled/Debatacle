from . import start_bp
from flask import render_template

@start_bp.route("/start")
def start():
    return render_template('start.html')
        