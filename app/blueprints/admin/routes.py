from flask import Blueprint, render_template, request, redirect, url_for
from utils import is_admin, error_handling
from app.db_connection import get_connection
import logging
import bleach

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
@is_admin
def admin_panel():
    connection = get_connection()
    if connection is None:
        logging.error("Database connection failed.")
        return error_handling("Database connection failed", 503)

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT lesson_id, lesson_name, description, total_slides FROM lessons")
        lessons = cursor.fetchall()
        
        selected_lesson_id = request.args.get('lesson_id')
        slides = []
        selected_lesson = None

        if selected_lesson_id:
            cursor.execute("SELECT * FROM lessons WHERE lesson_id = %s", (selected_lesson_id,))
            selected_lesson = cursor.fetchone()
            if selected_lesson is None:
                logging.warning(f"Selected lesson not found: lesson_id={selected_lesson_id}")
                return error_handling("Selected lesson not found.", 404)

            cursor.execute("SELECT slide_id, content, slide_order FROM slides WHERE lesson_id = %s", (selected_lesson_id,))
            slides = cursor.fetchall()

        return render_template('admin.html', lessons=lessons, slides=slides, selected_lesson=selected_lesson)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return error_handling("An unexpected error occurred.", 500)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@admin_bp.route('/admin/add_lesson', methods=['POST'])
@is_admin
def add_lesson():
    lesson_name = request.form['lesson_name']
    description = request.form['description']
    total_slides = request.form['total_slides']
    
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO lessons (lesson_name, description, total_slides) 
            VALUES (%s, %s, %s
                    """, (lesson_name, description, total_slides))
        
        connection.commit()
        return redirect(url_for('admin.admin_panel'))
    except Exception as e:
        return str(e), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@admin_bp.route('/admin/add_slide', methods=['POST'])
@is_admin
def add_slide():
    lesson_id = request.form['lesson_id']
    content = bleach.clean(request.form['content'])  # Sanitize HTML
    slide_order = request.form['slide_order']
    
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO slides (lesson_id, content, slide_order) VALUES (%s, %s, %s)",
                       (lesson_id, content, slide_order))
        connection.commit()
        return redirect(url_for('admin.admin_panel'))
    except Exception as e:
        return str(e), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@admin_bp.route('/admin/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@is_admin
def edit_lesson(lesson_id):
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            lesson_name = request.form['lesson_name']
            description = request.form['description']
            total_slides = request.form['total_slides']
            cursor.execute("""
                UPDATE lessons
                SET lesson_name = %s, description = %s, total_slides = %s
                WHERE lesson_id = %s
            """, (lesson_name, description, total_slides, lesson_id))
            connection.commit()
            return redirect(url_for('admin.admin_panel'))

        cursor.execute("SELECT * FROM lessons WHERE lesson_id = %s", (lesson_id,))
        lesson = cursor.fetchone()
        return render_template('edit_lesson.html', lesson=lesson)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@admin_bp.route('/admin/delete_lesson/<int:lesson_id>', methods=['GET'])
@is_admin
def delete_lesson(lesson_id):
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM lessons WHERE lesson_id=%s", (lesson_id,))
        connection.commit()
        return redirect(url_for('admin.admin_panel'))
    except Exception as e:
        return str(e), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@admin_bp.route('/admin/edit_slide/<int:slide_id>', methods=['GET', 'POST'])
@is_admin
def edit_slide(slide_id):
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            content = request.form['content']
            slide_order = request.form['slide_order']
            cursor.execute("""
                UPDATE slides
                SET content = %s, slide_order = %s
                WHERE slide_id = %s
            """, (content, slide_order, slide_id))
            connection.commit()
            return redirect(url_for('admin.admin_panel', lesson_id=request.form['lesson_id']))

        cursor.execute("SELECT * FROM slides WHERE slide_id = %s", (slide_id,))
        slide = cursor.fetchone()
        return render_template('edit_slide.html', slide=slide)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@admin_bp.route('/admin/delete_slide/<int:slide_id>', methods=['GET'])
@is_admin
def delete_slide(slide_id):
    connection = get_connection()
    if connection is None:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM slides WHERE slide_id=%s", (slide_id,))
        connection.commit()
        return redirect(url_for('admin.admin_panel'))
    except Exception as e:
        return str(e), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()