from app.db_connection import get_connection, close_connection

def add_quiz(lesson_id: int, title: str, questions: list) -> bool:
    """Add or update a quiz for a specific lesson"""
    connection = get_connection()
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        # Check if quiz exists
        cursor.execute("""
            SELECT quiz_id FROM quizzes 
            WHERE lesson_id = %s
        """, (lesson_id,))
        
        existing_quiz = cursor.fetchone()
        
        if existing_quiz:
            print(f"Quiz already exists for lesson {lesson_id}. Deleting old quiz...")
            # Delete old quiz (this will cascade to questions and choices)
            cursor.execute("DELETE FROM quizzes WHERE lesson_id = %s", (lesson_id,))
        
        # Insert new quiz
        cursor.execute("""
            INSERT INTO quizzes (lesson_id, title)
            VALUES (%s, %s)
        """, (lesson_id, title))
        
        quiz_id = cursor.lastrowid
        
        # Insert questions and choices
        for question in questions:
            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, question_text)
                VALUES (%s, %s)
            """, (quiz_id, question['text']))
            
            question_id = cursor.lastrowid
            
            # Insert choices for this question
            for choice in question['choices']:
                cursor.execute("""
                    INSERT INTO question_choices 
                    (question_id, choice_text, is_correct)
                    VALUES (%s, %s, %s)
                """, (question_id, choice['text'], choice['is_correct']))
        
        connection.commit()
        print("Quiz added/updated successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding/updating quiz: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        close_connection(connection)

if __name__ == "__main__":
    # Define your quiz here
    quiz1 = {
        'lesson_id': 1,  # Change this to your lesson ID
        'title': 'Introduction Quiz',  # Change this to your quiz title
        'questions': [
        {
            'text': 'What are the two main components of an argument?',
            'choices': [
                {'text': 'Claims and evidence', 'is_correct': False},
                {'text': 'Premises and conclusions', 'is_correct': True},
                {'text': 'Facts and opinions', 'is_correct': False},
                {'text': 'Questions and answers', 'is_correct': False}
            ]
        },
        {
            'text': 'What is the difference between a valid and a sound argument?',
            'choices': [
                {'text': 'A valid argument has true premises, while a sound argument has a true conclusion.', 'is_correct': False},
                {'text': 'A valid argument has a conclusion that logically follows from its premises, while a sound argument has both a valid form and true premises.', 'is_correct': True},
                {'text': 'A valid argument is based on evidence, while a sound argument is based on logic.', 'is_correct': False},
                {'text': 'A valid argument is persuasive, while a sound argument is factual.', 'is_correct': False}
            ]
        },
        {
            'text': 'Which of the following is an example of a proposition?',
            'choices': [
                {'text': '"Go away!"', 'is_correct': False},
                {'text': '"I am hungry."', 'is_correct': False},
                {'text': '"The sky is blue."', 'is_correct': True},
                {'text': '"What time is it?"', 'is_correct': False}
            ]
        },
        {
            'text': 'Which of the following is an example of a deductive argument?',
            'choices': [
                {'text': 'Every time I eat peanuts, I get a rash. Therefore, peanuts cause rashes.', 'is_correct': False},
                {'text': 'All mammals are warm-blooded. Dogs are mammals. Therefore, dogs are warm-blooded.', 'is_correct': True},
                {'text': 'Most birds can fly. Sparrows are birds. Therefore, sparrows can fly.', 'is_correct': False},
                {'text': 'The sun has risen every day so far. Therefore, the sun will rise tomorrow.', 'is_correct': False}
            ]
        },
        {
            'text': 'What is the primary goal of an argument?',
            'choices': [
                {'text': 'To persuade the listener to agree with a particular viewpoint.', 'is_correct': True},
                {'text': 'To provide information and facts.', 'is_correct': False},
                {'text': 'To entertain the audience.', 'is_correct': False},
                {'text': 'To provoke emotional responses.', 'is_correct': False}
            ]
        }
    ]
    }
    
    quiz2 = {
    'lesson_id': 2,
    'title': 'Validity and Soundness Quiz',
    'questions': [
        {
            'text': 'What makes an argument sound?',
            'choices': [
                {'text': 'It just needs to be valid', 'is_correct': False},
                {'text': 'It just needs to have true premises', 'is_correct': False},
                {'text': 'It needs to be valid AND have true premises', 'is_correct': True},
                {'text': 'It needs to be persuasive to the audience', 'is_correct': False}
            ]
        },
        {
            'text': 'Which of the following best describes validity in an argument?',
            'choices': [
                {'text': 'All the premises must be true', 'is_correct': False},
                {'text': 'The conclusion must be true', 'is_correct': False},
                {'text': 'The propositions must have a logical connection', 'is_correct': True},
                {'text': 'The argument must be persuasive', 'is_correct': False}
            ]
        },
        {
            'text': 'What is the key difference between deductive and inductive arguments?',
            'choices': [
                {'text': 'Deductive arguments must be true if premises are true, while inductive arguments are about likelihood', 'is_correct': True},
                {'text': 'Deductive arguments are about statistics, while inductive arguments are about logic', 'is_correct': False},
                {'text': 'Deductive arguments are always false, while inductive arguments are always true', 'is_correct': False},
                {'text': 'There is no real difference between them', 'is_correct': False}
            ]
        },
        {
            'text': 'In the "plains are mammals" example from the lecture, why is the argument valid but not sound?',
            'choices': [
                {'text': 'Because the conclusion is false', 'is_correct': False},
                {'text': 'Because the logical structure is correct but the first premise is false', 'is_correct': True},
                {'text': 'Because it has no logical connection', 'is_correct': False},
                {'text': 'Because all the premises are false', 'is_correct': False}
            ]
        },
        {
            'text': 'What type of argument is the SuperMario player example?',
            'choices': [
                {'text': 'A deductive argument', 'is_correct': False},
                {'text': 'An invalid argument', 'is_correct': False},
                {'text': 'An inductive argument', 'is_correct': True},
                {'text': 'A sound deductive argument', 'is_correct': False}
            ]
        }
    ]
    }
    
    quiz3 = {
    'lesson_id': 3,
    'title': 'Logical Structures Quiz',
    'questions': [
        {
            'text': 'What is the correct structure of a Modus Ponens?',
            'choices': [
                {'text': 'p -> q, q, therefore p', 'is_correct': False},
                {'text': 'p -> q, p, therefore q', 'is_correct': True},
                {'text': 'p -> q, -q, therefore -p', 'is_correct': False},
                {'text': 'p -> q, -p, therefore -q', 'is_correct': False}
            ]
        },
        {
            'text': 'In the Ludwig Spanish example, why is "understanding the word cajón" a necessary but not sufficient condition for Spanish fluency?',
            'choices': [
                {'text': 'Because understanding one word guarantees fluency', 'is_correct': False},
                {'text': 'Because you must know the word to be fluent, but knowing it alone doesn\'t make you fluent', 'is_correct': True},
                {'text': 'Because it is sufficient for basic Spanish knowledge', 'is_correct': False},
                {'text': 'Because it has nothing to do with Spanish fluency', 'is_correct': False}
            ]
        },
        {
            'text': 'What is the purpose of a reductio ad absurdum argument?',
            'choices': [
                {'text': 'To prove a premise is true by showing its consequences', 'is_correct': False},
                {'text': 'To show that an argument is valid by examining its structure', 'is_correct': False},
                {'text': 'To prove a premise is false by showing it leads to an absurd or contradictory conclusion', 'is_correct': True},
                {'text': 'To demonstrate that the conclusion follows logically from the premises', 'is_correct': False}
            ]
        },
        {
            'text': 'Why do we analyze the structure of arguments before examining their content?',
            'choices': [
                {'text': 'Because content is not important in arguments', 'is_correct': False},
                {'text': 'Because if the structure is invalid, we don\'t need to fact-check the content', 'is_correct': True},
                {'text': 'Because structure is more complicated than content', 'is_correct': False},
                {'text': 'Because content analysis takes too much time', 'is_correct': False}
            ]
        },
        {
            'text': 'What is the structure of a Modus Tollens?',
            'choices': [
                {'text': 'p -> q, p, therefore q', 'is_correct': False},
                {'text': 'p -> q, q, therefore p', 'is_correct': False},
                {'text': 'p -> q, -q, therefore -p', 'is_correct': True},
                {'text': 'p -> q, -p, therefore -q', 'is_correct': False}
            ]
        }
    ]
    }
    
    quiz4 = {
   'lesson_id': 4,
   'title': 'Logical Fallacies Quiz',
   'questions': [
       {
           'text': 'Which of the following is an example of an ad hominem fallacy?',
           'choices': [
               {'text': '"Your research on climate change is flawed because you received funding from oil companies"', 'is_correct': False},
               {'text': '"Your argument about immigration is invalid because you dropped out of college"', 'is_correct': True},
               {'text': '"This study\'s methodology has several major flaws"', 'is_correct': False},
               {'text': '"The data in your presentation contradicts official statistics"', 'is_correct': False}
           ]
       },
       {
           'text': 'What is the key characteristic of a straw man fallacy?',
           'choices': [
               {'text': 'Attacking the person making the argument', 'is_correct': False},
               {'text': 'Presenting only two extreme options', 'is_correct': False},
               {'text': 'Misrepresenting an argument to make it easier to attack', 'is_correct': True},
               {'text': 'Claiming something is true because it\'s popular', 'is_correct': False}
           ]
       },
       {
           'text': 'In the shopping mall example from the lecture, why is the job creation argument a red herring?',
           'choices': [
               {'text': 'Because job creation is not important', 'is_correct': False},
               {'text': 'Because it diverts attention from the original concerns about traffic and noise', 'is_correct': True},
               {'text': 'Because shopping malls don\'t create jobs', 'is_correct': False},
               {'text': 'Because it\'s an appeal to authority', 'is_correct': False}
           ]
       },
       {
           'text': 'Which fallacy assumes that one action will inevitably lead to a chain of negative consequences?',
           'choices': [
               {'text': 'False dichotomy', 'is_correct': False},
               {'text': 'Red herring', 'is_correct': False},
               {'text': 'Bandwagon fallacy', 'is_correct': False},
               {'text': 'Slippery slope', 'is_correct': True}
           ]
       },
       {
           'text': 'What is important to remember about logical fallacies?',
           'choices': [
               {'text': 'They are always used intentionally to deceive', 'is_correct': False},
               {'text': 'Only uneducated people use them', 'is_correct': False},
               {'text': 'They can be used both intentionally and unintentionally', 'is_correct': True},
               {'text': 'They are only found in formal debates', 'is_correct': False}
           ]
       }
    ]
    }
    
    # Add the quiz
    add_quiz(quiz1['lesson_id'], quiz1['title'], quiz1['questions'])
    add_quiz(quiz2['lesson_id'], quiz2['title'], quiz2['questions'])
    add_quiz(quiz3['lesson_id'], quiz3['title'], quiz3['questions'])
    add_quiz(quiz4['lesson_id'], quiz4['title'], quiz4['questions'])