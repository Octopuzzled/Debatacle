// Code for lesson slides
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

    // Destructure lessonData safely
    const { lessonId, currentSlide, totalSlides } = window.lessonData;
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
                prevButton.disabled = newSlideOrder <= 1;
                nextButton.disabled = newSlideOrder >= totalSlides;

                // Update URL without reloading
                history.pushState(null, '', `/lessons/learn-logic/${lessonId}/${newSlideOrder}`);

                // Update current slide order
                currentSlideOrder = newSlideOrder;

                // Update progress
                updateProgress(newSlideOrder);

                // Important: Add active class after a brief delay
                setTimeout(() => {
                    slideDiv.classList.add('active');
                    // Manually trigger quiz check on last slide
                    if (newSlideOrder === totalSlides) {
                        const event = new CustomEvent('slideChanged', {
                            detail: { currentSlide: newSlideOrder, totalSlides: totalSlides }
                        });
                        document.dispatchEvent(event);
                    }
                }, 0);
            })
            .catch(error => console.error('Error updating slide:', error));
    }

    // Attach click handlers using event delegation
    document.addEventListener('click', (event) => {
        if (event.target.id === 'prevSlide' && !event.target.disabled) {
            if (currentSlideOrder > 1) {
                updateSlide(currentSlideOrder - 1);
            }
        } else if (event.target.id === 'nextSlide' && !event.target.disabled) {
            if (currentSlideOrder < totalSlides) {
                updateSlide(currentSlideOrder + 1);
            }
        }
    });

    function updateProgress(slideOrder) {
        fetch(`/slides/api/update-progress/${lessonId}/${slideOrder}`, { method: 'POST' })
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

    // Initialize the first slide's state
    const initialSlide = document.getElementById('slideContent');
    if (initialSlide) {
        initialSlide.className = 'slide active';
        initialSlide.setAttribute('data-slide-order', currentSlide);
    }
});