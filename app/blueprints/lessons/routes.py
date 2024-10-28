from flask import Blueprint, render_template, session
from app.db_connection import get_connection
from utils import login_required

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route("/")
def index():
    return render_template("index.html")

@lessons_bp.route("/home", methods=["GET"])
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

@lessons_bp.route('/lessons')
def lessons():
    connection = get_connection()
    if connection is None:
        return render_template('lessons.html', error="Database connection failed"), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT lesson_id, lesson_name, description FROM lessons ORDER BY lesson_id")
            all_lessons = cursor.fetchall()
    except Exception as e:
        return render_template('lessons.html', error=f"An error occurred: {str(e)}"), 500
    finally:
        if connection.is_connected():
            connection.close()

    return render_template('lessons.html', lessons=all_lessons)

@lessons_bp.route("/learn-logic/<int:lesson_id>")
@lessons_bp.route("/learn-logic/<int:lesson_id>/<int:slide_order>")
def learn_logic(lesson_id, slide_order=None):
    user_id = session.get('user_id')
    connection = get_connection()
    if connection is None:
        return render_template('learn-logic.html', error="Database connection failed"), 500

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT lesson_name FROM lessons WHERE lesson_id = %s", (lesson_id,))
            lesson = cursor.fetchone()
            if not lesson:
                return render_template('learn-logic.html', error="Lesson not found"), 404

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
            
            cursor.execute("""
                SELECT slide_id, content
                FROM slides
                WHERE lesson_id = %s AND slide_order = %s
            """, (lesson_id, slide_order))
            slide = cursor.fetchone()
            if not slide:
                return render_template('learn-logic.html', error="Slide not found"), 404

            cursor.execute("SELECT COUNT(*) as total FROM slides WHERE lesson_id = %s", (lesson_id,))
            total_slides = cursor.fetchone()['total']

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