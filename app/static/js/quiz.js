// I' bad with JS whenever it doesn't look like Python or C or Java. So AI had to help me a lot with the entire JS code.

// Define the Quiz class
class Quiz {
    constructor(lessonId) {
        this.lessonId = lessonId;
        this.currentQuestion = 0;
        this.userAnswers = [];
        this.quizData = null;
    }

    async loadQuiz() {
        console.log('Attempting to load quiz for lesson ID:', this.lessonId);
        try {
            const response = await fetch('/api/quiz/lesson/' + this.lessonId + '/quiz');
            console.log('Response status:', response.status);
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error data:', errorData);
                throw new Error('Failed to load quiz: ' + (errorData.error || 'Unknown error'));
            }
            this.quizData = await response.json();
            console.log('Quiz data:', this.quizData);
            this.renderQuestion();
        } catch (error) {
            console.error('Error loading quiz:', error);
            const quizContainer = document.getElementById('quiz-container');
            quizContainer.innerHTML = '<div class="quiz-error">' +
                '<p>Sorry, there was an error loading the quiz: ' + error.message + '</p>' +
                '</div>';
        }
    }

    renderQuestion() {
        if (!this.quizData || !this.quizData.questions.length) {
            console.error('No quiz data available');
            return;
        }
        
        const question = this.quizData.questions[this.currentQuestion];
        const quizContainer = document.getElementById('quiz-container');
        const previousAnswer = this.userAnswers[this.currentQuestion];
        
        // Build choices HTML
        let choicesHtml = '';
        question.choices.forEach(choice => {
            const selectedClass = previousAnswer === choice.id ? 'selected' : '';
            choicesHtml += '<button class="choice-btn ' + selectedClass + '" ' +
                          'data-choice-id="' + choice.id + '">' +
                          choice.text + '</button>';
        });

        // Build navigation HTML
        let navigationHtml = '<div class="navigation">';
        if (this.currentQuestion > 0) {
            navigationHtml += '<button class="prev-btn">Previous</button>';
        }
        if (this.currentQuestion < this.quizData.questions.length - 1) {
            navigationHtml += '<button class="next-btn"' + (!previousAnswer ? ' disabled' : '') + '>Next</button>';
        } else {
            navigationHtml += '<button class="submit-btn"' + (!previousAnswer ? ' disabled' : '') + '>Submit Quiz</button>';
        }
        navigationHtml += '</div>';

        // Combine all HTML
        quizContainer.innerHTML = 
            '<div class="quiz-question">' +
            '<div class="question-progress">Question ' + 
            (this.currentQuestion + 1) + ' of ' + this.quizData.questions.length + '</div>' +
            '<h3>' + question.text + '</h3>' +
            '<div class="choices">' + choicesHtml + '</div>' +
            navigationHtml +
            '</div>';

        this.attachEventListeners();
    }

    attachEventListeners() {
        const choiceButtons = document.querySelectorAll('.choice-btn');
        choiceButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.selectAnswer(button.dataset.choiceId);
            });
        });

        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        const submitBtn = document.querySelector('.submit-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousQuestion());
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextQuestion());
        }
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitQuiz());
        }
    }

    selectAnswer(choiceId) {
        this.userAnswers[this.currentQuestion] = choiceId;
        
        document.querySelectorAll('.choice-btn').forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.choiceId === choiceId) {
                btn.classList.add('selected');
            }
        });

        const nextBtn = document.querySelector('.next-btn');
        const submitBtn = document.querySelector('.submit-btn');
        if (nextBtn) nextBtn.disabled = false;
        if (submitBtn) submitBtn.disabled = false;
    }

    previousQuestion() {
        if (this.currentQuestion > 0) {
            this.currentQuestion--;
            this.renderQuestion();
        }
    }

    nextQuestion() {
        if (this.currentQuestion < this.quizData.questions.length - 1) {
            this.currentQuestion++;
            this.renderQuestion();
        }
    }

    async submitQuiz() {
        if (this.userAnswers.length !== this.quizData.questions.length) {
            alert('Please answer all questions before submitting.');
            return;
        }

        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: document.querySelector('[data-user-id]').dataset.userId,
                    quiz_id: this.quizData.quiz_id,
                    answers: this.userAnswers.map((choiceId, index) => ({
                        question_id: this.quizData.questions[index].id,
                        choice_id: choiceId
                    }))
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit quiz');
            }

            const result = await response.json();
            this.showResults(result);
        } catch (error) {
            console.error('Error submitting quiz:', error);
            alert('There was an error submitting your quiz. Please try again.');
        }
    }

    showResults(result) {
        const quizContainer = document.getElementById('quiz-container');
        const message = this.getResultMessage(result.percentage);
        
        quizContainer.innerHTML = 
            '<div class="quiz-results">' +
            '<h2>Quiz Results</h2>' +
            '<div class="score-details">' +
            '<p>You scored: ' + result.score + ' out of ' + result.total + '</p>' +
            '<p>Percentage: ' + result.percentage.toFixed(1) + '%</p>' +
            '</div>' +
            '<div class="result-message">' + message + '</div>' +
            '<button class="retry-btn" onclick="location.reload()">Try Again</button>' +
            '</div>';
    }

    getResultMessage(percentage) {
        if (percentage >= 90) {
            return 'Excellent! You\'ve mastered this material!';
        } else if (percentage >= 70) {
            return 'Good job! You have a solid understanding of the material.';
        } else if (percentage >= 50) {
            return 'You passed! Consider reviewing some of the material to improve your understanding.';
        } else {
            return 'You might want to review the material and try again.';
        }
    }
}

// Initialize quiz functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Quiz script loaded');
    const lessonContainer = document.querySelector('[data-lesson-id]');
    console.log('Lesson container:', lessonContainer);
    if (!lessonContainer) {
        console.error('Could not find lesson container');
        return;
    }

    const lessonId = lessonContainer.dataset.lessonId;
    console.log('Lesson ID:', lessonId);
    
    function checkForQuiz() {
        console.log('Checking for quiz...');
        const currentSlide = document.querySelector('.slide.active');
        console.log('Current slide:', currentSlide);
        if (!currentSlide) return;

        const currentSlideOrder = parseInt(currentSlide.dataset.slideOrder);
        const totalSlides = parseInt(document.querySelector('[data-total-slides]').dataset.totalSlides);
        console.log('Current slide order:', currentSlideOrder, 'Total slides:', totalSlides);

        if (currentSlideOrder === totalSlides) {
            console.log('Last slide detected');
            if (!currentSlide.querySelector('#quiz-container')) {
                console.log('Creating quiz container');
                const quizContainer = document.createElement('div');
                quizContainer.id = 'quiz-container';
                currentSlide.appendChild(quizContainer);

                const quiz = new Quiz(lessonId);
                quiz.loadQuiz();
            }
        }
    }

    // Listen for slide changes
    document.addEventListener('slideChanged', (event) => {
        console.log('Slide changed event received:', event.detail);
        checkForQuiz();
    });

    // Initial check
    checkForQuiz();
});