from . import quiz_bp
from flask import render_template, jsonify, request, Blueprint
import json
from typing import Dict, List
from app.utils.error_handling import error_handling
from app.db_connection import get_connection, close_connection
from .quiz_handler import QuizHandler
      
        
quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/lesson/<int:lesson_id>/quiz')
def get_quiz(lesson_id):
    quiz_handler = QuizHandler()
    try:
        quiz = quiz_handler.get_quiz_by_lesson(lesson_id)
        
        if not quiz:
            return error_handling("Quiz not found", 404)
        
        return jsonify(quiz)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz():
    try:
        data = request.json
        quiz_handler = QuizHandler()
        
        result = quiz_handler.submit_quiz(
            user_id=data['user_id'],
            quiz_id=data['quiz_id'],
            answers=data['answers']
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500