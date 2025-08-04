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

    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateY = ((x - centerX) / centerX) * 8;
            const rotateX = ((centerY - y) / centerY) * 8;
            card.style.transform = `scale(1.05) rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'scale(1) rotateY(0deg) rotateX(0deg)';
        });
    });
});