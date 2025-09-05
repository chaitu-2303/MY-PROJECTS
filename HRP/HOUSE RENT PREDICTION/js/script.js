// JavaScript for Rent Right Front-end

// Mobile navigation toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');

if (navToggle) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('nav-menu_visible');
        navToggle.classList.toggle('nav-toggle_active');
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Placeholder for Rent Prediction form submission
const rentPredictionForm = document.querySelector('.rent-prediction-form');
if (rentPredictionForm) {
    rentPredictionForm.addEventListener('submit', function (e) {
        e.preventDefault();
        alert('Rent prediction feature coming soon!');
    });
}
