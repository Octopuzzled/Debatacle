import re

def valid_email(email):
    # Regex pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    # Check if email matches the pattern
    return bool(re.match(pattern, email))