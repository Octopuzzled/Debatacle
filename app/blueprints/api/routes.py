from flask import Blueprint, jsonify, session
from app.db_connection import get_connection, close_connection

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/lessons')
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
        # Close the cursor and return the connection to the pool
        if cursor:
            cursor.close()
        close_connection(connection)

@api_bp.route('/api/progress')
def get_user_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User  not logged in"}), 401

    connection = get_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT up.lesson_id, up.last_slide_id, s.slide_order
                FROM user_progress up
                JOIN slides s ON up.last_slide_id = s.slide_id
                WHERE up.user_id = %s
            """, (user_id,))
            progress = cursor.fetchall()
            
            progress_dict = {
                p['lesson_id']: {
                    'last_slide_id': p['last_slide_id'],
                    'slide_order': p['slide_order']
                } for p in progress
            }
            
            return jsonify(progress_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        close_connection(connection)