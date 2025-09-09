// Main JavaScript for House Rent Prediction

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS Animation Library
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('bg-white', 'shadow');
            } else {
                navbar.classList.remove('bg-white', 'shadow');
            }
        });
    }

    // Property search form validation
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const location = document.getElementById('location');
            const propertyType = document.getElementById('property-type');
            
            if (location && location.value.trim() === '') {
                e.preventDefault();
                showAlert('Please enter a location', 'danger');
            }
            
            if (propertyType && propertyType.value === '') {
                e.preventDefault();
                showAlert('Please select a property type', 'danger');
            }
        });
    }

    // Initialize property sliders if any
    if (typeof Swiper !== 'undefined') {
        const propertySwiper = new Swiper('.property-slider', {
            slidesPerView: 1,
            spaceBetween: 30,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                640: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            },
        });

        // Testimonial slider
        const testimonialSwiper = new Swiper('.testimonial-slider', {
            slidesPerView: 1,
            spaceBetween: 30,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                640: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            },
        });
    }

    // Rent prediction form validation
    const predictionForm = document.querySelector('.prediction-form');
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            const requiredFields = predictionForm.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (field.value.trim() === '') {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please fill all required fields', 'danger');
            }
        });
    }

    // Contact form validation
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const message = document.getElementById('message');
            let isValid = true;
            
            if (name && name.value.trim() === '') {
                isValid = false;
                name.classList.add('is-invalid');
            } else if (name) {
                name.classList.remove('is-invalid');
            }
            
            if (email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email.value)) {
                    isValid = false;
                    email.classList.add('is-invalid');
                } else {
                    email.classList.remove('is-invalid');
                }
            }
            
            if (message && message.value.trim() === '') {
                isValid = false;
                message.classList.add('is-invalid');
            } else if (message) {
                message.classList.remove('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please check your inputs and try again', 'danger');
            }
        });
    }

    // Login form validation
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            let isValid = true;
            
            if (email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email.value)) {
                    isValid = false;
                    email.classList.add('is-invalid');
                } else {
                    email.classList.remove('is-invalid');
                }
            }
            
            if (password && password.value.trim() === '') {
                isValid = false;
                password.classList.add('is-invalid');
            } else if (password) {
                password.classList.remove('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please check your credentials and try again', 'danger');
            }
        });
    }

    // Registration form validation
    const registerForm = document.querySelector('.register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            let isValid = true;
            
            if (name && name.value.trim() === '') {
                isValid = false;
                name.classList.add('is-invalid');
            } else if (name) {
                name.classList.remove('is-invalid');
            }
            
            if (email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email.value)) {
                    isValid = false;
                    email.classList.add('is-invalid');
                } else {
                    email.classList.remove('is-invalid');
                }
            }
            
            if (password && password.value.trim().length < 8) {
                isValid = false;
                password.classList.add('is-invalid');
                showAlert('Password must be at least 8 characters', 'danger');
            } else if (password) {
                password.classList.remove('is-invalid');
            }
            
            if (confirmPassword && password && confirmPassword.value !== password.value) {
                isValid = false;
                confirmPassword.classList.add('is-invalid');
                showAlert('Passwords do not match', 'danger');
            } else if (confirmPassword) {
                confirmPassword.classList.remove('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Property listing form validation
    const listingForm = document.querySelector('.property-listing-form');
    if (listingForm) {
        listingForm.addEventListener('submit', function(e) {
            const requiredFields = listingForm.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (field.value.trim() === '') {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please fill all required fields', 'danger');
            }
        });
    }

    // Alert function
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container') || document.body;
        const firstChild = container.firstChild;
        container.insertBefore(alertDiv, firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    if (typeof bootstrap !== 'undefined') {
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Back to top button
    const backToTopBtn = document.querySelector('.back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('active');
            } else {
                backToTopBtn.classList.remove('active');
            }
        });
        
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Animate elements on scroll
    const animateElements = document.querySelectorAll('.fade-up');
    if (animateElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, { threshold: 0.1 });
        
        animateElements.forEach(element => {
            observer.observe(element);
        });
    }
});