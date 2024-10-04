// Get the lesson container and slides
const lessonContainer = document.querySelector('.lesson-container');
const slides = lessonContainer.querySelectorAll('[data-title]');

// Add navigation buttons
const prevButton = document.createElement('button');
prevButton.textContent = 'Previous';
prevButton.classList.add('prev-button');

const nextButton = document.createElement('button');
nextButton.textContent = 'Next';
nextButton.classList.add('next-button');

// Add event listeners to navigation buttons
prevButton.addEventListener('click', () => {
  const currentSlide = lessonContainer.querySelector('.active');
  const prevSlide = currentSlide.previousElementSibling;
  if (prevSlide) {
    currentSlide.classList.remove('active');
    prevSlide.classList.add('active');
  }
});

nextButton.addEventListener('click', () => {
  const currentSlide = lessonContainer.querySelector('.active');
  const nextSlide = currentSlide.nextElementSibling;
  if (nextSlide) {
    currentSlide.classList.remove('active');
    nextSlide.classList.add('active');
  }
});

// Add navigation buttons to the lesson container
lessonContainer.appendChild(prevButton);
lessonContainer.appendChild(nextButton);

// Update user progress
function updateProgress(user_id, lesson_name, page_number) {
  fetch("/update_progress", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `user_id=${user_id}&lesson_name=${lesson_name}&page_number=${page_number}`
  })
  .then(response => response.text())
  .then(message => console.log(message));
}

// Get user progress
function getProgress(user_id) {
  fetch(`/get_progress?user_id=${user_id}`)
  .then(response => response.json())
  .then(progress => console.log(progress));
}

// Continue lesson
function continueLesson(user_id, lesson_name) {
  fetch(`/continue_lesson?user_id=${user_id}&lesson_name=${lesson_name}`)
  .then(response => response.text())
  .then(message => console.log(message));
}

// Set the first slide as active
slides[0].classList.add('active');