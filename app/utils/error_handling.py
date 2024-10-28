from flask import render_template

def error_handling(error_message, error_code):
    return render_template('error.html', error_message=error_message, error_code=error_code)