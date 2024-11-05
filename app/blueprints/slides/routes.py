from . import slides_bp
from flask import Blueprint, jsonify, request, session
from app.db_connection import get_connection

slides_bp = Blueprint('slides', __name__)

@slides_bp.route('/api/slides')
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

@slides_bp.route('/api/update-progress/<int:lesson_id>/<int:slide_order>', methods=['POST'])
def update_progress(lesson_id, slide_order):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User  not logged in"}), 401

    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT s.slide_id, 
                       (SELECT COUNT(*) FROM slides WHERE lesson_id = %s) as total_slides
                FROM slides s 
                WHERE s.lesson_id = %s AND s.slide_order = %s
            """, (lesson_id, lesson_id, slide_order))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({"error": "Slide not found"}), 404
            
            cursor.execute("""
                INSERT INTO user_progress (user_id, lesson_id, last_slide_id)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE last_slide_id = %s
            """, (user_id, lesson_id, result['slide_id'], result['slide_id']))
            
            if slide_order == result['total_slides']:
                cursor.execute("""
                    INSERT IGNORE INTO lesson_completions (user_id, lesson_id)
                    VALUES (%s, %s)
                """, (user_id, lesson_id))
            
            connection.commit()
            
            return jsonify({
                "message": "Progress updated successfully",
                "is_completed": slide_order == result['total_slides']
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            connection.close()