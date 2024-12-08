document.addEventListener("DOMContentLoaded", function () {
    const fadeElements = document.querySelectorAll('.fade-in, .fade-out');

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5, // Adjust to trigger animations earlier/later
    };

    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add fade-in and scaling effect when in view
                entry.target.classList.remove('fade-out');
                entry.target.classList.add('fade-in');
                entry.target.style.transform = 'scale(1.1)'; // Grow when visible
            } else {
                // Shrink and add fade-out when out of view
                entry.target.classList.remove('fade-in');
                entry.target.classList.add('fade-out');
                entry.target.style.transform = 'scale(0.9)'; // Shrink when not visible
            }
        });
    }, observerOptions);

    fadeElements.forEach(element => {
        fadeObserver.observe(element);
    });
});
