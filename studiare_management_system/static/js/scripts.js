let currentSection = 0;
const sectionsContainer = document.getElementById('sections-container');
const sections = document.querySelectorAll('section');

// This function handles the horizontal navigation
function moveSection(direction) {
    currentSection += direction;

    // Loop back if we reach the end or beginning
    if (currentSection < 0) {
        currentSection = sections.length - 1; // Go to the last section
    } else if (currentSection >= sections.length) {
        currentSection = 0; // Go back to the first section
    }

    // Update the transform property to move the sections
    sectionsContainer.style.transform = `translateX(-${currentSection * 100}vw)`;
}
