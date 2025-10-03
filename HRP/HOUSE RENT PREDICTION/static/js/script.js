// Initialize AOS Animation Library
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS if it exists
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('bg-white', 'shadow-sm');
            } else {
                navbar.classList.remove('bg-white', 'shadow-sm');
            }
        });
    }

    // Property Search Form Validation
    const propertySearchForm = document.getElementById('propertySearchForm');
    if (propertySearchForm) {
        // Real-time validation
        const location = document.getElementById('location');
        const propertyType = document.getElementById('propertyType');
        
        // Add input event listeners for real-time validation
        if (location) {
            location.addEventListener('input', function() {
                validateField(location, location.value.trim() !== '', 'Please enter a location');
            });
        }
        
        if (propertyType) {
            propertyType.addEventListener('change', function() {
                validateField(propertyType, propertyType.value !== '', 'Please select a property type');
            });
        }
        
        // Form submission
        propertySearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Validate location
            if (location && !location.value.trim()) {
                showAlert('Please enter a location', 'danger');
                location.classList.add('is-invalid');
                isValid = false;
            } else if (location) {
                location.classList.remove('is-invalid');
            }

            // Validate property type
            if (propertyType && propertyType.value === '') {
                showAlert('Please select a property type', 'danger');
                propertyType.classList.add('is-invalid');
                isValid = false;
            } else if (propertyType) {
                propertyType.classList.remove('is-invalid');
            }

            if (isValid) {
                // Show loading indicator
                const submitBtn = propertySearchForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
                    submitBtn.disabled = true;
                }
                
                // AJAX request to search properties
                const formData = new FormData(propertySearchForm);
                const searchParams = new URLSearchParams(formData);
                
                fetch(`/api/properties/search?${searchParams.toString()}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Handle successful search results
                    window.location.href = `/properties?${searchParams.toString()}`;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred while searching. Please try again.', 'danger');
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                });
            }
        });
    }
    
    // Helper function for field validation
    function validateField(field, condition, errorMessage) {
        if (!field) return true; // Skip if field doesn't exist
        
        const feedbackElement = field.nextElementSibling;
        if (condition) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                feedbackElement.textContent = '';
            }
            return true;
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                feedbackElement.textContent = errorMessage;
            } else {
                const feedback = document.createElement('div');
                feedback.classList.add('invalid-feedback');
                feedback.textContent = errorMessage;
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
            return false;
        }
    }

    // Initialize Swiper for Properties
    const propertiesSwiper = new Swiper('.properties-swiper', {
        slidesPerView: 1,
        spaceBetween: 30,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
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

    // Initialize Swiper for Testimonials
    const testimonialsSwiper = new Swiper('.testimonials-swiper', {
        slidesPerView: 1,
        spaceBetween: 30,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
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

    // Contact Form Validation
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        // Get form fields
        const name = document.getElementById('name');
        const email = document.getElementById('email');
        const message = document.getElementById('message');
        const subject = document.getElementById('subject'); // Optional field
        
        // Add real-time validation
        if (name) {
            name.addEventListener('input', function() {
                validateField(name, name.value.trim() !== '', 'Please enter your name');
            });
        }
        
        if (email) {
            email.addEventListener('input', function() {
                validateField(email, validateEmail(email.value), 'Please enter a valid email address');
            });
        }
        
        if (message) {
            message.addEventListener('input', function() {
                validateField(message, message.value.trim().length >= 10, 'Please enter a message (at least 10 characters)');
            });
        }
        
        if (subject) {
            subject.addEventListener('input', function() {
                if (subject.value.trim() !== '') {
                    validateField(subject, subject.value.trim() !== '', 'Please enter a subject');
                }
            });
        }
        
        // Form submission
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Validate name
            if (name) {
                isValid = validateField(name, name.value.trim() !== '', 'Please enter your name') && isValid;
            }

            // Validate email
            if (email) {
                isValid = validateField(email, validateEmail(email.value), 'Please enter a valid email address') && isValid;
            }

            // Validate message
            if (message) {
                isValid = validateField(message, message.value.trim().length >= 10, 'Please enter a message (at least 10 characters)') && isValid;
            }
            
            // Validate subject if provided
            if (subject && subject.value.trim() !== '') {
                isValid = validateField(subject, subject.value.trim() !== '', 'Please enter a subject') && isValid;
            }

            if (isValid) {
                // Show loading indicator
                const submitBtn = contactForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
                    submitBtn.disabled = true;
                }
                
                // AJAX request to submit contact form
                const formData = new FormData(contactForm);
                
                fetch('/api/contact', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Handle successful form submission
                    showAlert('Your message has been sent successfully!', 'success');
                    contactForm.reset();
                    
                    // Reset validation classes
                    const formInputs = contactForm.querySelectorAll('.form-control');
                    formInputs.forEach(input => {
                        input.classList.remove('is-valid');
                    });
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred. Please try again later.', 'danger');
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                });
            } else {
                showAlert('Please fill in all required fields correctly.', 'danger');
            }
        });
    }

    // Login Form Validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        // Get form fields
        const email = document.getElementById('loginEmail');
        const password = document.getElementById('loginPassword');
        const rememberMe = document.getElementById('rememberMe'); // Optional checkbox
        
        // Add real-time validation
        if (email) {
            email.addEventListener('input', function() {
                validateField(email, validateEmail(email.value), 'Please enter a valid email address');
            });
        }
        
        if (password) {
            password.addEventListener('input', function() {
                validateField(password, password.value.trim().length >= 6, 'Password must be at least 6 characters');
            });
        }
        
        // Form submission
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Validate email
            if (email) {
                isValid = validateField(email, validateEmail(email.value), 'Please enter a valid email address') && isValid;
            }

            // Validate password
            if (password) {
                isValid = validateField(password, password.value.trim().length >= 6, 'Password must be at least 6 characters') && isValid;
            }

            if (isValid) {
                // Show loading indicator
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
                    submitBtn.disabled = true;
                }
                
                // AJAX request to login
                const formData = new FormData(loginForm);
                
                // Add remember me value if checkbox exists
                if (rememberMe) {
                    formData.set('remember_me', rememberMe.checked);
                }
                
                fetch('/api/auth/login', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Login failed');
                    }
                    return response.json();
                })
                .then(data => {
                    showAlert('Login successful!', 'success');
                    
                    // Reset validation classes
                    const formInputs = loginForm.querySelectorAll('.form-control');
                    formInputs.forEach(input => {
                        input.classList.remove('is-valid');
                    });
                    
                    // Redirect to dashboard or home page after a short delay
                    setTimeout(() => {
                        window.location.href = data.redirect_url || '/dashboard';
                    }, 1500);
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Invalid email or password. Please try again.', 'danger');
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                });
            } else {
                showAlert('Please fill in all required fields correctly.', 'danger');
            }
        });
    }

    // Registration Form Validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        // Get form fields
        const name = document.getElementById('registerName');
        const email = document.getElementById('registerEmail');
        const password = document.getElementById('registerPassword');
        const confirmPassword = document.getElementById('confirmPassword');
        const phone = document.getElementById('registerPhone'); // Optional field
        const terms = document.getElementById('registerTerms'); // Terms checkbox
        
        // Add real-time validation
        if (name) {
            name.addEventListener('input', function() {
                validateField(name, name.value.trim().length >= 2, 'Please enter your full name (at least 2 characters)');
            });
        }
        
        if (email) {
            email.addEventListener('input', function() {
                validateField(email, validateEmail(email.value), 'Please enter a valid email address');
            });
        }
        
        if (password) {
            password.addEventListener('input', function() {
                validateField(password, password.value.trim().length >= 8, 'Password must be at least 8 characters');
                // Also validate confirm password if it has a value
                if (confirmPassword && confirmPassword.value.trim()) {
                    validateField(confirmPassword, confirmPassword.value === password.value, 'Passwords do not match');
                }
            });
        }
        
        if (confirmPassword) {
            confirmPassword.addEventListener('input', function() {
                validateField(confirmPassword, confirmPassword.value === password.value, 'Passwords do not match');
            });
        }
        
        if (phone) {
            phone.addEventListener('input', function() {
                if (phone.value.trim()) {
                    validateField(phone, /^\d{10,15}$/.test(phone.value.replace(/[\s-()]/g, '')), 'Please enter a valid phone number');
                } else {
                    // Phone might be optional
                    phone.classList.remove('is-invalid');
                    phone.classList.remove('is-valid');
                }
            });
        }
        
        if (terms) {
            terms.addEventListener('change', function() {
                validateField(terms, terms.checked, 'You must agree to the terms and conditions');
            });
        }
        
        // Form submission
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Validate name
            if (name) {
                isValid = validateField(name, name.value.trim().length >= 2, 'Please enter your full name (at least 2 characters)') && isValid;
            }

            // Validate email
            if (email) {
                isValid = validateField(email, validateEmail(email.value), 'Please enter a valid email address') && isValid;
            }

            // Validate password
            if (password) {
                isValid = validateField(password, password.value.trim().length >= 8, 'Password must be at least 8 characters') && isValid;
            }

            // Validate confirm password
            if (confirmPassword) {
                isValid = validateField(confirmPassword, confirmPassword.value === password.value, 'Passwords do not match') && isValid;
            }
            
            // Validate phone if provided
            if (phone && phone.value.trim()) {
                isValid = validateField(phone, /^\d{10,15}$/.test(phone.value.replace(/[\s-()]/g, '')), 'Please enter a valid phone number') && isValid;
            }
            
            // Validate terms if provided
            if (terms) {
                isValid = validateField(terms, terms.checked, 'You must agree to the terms and conditions') && isValid;
            }

            if (isValid) {
                // Show loading indicator
                const submitBtn = registerForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';
                    submitBtn.disabled = true;
                }
                
                // AJAX request to register
                const formData = new FormData(registerForm);
                
                fetch('/api/auth/register', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.message || 'Registration failed');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    showAlert('Registration successful! Please check your email to verify your account.', 'success');
                    registerForm.reset();
                    
                    // Reset validation classes
                    const formInputs = registerForm.querySelectorAll('.form-control');
                    formInputs.forEach(input => {
                        input.classList.remove('is-valid');
                        input.classList.remove('is-invalid');
                    });
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                    
                    // Redirect if specified in response
                    if (data.redirect_url) {
                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 2000);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert(error.message || 'An error occurred during registration. Please try again.', 'danger');
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                });
            } else {
                showAlert('Please fill in all required fields correctly.', 'danger');
            }
        });
    }

    // Property Listing Form Validation
    const propertyListingForm = document.getElementById('propertyListingForm');
    if (propertyListingForm) {
        // Get form fields
        const title = document.getElementById('propertyTitle');
        const description = document.getElementById('propertyDescription');
        const price = document.getElementById('propertyPrice');
        const location = document.getElementById('propertyLocation');
        const propertyType = document.getElementById('propertyType');
        const bedrooms = document.getElementById('propertyBedrooms');
        const bathrooms = document.getElementById('propertyBathrooms');
        const area = document.getElementById('propertyArea');
        const images = document.getElementById('propertyImages');
        const amenities = document.querySelectorAll('input[name="amenities[]"]'); // Optional checkboxes
        
        // Add real-time validation
        if (title) {
            title.addEventListener('input', function() {
                validateField(title, title.value.trim().length >= 5, 'Please enter a descriptive title (at least 5 characters)');
            });
        }
        
        if (description) {
            description.addEventListener('input', function() {
                validateField(description, description.value.trim().length >= 20, 'Please enter a detailed description (at least 20 characters)');
            });
        }
        
        if (price) {
            price.addEventListener('input', function() {
                validateField(price, !isNaN(price.value) && parseFloat(price.value) > 0, 'Please enter a valid price greater than 0');
            });
        }
        
        if (location) {
            location.addEventListener('input', function() {
                validateField(location, location.value.trim().length >= 3, 'Please enter a valid location');
            });
        }
        
        if (propertyType) {
            propertyType.addEventListener('change', function() {
                validateField(propertyType, propertyType.value, 'Please select a property type');
            });
        }
        
        if (bedrooms) {
            bedrooms.addEventListener('input', function() {
                validateField(bedrooms, !isNaN(bedrooms.value) && parseInt(bedrooms.value) >= 0, 'Please enter a valid number of bedrooms');
            });
        }
        
        if (bathrooms) {
            bathrooms.addEventListener('input', function() {
                validateField(bathrooms, !isNaN(bathrooms.value) && parseInt(bathrooms.value) >= 0, 'Please enter a valid number of bathrooms');
            });
        }
        
        if (area) {
            area.addEventListener('input', function() {
                validateField(area, !isNaN(area.value) && parseFloat(area.value) > 0, 'Please enter a valid area in square feet');
            });
        }
        
        if (images) {
            images.addEventListener('change', function() {
                validateField(images, images.files.length > 0, 'Please select at least one image');
                
                // Validate file types and sizes
                if (images.files.length > 0) {
                    const maxFileSize = 5 * 1024 * 1024; // 5MB
                    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
                    let isValid = true;
                    
                    for (let i = 0; i < images.files.length; i++) {
                        const file = images.files[i];
                        if (!allowedTypes.includes(file.type)) {
                            isValid = false;
                            break;
                        }
                        if (file.size > maxFileSize) {
                            isValid = false;
                            break;
                        }
                    }
                    
                    validateField(images, isValid, 'Please select valid image files (JPG, PNG, WEBP) under 5MB each');
                }
            });
        }
        
        // Form submission
        propertyListingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Validate title
            if (title) {
                isValid = validateField(title, title.value.trim().length >= 5, 'Please enter a descriptive title (at least 5 characters)') && isValid;
            }

            // Validate description
            if (description) {
                isValid = validateField(description, description.value.trim().length >= 20, 'Please enter a detailed description (at least 20 characters)') && isValid;
            }

            // Validate price
            if (price) {
                isValid = validateField(price, !isNaN(price.value) && parseFloat(price.value) > 0, 'Please enter a valid price greater than 0') && isValid;
            }

            // Validate location
            if (location) {
                isValid = validateField(location, location.value.trim().length >= 3, 'Please enter a valid location') && isValid;
            }

            // Validate property type
            if (propertyType) {
                isValid = validateField(propertyType, propertyType.value, 'Please select a property type') && isValid;
            }

            // Validate bedrooms
            if (bedrooms) {
                isValid = validateField(bedrooms, !isNaN(bedrooms.value) && parseInt(bedrooms.value) >= 0, 'Please enter a valid number of bedrooms') && isValid;
            }

            // Validate bathrooms
            if (bathrooms) {
                isValid = validateField(bathrooms, !isNaN(bathrooms.value) && parseInt(bathrooms.value) >= 0, 'Please enter a valid number of bathrooms') && isValid;
            }

            // Validate area
            if (area) {
                isValid = validateField(area, !isNaN(area.value) && parseFloat(area.value) > 0, 'Please enter a valid area in square feet') && isValid;
            }

            // Validate images
            if (images) {
                isValid = validateField(images, images.files.length > 0, 'Please select at least one image') && isValid;
                
                // Validate file types and sizes
                if (images.files.length > 0) {
                    const maxFileSize = 5 * 1024 * 1024; // 5MB
                    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
                    let filesValid = true;
                    
                    for (let i = 0; i < images.files.length; i++) {
                        const file = images.files[i];
                        if (!allowedTypes.includes(file.type)) {
                            filesValid = false;
                            break;
                        }
                        if (file.size > maxFileSize) {
                            filesValid = false;
                            break;
                        }
                    }
                    
                    isValid = validateField(images, filesValid, 'Please select valid image files (JPG, PNG, WEBP) under 5MB each') && isValid;
                }
            }

            // Check if at least one amenity is selected (if amenities exist)
            if (amenities && amenities.length > 0) {
                let amenityChecked = false;
                amenities.forEach(function(amenity) {
                    if (amenity.checked) {
                        amenityChecked = true;
                    }
                });
                
                // Optional validation for amenities
                if (!amenityChecked) {
                    const amenitiesContainer = document.querySelector('.amenities-container');
                    if (amenitiesContainer) {
                        amenitiesContainer.classList.add('is-invalid');
                        const feedbackElement = amenitiesContainer.querySelector('.invalid-feedback');
                        if (feedbackElement) {
                            feedbackElement.textContent = 'Please select at least one amenity';
                        } else {
                            const feedback = document.createElement('div');
                            feedback.classList.add('invalid-feedback');
                            feedback.textContent = 'Please select at least one amenity';
                            amenitiesContainer.appendChild(feedback);
                        }
                        isValid = false;
                    }
                } else {
                    const amenitiesContainer = document.querySelector('.amenities-container');
                    if (amenitiesContainer) {
                        amenitiesContainer.classList.remove('is-invalid');
                    }
                }
            }

            if (isValid) {
                // Show loading indicator
                const submitBtn = propertyListingForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
                    submitBtn.disabled = true;
                }
                
                // AJAX request to submit property listing
                const formData = new FormData(propertyListingForm);
                
                fetch('/api/properties', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to submit property listing');
                    }
                    return response.json();
                })
                .then(data => {
                    showAlert('Property listing submitted successfully!', 'success');
                    propertyListingForm.reset();
                    
                    // Reset validation classes
                    const formInputs = propertyListingForm.querySelectorAll('.form-control');
                    formInputs.forEach(input => {
                        input.classList.remove('is-valid');
                        input.classList.remove('is-invalid');
                    });
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                    
                    // Redirect to the new property page after a short delay
                    setTimeout(() => {
                        window.location.href = `/properties/${data.id}`;
                    }, 1500);
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred while submitting your property listing. Please try again.', 'danger');
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                });
            } else {
                showAlert('Please fill in all required fields correctly.', 'danger');
            }
        });
    }

    // Rent Prediction Form
    const rentPredictionForm = document.getElementById('rentPredictionForm');
    if (rentPredictionForm) {
        // Get form fields
        const location = document.getElementById('location');
        const propertyType = document.getElementById('propertyType');
        const bedrooms = document.getElementById('bedrooms');
        const bathrooms = document.getElementById('bathrooms');
        const area = document.getElementById('area');
        const amenities = document.querySelectorAll('input[name="amenities[]"]'); // Optional checkboxes
        
        // Add real-time validation
        if (location) {
            location.addEventListener('input', function() {
                validateField(location, location.value.trim().length >= 3, 'Please enter a valid location');
            });
        }
        
        if (propertyType) {
            propertyType.addEventListener('change', function() {
                validateField(propertyType, propertyType.value, 'Please select a property type');
            });
        }
        
        if (bedrooms) {
            bedrooms.addEventListener('input', function() {
                validateField(bedrooms, !isNaN(bedrooms.value) && parseInt(bedrooms.value) >= 0, 'Please enter a valid number of bedrooms');
            });
        }
        
        if (bathrooms) {
            bathrooms.addEventListener('input', function() {
                validateField(bathrooms, !isNaN(bathrooms.value) && parseInt(bathrooms.value) >= 0, 'Please enter a valid number of bathrooms');
            });
        }
        
        if (area) {
            area.addEventListener('input', function() {
                validateField(area, !isNaN(area.value) && parseFloat(area.value) > 0, 'Please enter a valid area in square feet');
            });
        }
        
        // Form submission
        rentPredictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;

            // Validate location
            if (location) {
                isValid = validateField(location, location.value.trim().length >= 3, 'Please enter a valid location') && isValid;
            }

            // Validate property type
            if (propertyType) {
                isValid = validateField(propertyType, propertyType.value, 'Please select a property type') && isValid;
            }

            // Validate bedrooms
            if (bedrooms) {
                isValid = validateField(bedrooms, !isNaN(bedrooms.value) && parseInt(bedrooms.value) >= 0, 'Please enter a valid number of bedrooms') && isValid;
            }

            // Validate bathrooms
            if (bathrooms) {
                isValid = validateField(bathrooms, !isNaN(bathrooms.value) && parseInt(bathrooms.value) >= 0, 'Please enter a valid number of bathrooms') && isValid;
            }

            // Validate area
            if (area) {
                isValid = validateField(area, !isNaN(area.value) && parseFloat(area.value) > 0, 'Please enter a valid area in square feet') && isValid;
            }

            if (isValid) {
                // Show loading state and disable submit button
                const submitBtn = rentPredictionForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Predicting...';
                    submitBtn.disabled = true;
                }
                
                const predictionLoading = document.getElementById('predictionLoading');
                const predictionResult = document.getElementById('predictionResult');
                
                if (predictionLoading) {
                    predictionLoading.classList.remove('d-none');
                }
                
                if (predictionResult) {
                    predictionResult.classList.add('d-none');
                }
                
                // AJAX request for rent prediction
                const formData = new FormData(rentPredictionForm);
                
                // Add amenities if they exist
                if (amenities && amenities.length > 0) {
                    const selectedAmenities = [];
                    amenities.forEach(function(amenity) {
                        if (amenity.checked) {
                            selectedAmenities.push(amenity.value);
                        }
                    });
                    formData.set('amenities', selectedAmenities.join(','));
                }
                
                const searchParams = new URLSearchParams(formData);
                
                fetch(`/api/predict?${searchParams.toString()}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Prediction failed');
                    }
                    return response.json();
                })
                .then(data => {
                    // Hide loading state
                    if (predictionLoading) {
                        predictionLoading.classList.add('d-none');
                    }
                    
                    if (predictionResult) {
                        predictionResult.classList.remove('d-none');
                    }
                    
                    // Update prediction result
                    const predictedAmount = document.getElementById('predictedAmount');
                    const predictionAccuracy = document.getElementById('predictionAccuracy');
                    
                    if (predictedAmount) {
                        predictedAmount.textContent = `$${data.predicted_rent}`;
                    }
                    
                    if (predictionAccuracy) {
                        predictionAccuracy.textContent = `${data.accuracy}%`;
                    }
                    
                    // Add property details to the result
                    const predictionDetails = document.getElementById('predictionDetails');
                    if (predictionDetails) {
                        predictionDetails.innerHTML = `
                            <div class="mt-3">
                                <p><strong>Property Details:</strong></p>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-map-marker-alt me-2"></i> ${location.value}</li>
                                    <li><i class="fas fa-home me-2"></i> ${propertyType.options[propertyType.selectedIndex].text}</li>
                                    <li><i class="fas fa-bed me-2"></i> ${bedrooms.value} Bedrooms</li>
                                    <li><i class="fas fa-bath me-2"></i> ${bathrooms.value} Bathrooms</li>
                                    <li><i class="fas fa-ruler-combined me-2"></i> ${area.value} sq ft</li>
                                </ul>
                            </div>
                        `;
                    }
                    
                    // Show similar properties if available
                    const similarPropertiesContainer = document.getElementById('similarProperties');
                    const similarPropertiesSection = document.getElementById('similarPropertiesSection');
                    
                    if (similarPropertiesContainer && data.similar_properties && data.similar_properties.length > 0) {
                        similarPropertiesContainer.innerHTML = '';
                        data.similar_properties.forEach(property => {
                            similarPropertiesContainer.innerHTML += `
                                <div class="col-md-4 mb-4">
                                    <div class="card property-card">
                                        <div class="card-img-wrapper">
                                            <img src="${property.image || 'https://via.placeholder.com/300x200'}" class="card-img-top" alt="${property.title}">
                                            <div class="property-tag">${property.property_type}</div>
                                            <div class="property-price">$${property.price}</div>
                                        </div>
                                        <div class="card-body">
                                            <h5 class="card-title">${property.title}</h5>
                                            <div class="property-features">
                                                <span><i class="fas fa-bed"></i> ${property.bedrooms} Beds</span>
                                                <span><i class="fas fa-bath"></i> ${property.bathrooms} Baths</span>
                                                <span><i class="fas fa-ruler-combined"></i> ${property.area} sqft</span>
                                            </div>
                                            <div class="property-location">
                                                <i class="fas fa-map-marker-alt"></i> ${property.location}
                                            </div>
                                            <a href="/properties/${property.id}" class="btn btn-primary mt-3 w-100">View Details</a>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        if (similarPropertiesSection) {
                            similarPropertiesSection.classList.remove('d-none');
                        }
                    } else if (similarPropertiesSection) {
                        similarPropertiesSection.classList.add('d-none');
                    }
                    
                    // Add action buttons
                    const predictionActions = document.getElementById('predictionActions');
                    if (predictionActions) {
                        predictionActions.innerHTML = `
                            <div class="mt-3">
                                <button type="button" class="btn btn-primary" id="savePredictionBtn">Save This Prediction</button>
                                <button type="button" class="btn btn-outline-secondary ms-2" id="newPredictionBtn">New Prediction</button>
                            </div>
                        `;
                        
                        // Add event listeners to the new buttons
                        const savePredictionBtn = document.getElementById('savePredictionBtn');
                        const newPredictionBtn = document.getElementById('newPredictionBtn');
                        
                        if (savePredictionBtn) {
                            savePredictionBtn.addEventListener('click', function() {
                                // Save prediction logic (requires user to be logged in)
                                fetch('/api/save-prediction', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({
                                        location: location.value,
                                        property_type: propertyType.value,
                                        bedrooms: bedrooms.value,
                                        bathrooms: bathrooms.value,
                                        area: area.value,
                                        predicted_rent: data.predicted_rent
                                    })
                                })
                                .then(response => {
                                    if (!response.ok) {
                                        if (response.status === 401) {
                                            throw new Error('Please log in to save predictions');
                                        }
                                        throw new Error('Network response was not ok');
                                    }
                                    return response.json();
                                })
                                .then(saveData => {
                                    showAlert('Prediction saved successfully!', 'success');
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                    showAlert(error.message || 'An error occurred while saving the prediction.', 'danger');
                                });
                            });
                        }
                        
                        if (newPredictionBtn) {
                            newPredictionBtn.addEventListener('click', function() {
                                // Reset the form and result container
                                rentPredictionForm.reset();
                                
                                if (predictionResult) {
                                    predictionResult.classList.add('d-none');
                                }
                                
                                // Reset validation classes
                                const formInputs = rentPredictionForm.querySelectorAll('.form-control');
                                formInputs.forEach(input => {
                                    input.classList.remove('is-valid');
                                    input.classList.remove('is-invalid');
                                });
                                
                                // Scroll back to form
                                rentPredictionForm.scrollIntoView({ behavior: 'smooth' });
                            });
                        }
                    }
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                    
                    // Scroll to results
                    if (predictionResult) {
                        predictionResult.scrollIntoView({ behavior: 'smooth' });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    
                    if (predictionLoading) {
                        predictionLoading.classList.add('d-none');
                    }
                    
                    showAlert('An error occurred while generating the prediction. Please try again.', 'danger');
                    
                    // Reset button
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                });
            } else {
                showAlert('Please fill in all required fields correctly.', 'danger');
            }
        });
    }

    // Utility function to show alerts
    function showAlert(message, type) {
        const alertPlaceholder = document.getElementById('alertPlaceholder');
        if (!alertPlaceholder) return;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        alertPlaceholder.appendChild(wrapper);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const alert = wrapper.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    // Utility function to validate email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    // Initialize Bootstrap tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('active');
            } else {
                backToTopButton.classList.remove('active');
            }
        });

        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Animate elements on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.fade-up').forEach(element => {
        observer.observe(element);
    });

    // Property Favorites
    const favoriteButtons = document.querySelectorAll('.favorite-button');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const propertyId = this.dataset.propertyId;
            const isFavorite = this.classList.contains('active');
            
            fetch(`/api/favorites/${propertyId}`, {
                method: isFavorite ? 'DELETE' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401) {
                        // User not logged in
                        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                        throw new Error('Please login to add favorites');
                    }
                    throw new Error('Request failed');
                }
                return response.json();
            })
            .then(data => {
                if (isFavorite) {
                    this.classList.remove('active');
                    this.querySelector('i').classList.replace('fas', 'far');
                    showAlert('Property removed from favorites', 'info');
                } else {
                    this.classList.add('active');
                    this.querySelector('i').classList.replace('far', 'fas');
                    showAlert('Property added to favorites', 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (error.message !== 'Please login to add favorites') {
                    showAlert('An error occurred. Please try again.', 'danger');
                }
            });
        });
    });

    // Property Image Gallery
    const propertyGallery = document.querySelector('.property-gallery');
    if (propertyGallery) {
        const mainImage = document.querySelector('.property-main-image img');
        const thumbnails = document.querySelectorAll('.property-thumbnail');
        
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                const imgSrc = this.querySelector('img').getAttribute('src');
                mainImage.setAttribute('src', imgSrc);
                thumbnails.forEach(thumb => thumb.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Property Reviews
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;
            const rating = document.querySelector('input[name="rating"]:checked');
            const comment = document.getElementById('reviewComment');

            if (!rating) {
                document.getElementById('ratingError').classList.remove('d-none');
                isValid = false;
            } else {
                document.getElementById('ratingError').classList.add('d-none');
            }

            if (!comment.value.trim()) {
                comment.classList.add('is-invalid');
                isValid = false;
            } else {
                comment.classList.remove('is-invalid');
            }

            if (isValid) {
                const formData = new FormData(reviewForm);
                const propertyId = reviewForm.dataset.propertyId;
                
                fetch(`/api/properties/${propertyId}/reviews`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                            throw new Error('Please login to submit a review');
                        }
                        throw new Error('Failed to submit review');
                    }
                    return response.json();
                })
                .then(data => {
                    showAlert('Your review has been submitted successfully!', 'success');
                    reviewForm.reset();
                    
                    // Add the new review to the list without reloading
                    const reviewsList = document.querySelector('.reviews-list');
                    if (reviewsList) {
                        const newReview = document.createElement('div');
                        newReview.className = 'review-item mb-4 p-4 bg-light rounded';
                        newReview.innerHTML = `
                            <div class="d-flex align-items-center mb-3">
                                <img src="${data.user.avatar || 'https://via.placeholder.com/50'}" class="rounded-circle me-3" width="50" height="50" alt="${data.user.name}">
                                <div>
                                    <h5 class="mb-0">${data.user.name}</h5>
                                    <div class="text-muted small">${new Date(data.created_at).toLocaleDateString()}</div>
                                </div>
                                <div class="ms-auto">
                                    <div class="rating">
                                        ${generateStarRating(data.rating)}
                                    </div>
                                </div>
                            </div>
                            <p>${data.comment}</p>
                        `;
                        reviewsList.prepend(newReview);
                        
                        // Update review count and average
                        const reviewCount = document.getElementById('reviewCount');
                        const reviewAverage = document.getElementById('reviewAverage');
                        if (reviewCount && reviewAverage) {
                            reviewCount.textContent = parseInt(reviewCount.textContent) + 1;
                            reviewAverage.textContent = data.average_rating.toFixed(1);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (error.message !== 'Please login to submit a review') {
                        showAlert('An error occurred while submitting your review. Please try again.', 'danger');
                    }
                });
            } else {
                showAlert('Please provide a rating and comment.', 'danger');
            }
        });
    }

    // Helper function to generate star rating HTML
    function generateStarRating(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                stars += '<i class="fas fa-star text-warning"></i>';
            } else if (i - 0.5 <= rating) {
                stars += '<i class="fas fa-star-half-alt text-warning"></i>';
            } else {
                stars += '<i class="far fa-star text-warning"></i>';
            }
        }
        return stars;
    }

    // Property Booking
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        const checkInDate = document.getElementById('checkInDate');
        const checkOutDate = document.getElementById('checkOutDate');
        const totalPrice = document.getElementById('totalPrice');
        const pricePerNight = parseFloat(bookingForm.dataset.price || 0);
        
        // Calculate total price when dates change
        function calculateTotalPrice() {
            if (checkInDate.value && checkOutDate.value) {
                const startDate = new Date(checkInDate.value);
                const endDate = new Date(checkOutDate.value);
                
                if (endDate > startDate) {
                    const nights = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
                    const total = nights * pricePerNight;
                    totalPrice.textContent = total.toFixed(2);
                    document.getElementById('totalNights').textContent = nights;
                    document.getElementById('bookingSummary').classList.remove('d-none');
                } else {
                    document.getElementById('bookingSummary').classList.add('d-none');
                }
            }
        }
        
        if (checkInDate && checkOutDate) {
            checkInDate.addEventListener('change', calculateTotalPrice);
            checkOutDate.addEventListener('change', calculateTotalPrice);
            
            // Set min date for check-in to today
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            const formattedToday = `${yyyy}-${mm}-${dd}`;
            
            checkInDate.setAttribute('min', formattedToday);
            
            // Update check-out min date when check-in changes
            checkInDate.addEventListener('change', function() {
                checkOutDate.setAttribute('min', this.value);
                if (checkOutDate.value && new Date(checkOutDate.value) <= new Date(this.value)) {
                    checkOutDate.value = '';
                }
            });
        }
        
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;
            
            if (!checkInDate.value) {
                checkInDate.classList.add('is-invalid');
                isValid = false;
            } else {
                checkInDate.classList.remove('is-invalid');
            }
            
            if (!checkOutDate.value) {
                checkOutDate.classList.add('is-invalid');
                isValid = false;
            } else {
                checkOutDate.classList.remove('is-invalid');
            }
            
            if (isValid) {
                const formData = new FormData(bookingForm);
                const propertyId = bookingForm.dataset.propertyId;
                
                fetch(`/api/properties/${propertyId}/book`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                            throw new Error('Please login to book this property');
                        }
                        return response.json().then(data => {
                            throw new Error(data.message || 'Booking failed');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    showAlert('Booking successful! Check your email for confirmation details.', 'success');
                    setTimeout(() => {
                        window.location.href = '/bookings';
                    }, 2000);
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (error.message !== 'Please login to book this property') {
                        showAlert(error.message || 'An error occurred while processing your booking. Please try again.', 'danger');
                    }
                });
            } else {
                showAlert('Please select check-in and check-out dates.', 'danger');
            }
        });
    }
});