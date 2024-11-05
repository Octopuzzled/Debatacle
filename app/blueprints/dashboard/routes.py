from . import dashboard_bp
from flask import Blueprint, render_template, session
from app.db_connection import get_connection
from app.blueprints.auth.utils import login_required


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/home", methods=["GET"])
@login_required
def home():
    user_id = session["user_id"]
    connection = get_connection()
    
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT 
                    l.lesson_id,
                    l.lesson_name,
                    l.total_slides,
                    up.last_slide_id,
                    s.slide_order as current_progress,
                    CASE WHEN lc.completed_at IS NOT NULL 
                         THEN TRUE ELSE FALSE END as is_completed
                FROM lessons l
                LEFT JOIN user_progress up 
                    ON l.lesson_id = up.lesson_id 
                    AND up.user_id = %s
                LEFT JOIN slides s 
                    ON up.last_slide_id = s.slide_id
                LEFT JOIN lesson_completions lc 
                    ON l.lesson_id = lc.lesson_id 
                    AND lc.user_id = %s
                ORDER BY l.lesson_id
            """, (user_id, user_id))
            
            lessons = cursor.fetchall()
            
            for lesson in lessons:
                if lesson['current_progress'] and lesson['total_slides'] and lesson['total_slides'] > 0:
                    lesson['progress_percent'] = round(
                        (lesson['current_progress'] / lesson['total_slides']) * 100
                    )
                else:
                    lesson['progress_percent'] = 0

            last_lesson = next(
                (lesson for lesson in lessons if lesson['last_slide_id']), 
                None
            )

            return render_template(
                'home.html', 
                last_lesson=last_lesson, 
                all_lessons=lessons
            )
                
    except Exception as e:
        return render_template('home.html', error=f"An error occurred: {str(e)}"), 500
    finally:
        if connection.is_connected():
            connection.close()