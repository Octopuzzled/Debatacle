# Debatacle

#### Video Demo

URL HERE

#### Description

The world is full of arguments. This web app helps you understand them with lectures and quizzes.
Final project for the CS50 online course.

## Features

- Lectures on argumentation theory, covering the basics of argumentation, types of arguments, and common fallacies.
- Quizzes to test your knowledge (currently single choice)
- Account registration for progress tracking with personal dashboard

## Technologies Used

- Python for backend
- Flask for backend
- MySQL for database
- HTML/CSS for frontend
- Bootstrap for styling
- JavaScript for client-side scripting

## File Structure

```
Debatacle/
├── app.py                       # Flask app
├── app/                         # Application package directory
│   ├── __init__.py              # Flask app initialization and blueprint registration
│   ├── db_connection.py         # Connection to databank and connection pooling
│   ├── blueprints/              # Blueprint directory
│   │   ├── admin/
│   │   │   ├── routes.py        # Admin routes for admin panel, including adding/editing/deleting lessons and slides
│   │   │   └── utils.py         # Get user progress
│   │   ├── api/
│   │   │   └── routes.py        # API routes for getting lessons and user progress
│   │   ├── auth/
│   │   │   ├── routes.py        # Authentication routes for user registration and login/logout
│   │   │   └── utils.py         # Hashing and verifying passwords, decorated functions
│   │   ├── dashboard/
│   │   │   ├── routes.py        # Personal user homepage with current progress
│   │   │   └── utils.py         # Get user progress
│   │   ├── lessons/
│   │   │   └── routes.py        # Routes for overview of existing lessons
│   │   ├── main/
│   │   │   └── routes.py        # Rendering index page
│   │   ├── quiz/
│   │   │   ├── routes.py        # Routes for quiz functionality (getting and submitting)
│   │   │   ├── quiz_handler.py  # Further quiz logic
│   │   │   └── add_quiz.py      # Script for adding new quizzes
│   │   └── slides/
│   │       └── routes.py        # Routes for slides
│   ├── static/
│   │   ├── css/                 # CSS files
│   │   ├── js/                  # JavaScript files
│   │   ├── images/              # Generated using AI: https://www.seaart.ai
│   │   └── templates/           # HTML templates for rendering pages
```

## Design Choices

### Database Design Choices

The database schema follows a relational model designed to support an educational platform with lessons, slides, and user progress tracking. Below are the key design decisions and their benefits:

#### Structure overview

```MySQL
-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);


-- Lessons table
CREATE TABLE lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    lesson_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
	total_slides INT
);

-- Slides table 
CREATE TABLE slides (
    slide_id INT AUTO_INCREMENT PRIMARY KEY,
    lesson_id INT NOT NULL,
    content TEXT NOT NULL,
    slide_order INT NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE
);

-- User progress table 
CREATE TABLE user_progress (
    user_id INT,
    lesson_id INT,
    last_slide_id INT,
    PRIMARY KEY (user_id, lesson_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    FOREIGN KEY (last_slide_id) REFERENCES slides(slide_id) ON DELETE SET NULL
);

-- User lesson completion table
CREATE TABLE lesson_completions (
    user_id INT,
    lesson_id INT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, lesson_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
);
```

#### Users table

- Unique identifier for each user, AUTO_INcrement for automatic ID generation
- UNIQUE constraints on username and email to prevent duplicates
- Seperated password salt and hash for secure password storage
- Added timestamps for user account tracking
- Included admin flag for role-based access control

#### Content tables

- Hierarchical structure with lessons containing multiple slides
- Used ON DELETE CASCADE to automatically remove slides when a lesson is deleted
- Implemented slide ordering through slide_order field
- Allowed for rich content storage using TEXT data type

#### Progress tracking

- Implemented a separate table for user progress to track completion status of lessons  
- Appropriate foreign key constraints for data integrity
- Timestamp tracking for completion dates

### Blueprint Architechture

The application uses a modular blueprint architecture to organize routes and functionality into separate modules. This design choice allows for better code organisation , reusability, and maintainability. Each module is responsible for a specific feature or functionality, making it easier to update or replace individual components.

### Error Handling

- Used both jsonify and own error page depending on use case

### Security Considerations

- Implemented secure password hashing using bcrypt
- Used parameterized queries to prevent SQL injection
- Login required decorator for protected routes
- Admin role verification for administrative functions

## Future Development

### Security Enhancements

1. Add CSRF protection using Flask-WTF
    - Would protect against cross-site request forgery attacks
    - Important for form submissions and state-changing requests
2. Other potential security improvements:
    - Rate limiting for login attempts
    - Password complexity requirements
    - Session timeout settings

### Additional Content and Features

- Argument builder: drag and drop application to build arguments and get feedback
- More lectures and quizzes
- User profiles and leaderboard
- forum for discussions and peer learning
- Markdown formatting in slide content
- Add support for different languages (German)
- Create system for feedback on lessons

## Challenges Faced

- Creating good design instead of just functionality
- JavaScript
- Working with MySQL in Visual Studio Code
- Working with databank without using the CS50 solution
- Implementing progress tracking: took several attempts to get it right
- Shifitng from the mindest of static content to working with the databank and JavaScript
- Changing links after implementing blueprints when project almost finished

## Contributing

AI was a great help in discussing ideas, finding and fixing bugs and especially in working with JavaScript. Frequently, I found bugs on my own but after having a long discussion with AI. The JavaScript code is heavily inspired by the code AI provided regarding more general examples. I also used the code AI provided as a starting point for my own code. I mostly worked with ChatGPT and Claude, occasionally with Gemini.
