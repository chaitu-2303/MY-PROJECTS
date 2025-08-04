document.addEventListener('DOMContentLoaded', function() {
    // Animate buttons on hover
    document.querySelectorAll('.btn-vibrant').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'scale(1.08)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'scale(1)';
        });
    });

    // Card fade-in animation
    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = 0;
        setTimeout(() => {
            card.style.transition = 'opacity 0.8s';
            card.style.opacity = 1;
        }, 200);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});