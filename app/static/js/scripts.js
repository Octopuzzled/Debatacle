document.addEventListener('DOMContentLoaded', () => {
    // Check if lessonData is defined
    if (typeof window.lessonData === 'undefined') {
        console.error('Lesson data is not defined. Make sure it is properly passed from the server.');
        return;
    }

    // Store references to static elements
    const prevButton = document.getElementById('prevSlide');
    const nextButton = document.getElementById('nextSlide');
    const slideNumberSpan = document.getElementById('slideNumber');

    // Destructure lessonData safely with the new structure
    const { lessonId, currentSlide, totalSlides, baseUrl, updateProgressUrl } = window.lessonData;
    let currentSlideOrder = currentSlide;

    function updateSlide(newSlideOrder) {
        fetch(`/slides/api/slide/${lessonId}/${newSlideOrder}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Get current slideContent (needs to be inside here because it might change)
                const slideContent = document.getElementById('slideContent');
                if (!slideContent) {
                    console.error('Slide content element not found');
                    return;
                }

                // Create new slide div with proper attributes
                const slideDiv = document.createElement('div');
                slideDiv.id = 'slideContent';
                slideDiv.className = 'slide';
                slideDiv.setAttribute('data-slide-order', newSlideOrder);
                slideDiv.innerHTML = data.content;

                // Replace old slide
                slideContent.parentNode.replaceChild(slideDiv, slideContent);

                // Update navigation elements
                slideNumberSpan.textContent = `Slide ${newSlideOrder} of ${totalSlides}`;
                
                // Update button states
                prevButton.disabled = newSlideOrder <= 1;
                prevButton.classList.toggle('disabled', newSlideOrder <= 1);
                prevButton.setAttribute('aria-disabled', newSlideOrder <= 1);
                
                nextButton.disabled = newSlideOrder >= totalSlides;
                nextButton.classList.toggle('disabled', newSlideOrder >= totalSlides);
                nextButton.setAttribute('aria-disabled', newSlideOrder >= totalSlides);

                // Update URL without reloading - using the new baseUrl
                history.pushState(null, '', `${baseUrl}${newSlideOrder}`);

                // Update current slide order
                currentSlideOrder = newSlideOrder;

                // Update progress
                updateProgress(newSlideOrder);

                // Important: Add active class after a brief delay
                setTimeout(() => {
                    slideDiv.classList.add('active');
                    // Add rounded class for styling
                    slideDiv.classList.add('p-4', 'rounded');
                    
                    // Manually trigger quiz check on last slide
                    if (newSlideOrder === totalSlides) {
                        const event = new CustomEvent('slideChanged', {
                            detail: { currentSlide: newSlideOrder, totalSlides: totalSlides }
                        });
                        document.dispatchEvent(event);
                    }
                }, 0);

                // Update progress bar
                const progressBar = document.querySelector('.progress-bar');
                if (progressBar) {
                    const progressPercent = (newSlideOrder / totalSlides * 100).toFixed(0);
                    progressBar.style.width = `${progressPercent}%`;
                    progressBar.setAttribute('aria-valuenow', newSlideOrder);
                }
            })
            .catch(error => console.error('Error updating slide:', error));
    }

    // Attach click handlers using event delegation
    document.addEventListener('click', (event) => {
        if (event.target.closest('#prevSlide:not(.disabled)')) {
            if (currentSlideOrder > 1) {
                updateSlide(currentSlideOrder - 1);
            }
        } else if (event.target.closest('#nextSlide:not(.disabled)')) {
            if (currentSlideOrder < totalSlides) {
                updateSlide(currentSlideOrder + 1);
            }
        }
    });

    function updateProgress(slideOrder) {
        // Construct the URL in JavaScript instead of relying on Flask's url_for
        fetch(`/slides/api/update-progress/${lessonId}/${slideOrder}`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => console.log('Progress updated:', data))
            .catch(error => console.error('Error updating progress:', error));
    }

    // Add keyboard navigation
    document.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowLeft' && !prevButton.disabled) {
            if (currentSlideOrder > 1) {
                updateSlide(currentSlideOrder - 1);
            }
        } else if (event.key === 'ArrowRight' && !nextButton.disabled) {
            if (currentSlideOrder < totalSlides) {
                updateSlide(currentSlideOrder + 1);
            }
        }
    });

    // Add popstate listener
    window.addEventListener('popstate', (event) => {
        const currentPath = window.location.pathname.split('/');
        const slideOrder = parseInt(currentPath[currentPath.length - 1]);

        if (!isNaN(slideOrder)) {
            updateSlide(slideOrder);
        }
    });

    // Initialize the first slide's state
    const initialSlide = document.getElementById('slideContent');
    if (initialSlide) {
        initialSlide.classList.add('slide', 'active', 'p-4', 'rounded');
        initialSlide.setAttribute('data-slide-order', currentSlide);
    }
});