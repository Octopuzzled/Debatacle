document.addEventListener('DOMContentLoaded', () => {
  // Check if lessonData is defined
  if (typeof window.lessonData === 'undefined') {
      console.error('Lesson data is not defined. Make sure it is properly passed from the server.');
      return;
  }

  const slideContent = document.getElementById('slideContent');
  const prevButton = document.getElementById('prevSlide');
  const nextButton = document.getElementById('nextSlide');
  const slideNumberSpan = document.getElementById('slideNumber');

  // Destructure lessonData safely
  const { lessonId, currentSlide, totalSlides } = window.lessonData;
  let currentSlideOrder = currentSlide;

  function updateSlide(newSlideOrder) {
      fetch(`/api/slide/${lessonId}/${newSlideOrder}`)
          .then(response => {
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              return response.json();
          })
          .then(data => {
              slideContent.innerHTML = data.content;
              slideNumberSpan.textContent = `Slide ${newSlideOrder} of ${totalSlides}`;
              prevButton.disabled = newSlideOrder <= 1;
              nextButton.disabled = newSlideOrder >= totalSlides;

              // Update the URL without reloading the page
              history.pushState(null, '', `/learn-logic/${lessonId}/${newSlideOrder}`);

              // Update current slide order
              currentSlideOrder = newSlideOrder;

              // Update progress
              updateProgress(newSlideOrder);
          })
          .catch(error => console.error('Error updating slide:', error));
  }

  prevButton.addEventListener('click', () => {
      if (currentSlideOrder > 1) {
          updateSlide(currentSlideOrder - 1);
      }
  });

  nextButton.addEventListener('click', () => {
      if (currentSlideOrder < totalSlides) {
          updateSlide(currentSlideOrder + 1);
      }
  });

  function updateProgress(slideOrder) {
      fetch(`/api/update-progress/${lessonId}/${slideOrder}`, { method: 'POST' })
          .then(response => {
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              return response.json();
          })
          .then(data => console.log('Progress updated:', data))
          .catch(error => console.error('Error updating progress:', error));
  }

  // Add popstate listener
  window.addEventListener('popstate', (event) => {
      const currentPath = window.location.pathname.split('/');
      const slideOrder = parseInt(currentPath[currentPath.length - 1]);

      if (!isNaN(slideOrder)) {
          updateSlide(slideOrder);
      }
  });
});
