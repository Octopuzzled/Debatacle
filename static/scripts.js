document.addEventListener('DOMContentLoaded', function() {
    const content = document.querySelector('.lesson-content');
    const parts = document.querySelectorAll('.lesson-part');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const prevTitle = document.getElementById('prev-title');
    const nextTitle = document.getElementById('next-title');
    const currentTitle = document.getElementById('current-title');
    let currentPart = 0;

    function updateNavigation() {
        prevBtn.disabled = currentPart === 0;
        nextBtn.disabled = currentPart === parts.length - 1;

        parts.forEach((part, index) => {
            if (index === currentPart) {
                part.classList.add('active');
            } else {
                part.classList.remove('active');
            }
        });

        prevTitle.textContent = currentPart > 0 ? parts[currentPart - 1].dataset.title : '';
        nextTitle.textContent = currentPart < parts.length - 1 ? parts[currentPart + 1].dataset.title : '';
        currentTitle.textContent = parts[currentPart].dataset.title;

        prevBtn.parentElement.style.visibility = currentPart > 0 ? 'visible' : 'hidden';
        nextBtn.parentElement.style.visibility = currentPart < parts.length - 1 ? 'visible' : 'hidden';
    }

    function saveProgress() {
        // Assuming you're tracking the current lesson name and part number
        const lessonName = content.dataset.lessonName;  // Assuming this is set in the HTML
        const partNumber = currentPart;

        // Make an AJAX request to save progress
        fetch('/save_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lesson_name: lessonName,
                last_page: partNumber
            })
        })
        .then(response => {
            if (!response.ok) {
                console.error('Failed to save progress.');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    prevBtn.addEventListener('click', function() {
        if (currentPart > 0) {
            currentPart--;
            updateNavigation();
            saveProgress();  // Save progress after navigating
        }
    });

    nextBtn.addEventListener('click', function() {
        if (currentPart < parts.length - 1) {
            currentPart++;
            updateNavigation();
            saveProgress();  // Save progress after navigating
        }
    });

    updateNavigation();
});
