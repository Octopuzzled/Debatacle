document.addEventListener('DOMContentLoaded', function() {
  const lessonSelect = document.getElementById('lessonSelect');
  const slideContent = document.getElementById('slideContent');
  const prevButton = document.getElementById('prevSlide');
  const nextButton = document.getElementById('nextSlide');
  const slideNumber = document.getElementById('slideNumber');

  let currentLesson = null;
  let currentSlides = [];
  let currentSlideIndex = 0;

  // Fetch lessons and populate the select dropdown
  fetch('/api/lessons')
      .then(response => response.json())
      .then(lessons => {
          lessons.forEach(lesson => {
              const option = document.createElement('option');
              option.value = lesson.lesson_id;
              option.textContent = lesson.lesson_name;
              lessonSelect.appendChild(option);
          });
      });

  // Event listener for lesson selection
  lessonSelect.addEventListener('change', function() {
      currentLesson = this.value;
      if (currentLesson) {
          fetchSlides(currentLesson);
      }
  });

  // Fetch slides for a lesson
  function fetchSlides(lessonId) {
      fetch(`/api/slides?lesson_id=${lessonId}`)
          .then(response => response.json())
          .then(slides => {
              currentSlides = slides;
              currentSlideIndex = 0;
              updateSlideDisplay();
          });
  }

  // Update the slide display
  function updateSlideDisplay() {
      if (currentSlides.length > 0) {
          slideContent.innerHTML = currentSlides[currentSlideIndex].content;
          slideNumber.textContent = `Slide ${currentSlideIndex + 1} of ${currentSlides.length}`;
          prevButton.disabled = currentSlideIndex === 0;
          nextButton.disabled = currentSlideIndex === currentSlides.length - 1;
          saveProgress();
      } else {
          slideContent.innerHTML = 'No slides available for this lesson.';
          slideNumber.textContent = '';
          prevButton.disabled = true;
          nextButton.disabled = true;
      }
  }

  // Event listeners for navigation buttons
  prevButton.addEventListener('click', function() {
      if (currentSlideIndex > 0) {
          currentSlideIndex--;
          updateSlideDisplay();
      }
  });

  nextButton.addEventListener('click', function() {
      if (currentSlideIndex < currentSlides.length - 1) {
          currentSlideIndex++;
          updateSlideDisplay();
      }
  });

  // Save user progress
  function saveProgress() {
      if (currentLesson && currentSlides.length > 0) {
          fetch('/api/progress', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  lesson_id: currentLesson,
                  slide_id: currentSlides[currentSlideIndex].slide_id
              }),
          });
      }
  }

  // Load user progress when the page loads
  fetch('/api/progress')
      .then(response => response.json())
      .then(progress => {
          if (progress.lesson_id && progress.slide_id) {
              lessonSelect.value = progress.lesson_id;
              fetchSlides(progress.lesson_id);
              // Find the index of the last viewed slide
              currentSlideIndex = currentSlides.findIndex(slide => slide.slide_id === progress.slide_id);
              if (currentSlideIndex === -1) currentSlideIndex = 0; // If not found, start from the beginning
              updateSlideDisplay();
          }
      });
});