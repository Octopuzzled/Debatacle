from app.db_connection import get_connection

def get_user_progress(user_id):
    connection = get_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor(dictionary=True) # dictionary idea from AI
        cursor.execute("""
            SELECT lesson_id, slide_order 
            FROM user_progress 
            WHERE user_id = %s
            ORDER BY last_viewed DESC
            LIMIT 1
        """, (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()