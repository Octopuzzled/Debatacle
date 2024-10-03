document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.lesson-part');
    const content = document.querySelector('.lesson-content');
    const lessonName = content.dataset.lessonName;
    let currentSlide = 0;

    function saveProgress() {
        fetch('/save-progress', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ lessonName, slideId: slides[currentSlide].id }),
        })
        .catch(error => {
          console.error('Error saving progress:', error);
          alert('An error occurred while saving your progress. Please try again later.');
        });
      }

    function showSlide(index) {
        slides[currentSlide].classList.remove('active');
        slides[index].classList.add('active');
        currentSlide = index;
        saveProgress();
      }    
  
    fetch(`/get-progress/${lessonName}`)
      .then(response => response.json())
      .then(data => {
        if (data.slideId) {
          const slideIndex = Array.from(slides).findIndex(slide => slide.id === data.slideId);
          if (slideIndex !== -1) {
            showSlide(slideIndex);
          }
        }
      })
      .catch(error => {
        console.error('Error fetching progress:', error);
        alert('An error occurred while fetching your progress. Please try again later.');
      });
  
    // Navigation buttons
    document.getElementById('prev-btn').addEventListener('click', () => {
      if (currentSlide > 0) showSlide(currentSlide - 1);
    });
  
    document.getElementById('next-btn').addEventListener('click', () => {
      if (currentSlide < slides.length - 1) showSlide(currentSlide + 1);
    });
  });