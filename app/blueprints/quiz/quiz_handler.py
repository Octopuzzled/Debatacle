from typing import Dict, List
from app.db_connection import get_connection, close_connection
from app.utils.error_handling import error_handling

class QuizHandler:
    def get_quiz_by_lesson(self, lesson_id: int) -> Dict:
        connection = get_connection()
        if not connection:
            raise Exception("Could not establish database connection")
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Get quiz info
            cursor.execute("""
                SELECT quiz_id, title 
                FROM quizzes 
                WHERE lesson_id = %s
            """, (lesson_id,))
            
            quiz = cursor.fetchone()
            if not quiz:
                return None
            
            # Get questions and choices
            cursor.execute("""
                SELECT q.question_id, q.question_text,
                       c.choice_id, c.choice_text
                FROM quiz_questions q
                LEFT JOIN question_choices c ON q.question_id = c.question_id
                WHERE q.quiz_id = %s
                ORDER BY q.question_id, c.choice_id
            """, (quiz['quiz_id'],))
            
            questions = {}
            for row in cursor:
                if row['question_id'] not in questions:
                    questions[row['question_id']] = {
                        'id': row['question_id'],
                        'text': row['question_text'],
                        'choices': []
                    }
                
                questions[row['question_id']]['choices'].append({
                    'id': row['choice_id'],
                    'text': row['choice_text']
                })
            
            quiz['questions'] = list(questions.values())
            return quiz
            
        finally:
            cursor.close()
            close_connection(connection)

    def submit_quiz(self, user_id: int, quiz_id: int, answers: List[Dict]) -> Dict:
        connection = get_connection()
        if not connection:
            raise Exception("Could not establish database connection")
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Calculate score
            score = 0
            total = len(answers)
            
            for answer in answers:
                cursor.execute("""
                    SELECT is_correct 
                    FROM question_choices 
                    WHERE choice_id = %s
                """, (answer['choice_id'],))
                
                result = cursor.fetchone()
                if result and result['is_correct']:
                    score += 1
            
            # Record the attempt
            cursor.execute("""
                INSERT INTO quiz_attempts 
                (user_id, quiz_id, score, total_questions)
                VALUES (%s, %s, %s, %s)
            """, (user_id, quiz_id, score, total))
            
            connection.commit()
            
            return {
                'score': score,
                'total': total,
                'percentage': (score/total) * 100 if total > 0 else 0
            }
            
        finally:
            cursor.close()
            close_connection(connection)