
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from database import db
from models import User, Property, Booking, Favorite, Review
from forms import LoginForm, RegistrationForm, PropertyForm, BookingForm, SearchForm, EditProfileForm, ChangePasswordForm, ReviewForm, RequestResetForm, ResetPasswordForm
import folium
from datetime import datetime, timedelta
from sqlalchemy import or_, func
from wtforms import StringField, PasswordField, SelectField, validators
import os
from werkzeug.utils import secure_filename
from flask_dance.contrib.google import make_google_blueprint, google
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from flask_wtf.csrf import CSRFProtect, CSRFError
import functools
from collections import defaultdict
from flask_mail import Mail, Message

# Define constants
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Set maximum file upload size
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH  # 10MB limit

# Configure secure session
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same-site requests
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session expires after 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Handle CSRF errors
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.error(f"CSRF Error: {e}")
    flash('Security token has expired or is invalid. Please try again.', 'danger')
    return redirect(url_for('login'))

# Handle file size limit exceeded errors
@app.errorhandler(413)
def request_entity_too_large(e):
    app.logger.error(f"File too large error: {e}")
    flash('The file you are trying to upload is too large. Maximum size is 10MB.', 'danger')
    return redirect(request.url)

# Initialize Mail
mail = Mail(app)

# Configure secure headers
@app.after_request
def add_security_headers(response):
    # Prevent browsers from detecting the mimetype incorrectly
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Protect against XSS attacks
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Content Security Policy to prevent XSS attacks
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; img-src 'self' data:; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; connect-src 'self'; form-action 'self'; frame-ancestors 'self'; base-uri 'self'"
    # HTTP Strict Transport Security
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    # Strict Transport Security (HSTS)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Feature Policy
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response

# Rate limiting for login attempts
login_attempts = defaultdict(list)

def rate_limit(max_attempts=5, window_seconds=300):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_view(*args, **kwargs):
            # Get client IP
            ip = request.remote_addr
            # Clean up old attempts
            now = datetime.now()
            login_attempts[ip] = [attempt for attempt in login_attempts[ip] 
                                if (now - attempt) < timedelta(seconds=window_seconds)]
            # Check if too many attempts
            if len(login_attempts[ip]) >= max_attempts:
                return render_template('errors/error.html', 
                                      error_code=429, 
                                      error_title='Too Many Attempts',
                                      error_message=f'Too many login attempts. Please try again after {window_seconds//60} minutes.'), 429
            # Add this attempt
            login_attempts[ip].append(now)
            # Call the original view function
            return f(*args, **kwargs)
        return wrapped_view
    return decorator

# Error handlers
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/csrf_error.html'), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/error.html', 
                           error_code=404, 
                           error_title='Page Not Found',
                           error_message='The page you are looking for does not exist.'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/error.html', 
                           error_code=403, 
                           error_title='Forbidden',
                           error_message='You do not have permission to access this resource.'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/error.html', 
                           error_code=500, 
                           error_title='Internal Server Error',
                           error_message='Something went wrong on our end. Please try again later.'), 500

# Create new forms without email validation
class SimpleRegistrationForm(RegistrationForm):
    # Redefine the email field without the email validator
    email = StringField('Email', validators=[validators.DataRequired()])
    name = StringField('Name', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('owner', 'Property Owner')])
    phone = StringField('Phone', validators=[validators.DataRequired()])

class SimpleLoginForm(LoginForm):
    # Redefine the email field without the email validator
    email = StringField('Email', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def initialize_database():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin_user = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
        if not admin_user:
            admin = User(
                name='Admin',
                email=app.config['ADMIN_EMAIL'],
                role='admin',
                phone='0000000000'
            )
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()

# Ensure root URL goes to home page
@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    featured_properties = [
        {
            'id': 1,
            'title': 'Modern Downtown Apartment',
            'city': 'New York',
            'bedrooms': 2,
            'bathrooms': 1,
            'price': 2500,
            'description': 'Beautiful modern apartment in the heart of downtown with great amenities.',
            'image_id': '1560448204-e01f8e658d6a'
        },
        {
            'id': 2,
            'title': 'Cozy Suburban House',
            'city': 'Chicago',
            'bedrooms': 3,
            'bathrooms': 2,
            'price': 1800,
            'description': 'Spacious house with backyard in a quiet suburban neighborhood.',
            'image_id': '1564013799913-e644f80592f9'
        },
        {
            'id': 3,
            'title': 'Luxury Beachfront Condo',
            'city': 'Miami',
            'bedrooms': 2,
            'bathrooms': 2,
            'price': 3500,
            'description': 'Stunning ocean views from this luxury beachfront property.',
            'image_id': '1560520031-3a4e9a93f5a1'
        }
    ]
    return render_template('home.html', featured_properties=featured_properties)

@app.route('/login', methods=['GET', 'POST'])
@rate_limit(max_attempts=5, window_seconds=300)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SimpleLoginForm()  # Use the new login form without email validation
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Reset login attempts on successful login
            if request.remote_addr in login_attempts:
                login_attempts[request.remote_addr] = []
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SimpleRegistrationForm()  # Use the new form without email validation
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)  # Use password hashing
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))  # Redirect to home after logout

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'owner':
        return redirect(url_for('owner_dashboard'))
    else:
        return redirect(url_for('customer_dashboard'))

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    properties = Property.query.all()
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', properties=properties, bookings=bookings, users=users)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('You are not authorized to perform this action', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin_users'))
    
    # Delete user's properties and bookings
    Property.query.filter_by(owner_id=user.id).delete()
    Booking.query.filter_by(customer_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/properties')
@login_required
def admin_properties():
    if current_user.role != 'admin':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    properties = Property.query.all()
    return render_template('admin/properties.html', properties=properties)

@app.route('/admin/property/delete/<int:property_id>', methods=['POST'])
@login_required
def admin_delete_property(property_id):
    if current_user.role != 'admin':
        flash('You are not authorized to perform this action', 'danger')
        return redirect(url_for('dashboard'))
    
    property = Property.query.get_or_404(property_id)
    # Delete associated bookings
    Booking.query.filter_by(property_id=property.id).delete()
    
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully', 'success')
    return redirect(url_for('admin_properties'))

# Owner Dashboard
@app.route('/owner/dashboard')
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('owner/dashboard.html', properties=properties)

# Define allowed file extensions for security
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

# Function to check if file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/owner/add_property', methods=['GET', 'POST'])
@login_required
def add_property():
    if current_user.role != 'owner':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            title=form.title.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            price=form.price.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            owner_id=current_user.id
        )
        db.session.add(property)
        db.session.commit()
        flash('Property added successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    return render_template('owner/add_property.html', form=form)

@app.route('/owner/edit_property/<int:property_id>', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner_id != current_user.id:
        flash('You are not authorized to edit this property', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    form = PropertyForm(obj=property)
    if form.validate_on_submit():
        property.title = form.title.data
        property.description = form.description.data
        property.address = form.address.data
        property.city = form.city.data
        property.price = form.price.data
        property.bedrooms = form.bedrooms.data
        property.bathrooms = form.bathrooms.data
        property.latitude = form.latitude.data
        property.longitude = form.longitude.data
        property.furnishing_status = form.furnishing_status.data
        property.tenant_preferred = form.tenant_preferred.data
        property.area_type = form.area_type.data
        
        # Handle image upload with security validation
        if form.image_file.data:
            try:
                # Validate file type and content
                image_file = form.image_file.data
                if image_file.filename == '':
                    flash('No file selected', 'warning')
                elif not allowed_file(image_file.filename):
                    flash('Invalid file type. Only jpg, jpeg, and png files are allowed', 'danger')
                    return render_template('owner/edit_property.html', form=form, property=property)
                
                # Delete old image if it exists
                if property.image_file and property.image_file != 'default.jpg':
                    old_file_path = os.path.join(app.root_path, 'static/property_pics', property.image_file)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Generate secure filename to prevent path traversal attacks
                filename = secure_filename(image_file.filename)
                
                # Add random string to filename to prevent overwriting
                filename = str(uuid.uuid4().hex) + '_' + filename
                
                # Ensure directory exists
                os.makedirs(os.path.join(app.root_path, 'static/property_pics'), exist_ok=True)
                
                # Save file with size limit (10MB)
                file_path = os.path.join(app.root_path, 'static/property_pics', filename)
                image_file.save(file_path)
                
                # Set the property's image file attribute
                property.image_file = filename
            except Exception as e:
                app.logger.error(f"File upload error: {str(e)}")
                flash('An error occurred while uploading the image', 'danger')
                return render_template('owner/edit_property.html', form=form, property=property)
        
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    
    return render_template('owner/edit_property.html', form=form, property=property)

@app.route('/owner/delete_property/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner_id != current_user.id:
        flash('You are not authorized to delete this property', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    # Delete associated bookings
    Booking.query.filter_by(property_id=property.id).delete()
    
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully', 'success')
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/property/<int:property_id>')
@login_required
def owner_property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner_id != current_user.id:
        flash('You are not authorized to view this property', 'danger')
        return redirect(url_for('owner_dashboard'))
    bookings = Booking.query.filter_by(property_id=property.id).all()
    return render_template('owner/property_detail.html', property=property, bookings=bookings)

@app.route('/owner/booking/<int:booking_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    property = Property.query.get_or_404(booking.property_id)
    
    if property.owner_id != current_user.id:
        flash('You are not authorized to confirm this booking', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    booking.status = 'confirmed'
    db.session.commit()
    flash('Booking confirmed!', 'success')
    return redirect(url_for('owner_property_detail', property_id=property.id))

@app.route('/owner/booking/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    property = Property.query.get_or_404(booking.property_id)
    
    if property.owner_id != current_user.id:
        flash('You are not authorized to reject this booking', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    booking.status = 'rejected'
    db.session.commit()
    flash('Booking rejected', 'info')
    return redirect(url_for('owner_property_detail', property_id=property.id))

# Customer Dashboard
@app.route('/customer/dashboard', methods=['GET', 'POST'])
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    form = SearchForm()
    properties = Property.query
    
    # Apply filters with proper validation
    if form.validate_on_submit():
        try:
            # Location filtering with sanitized input
            if form.location.data:
                # Use parameterized query to prevent SQL injection
                properties = properties.filter(Property.city.ilike(f'%{form.location.data}%'))
            
            # Numeric filters with validation
            if form.min_price.data is not None and form.min_price.data >= 0:
                properties = properties.filter(Property.price >= form.min_price.data)
            if form.max_price.data is not None and form.max_price.data >= 0:
                properties = properties.filter(Property.price <= form.max_price.data)
            if form.bedrooms.data is not None and form.bedrooms.data >= 0:
                properties = properties.filter(Property.bedrooms >= form.bedrooms.data)
            if form.bathrooms.data is not None and form.bathrooms.data >= 0:
                properties = properties.filter(Property.bathrooms >= form.bathrooms.data)
            if form.min_size.data is not None and form.min_size.data >= 0:
                properties = properties.filter(Property.size >= form.min_size.data)
            if form.max_size.data is not None and form.max_size.data >= 0:
                properties = properties.filter(Property.size <= form.max_size.data)
            
            # Select field filters
            if form.furnishing_status.data:
                properties = properties.filter(Property.furnishing_status == form.furnishing_status.data)
            if form.tenant_preferred.data:
                properties = properties.filter(Property.tenant_preferred == form.tenant_preferred.data)
        except Exception as e:
            # Log the error and show a user-friendly message
            app.logger.error(f"Search error: {str(e)}")
            flash('An error occurred while processing your search. Please try again.', 'danger')
    
    properties = properties.all()
    
    # Create map
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Default to India
    for property in properties:
        folium.Marker(
            [property.latitude, property.longitude],
            popup=f'<b>{property.title}</b><br>${property.price}/month<br><a href="{url_for("customer_property_detail", property_id=property.id)}">View</a>',
            tooltip=property.title
        ).add_to(m)
    
    map_html = m._repr_html_()
    
    return render_template('customer/dashboard.html', form=form, properties=properties, map_html=map_html)

@app.route('/customer/property/<int:property_id>', methods=['GET', 'POST'])
@login_required
def customer_property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    form = BookingForm()
    if form.validate_on_submit():
        # Check for date conflicts
        overlapping_booking = Booking.query.filter(
            Booking.property_id == property.id,
            or_(
                (Booking.start_date <= form.start_date.data) & (Booking.end_date >= form.start_date.data),
                (Booking.start_date <= form.end_date.data) & (Booking.end_date >= form.end_date.data),
                (Booking.start_date >= form.start_date.data) & (Booking.end_date <= form.end_date.data)
            )
        ).first()

        if overlapping_booking:
            flash('This property is already booked for the selected dates', 'danger')
        else:
            booking = Booking(
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                property_id=property.id,
                customer_id=current_user.id,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking request sent! The owner will confirm soon.', 'success')
            return redirect(url_for('customer_bookings'))
    return render_template('customer/property_detail.html', property=property, form=form)

@app.route('/customer/bookings')
@login_required
def customer_bookings():
    if current_user.role != 'customer':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    bookings = Booking.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer/bookings.html', bookings=bookings)

@app.route('/customer/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        flash('You are not authorized to cancel this booking', 'danger')
        return redirect(url_for('customer_bookings'))
    
    if booking.status == 'confirmed':
        flash('This booking is already confirmed and cannot be canceled', 'warning')
    else:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking canceled successfully', 'success')
    
    return redirect(url_for('customer_bookings'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.dob = form.dob.data
        current_user.verified = form.verified.data

        # Handle profile picture upload
        if form.profile_pic.data:
            pic_file = form.profile_pic.data
            filename = secure_filename(pic_file.filename)
            pic_path = os.path.join('static/profile_pics', filename)
            pic_file.save(pic_path)
            current_user.profile_pic = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('customer/profile.html', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('auth/change_password.html', title='Change Password', form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''
To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)

# Replace with your Google OAuth credentials
google_bp = make_google_blueprint(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()
    email = user_info["email"]
    name = user_info.get("name", email.split("@")[0])
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, role="customer", verified=True)
        # Generate a random secure password for OAuth users
        import secrets
        random_password = secrets.token_urlsafe(16)
        user.set_password(random_password)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash("Logged in with Google!", "success")
    return redirect(url_for("dashboard"))

# Load dataset and train model (do this once at startup)
import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

# Fix the dataset path to use the correct location
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'House_Rent_Dataset.csv')

try:
    # Load the dataset
    df = pd.read_csv(DATASET_PATH, engine='python', on_bad_lines='skip')
    
    # Select features for the model
    numeric_features = ['Size', 'BHK', 'Bathroom']
    categorical_features = ['City', 'Furnishing Status', 'Tenant Preferred', 'Area Type']
    
    # Handle missing values
    df = df.dropna(subset=numeric_features + categorical_features)
    
    # Prepare features and target
    X = df[numeric_features + categorical_features]
    y = df['Rent']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create preprocessing for numeric and categorical features
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Create model pipelines
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42))
    ])
    
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])
    
    # Train the models
    xgb_pipeline.fit(X_train, y_train)
    rf_pipeline.fit(X_train, y_train)
    lr_pipeline.fit(X_train, y_train)
    
    # Evaluate models
    models = {
        'XGBoost': xgb_pipeline,
        'Random Forest': rf_pipeline,
        'Linear Regression': lr_pipeline
    }
    
    best_model = None
    best_score = float('-inf')
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(f'{name} - MSE: {mse:.2f}, R2: {r2:.2f}')
        
        if r2 > best_score:
            best_score = r2
            best_model = model
    
    # Use the best model for predictions
    model = best_model
    print(f'Using best model with R2 score: {best_score:.2f}')
    
    # Save feature names for prediction
    model_features = numeric_features + categorical_features
    
except Exception as e:
    print(f"Error loading dataset or training model: {e}")
    # Fallback to simple model if there's an error
    model = LinearRegression()
    df = pd.DataFrame({'Size': [1000, 1500], 'BHK': [2, 3], 'Bathroom': [2, 3], 'Rent': [15000, 25000]})
    model.fit(df[['Size', 'BHK', 'Bathroom']], df['Rent'])
    model_features = ['Size', 'BHK', 'Bathroom']

@app.route('/predict_rent', methods=['GET', 'POST'])
@login_required
def predict_rent():
    predicted_rent = None
    matching_properties = []
    prediction_accuracy = None
    model_name = None
    error_message = None
    
    # Get cities, furnishing status, tenant preferences, and area types for the form
    try:
        cities = sorted(list(set(df['City'].dropna().unique())))
        furnishing_statuses = sorted(list(set(df['Furnishing Status'].dropna().unique())))
        tenant_preferences = sorted(list(set(df['Tenant Preferred'].dropna().unique())))
        area_types = sorted(list(set(df['Area Type'].dropna().unique())))
    except Exception as e:
        app.logger.error(f"Error loading form data: {str(e)}")
        flash('An error occurred while loading the form. Please try again later.', 'danger')
        cities = []
        furnishing_statuses = []
        tenant_preferences = []
        area_types = []
    
    # Create form with dynamic choices
    form = PredictRentForm()
    form.city.choices = [('Any', 'Any')] + [(city, city) for city in cities]
    form.furnishing_status.choices = [('Any', 'Any')] + [(status, status) for status in furnishing_statuses]
    form.tenant_preferred.choices = [('Any', 'Any')] + [(pref, pref) for pref in tenant_preferences]
    form.area_type.choices = [('Any', 'Any')] + [(type_, type_) for type_ in area_types]
    
    if form.validate_on_submit():
        try:
            # Get input features from form with validation
            try:
                size = float(form.size.data)
                if size <= 0 or size > 10000:  # Reasonable size limits
                    flash('Size must be between 0 and 10,000 square feet', 'danger')
                    return render_template('predict_rent.html', form=form)
                
                bedroom = int(form.bedroom.data)
                if bedroom < 0 or bedroom > 20:  # Reasonable bedroom limits
                    flash('Number of bedrooms must be between 0 and 20', 'danger')
                    return render_template('predict_rent.html', form=form)
                
                bathroom = int(form.bathroom.data)
                if bathroom < 0 or bathroom > 20:  # Reasonable bathroom limits
                    flash('Number of bathrooms must be between 0 and 20', 'danger')
                    return render_template('predict_rent.html', form=form)
            except (ValueError, TypeError):
                flash('Please enter valid numeric values for size, bedrooms, and bathrooms', 'danger')
                return render_template('predict_rent.html', form=form)
            
            # Get additional features from form with validation
            city = form.city.data
            furnishing_status = form.furnishing_status.data
            tenant_preferred = form.tenant_preferred.data
            area_type = form.area_type.data
            
            # Validate dropdown selections
            if city != 'Any' and city not in [choice[0] for choice in form.city.choices]:
                flash('Invalid city selection', 'danger')
                return render_template('predict_rent.html', form=form)
                
            if furnishing_status != 'Any' and furnishing_status not in [choice[0] for choice in form.furnishing_status.choices]:
                flash('Invalid furnishing status selection', 'danger')
                return render_template('predict_rent.html', form=form)
                
            if tenant_preferred != 'Any' and tenant_preferred not in [choice[0] for choice in form.tenant_preferred.choices]:
                flash('Invalid tenant preference selection', 'danger')
                return render_template('predict_rent.html', form=form)
                
            if area_type != 'Any' and area_type not in [choice[0] for choice in form.area_type.choices]:
                flash('Invalid area type selection', 'danger')
                return render_template('predict_rent.html', form=form)
            
            # Prepare input features based on available model features
            if 'City' in model_features and 'Furnishing Status' in model_features and 'Tenant Preferred' in model_features and 'Area Type' in model_features:
                # Full featured model
                input_data = pd.DataFrame({
                    'Size': [size],
                    'BHK': [bedroom],
                    'Bathroom': [bathroom],
                    'City': [city],
                    'Furnishing Status': [furnishing_status],
                    'Tenant Preferred': [tenant_preferred],
                    'Area Type': [area_type]
                })
            else:
                # Fallback to basic model
                input_data = pd.DataFrame({
                    'Size': [size],
                    'BHK': [bedroom],
                    'Bathroom': [bathroom]
                })
            
            # Make prediction with error handling
            try:
                predicted_rent = model.predict(input_data)[0]
                # Validate prediction result
                if not isinstance(predicted_rent, (int, float)) or predicted_rent < 0:
                    raise ValueError("Invalid prediction result")
            except Exception as e:
                app.logger.error(f"Prediction error: {str(e)}")
                flash('An error occurred during prediction. Please try again with different values.', 'danger')
                return render_template('predict_rent.html', form=form, predicted_rent=None)
            
            # Get model type for display
            if hasattr(model, 'named_steps'):
                regressor = model.named_steps['regressor']
                if isinstance(regressor, XGBRegressor):
                    model_name = 'XGBoost'
                    prediction_accuracy = 'High'
                elif isinstance(regressor, RandomForestRegressor):
                    model_name = 'Random Forest'
                    prediction_accuracy = 'Medium-High'
                else:
                    model_name = 'Linear Regression'
                    prediction_accuracy = 'Medium'
            else:
                model_name = 'Linear Regression'
                prediction_accuracy = 'Basic'
            
            # Find properties in the predicted price range (+/- 10%)
            try:
                min_price = predicted_rent * 0.9
                max_price = predicted_rent * 1.1
                
                # Validate price range
                if min_price < 0 or max_price < 0 or min_price > max_price:
                    raise ValueError("Invalid price range calculated")
                
                # Build query with additional filters if provided - using parameterized queries
                query = Property.query.filter(
                    Property.price >= min_price,
                    Property.price <= max_price,
                    Property.available == True
                )
                
                # Add additional filters if values were provided - using parameterized queries
                if bedroom > 0:
                    query = query.filter(Property.bedrooms == bedroom)
                if bathroom > 0:
                    query = query.filter(Property.bathrooms == bathroom)
                if city and city != 'Any' and hasattr(Property, 'city'):
                    query = query.filter(Property.city == city)
                if furnishing_status and furnishing_status != 'Any' and hasattr(Property, 'furnishing_status'):
                    query = query.filter(Property.furnishing_status == furnishing_status)
                
                # Limit results for performance
                matching_properties = query.limit(50).all()
            except Exception as e:
                app.logger.error(f"Property search error: {str(e)}")
                flash('An error occurred while searching for matching properties.', 'warning')
                matching_properties = []
            
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'danger')
            print(f'Prediction error: {str(e)}')
    
    return render_template('predict_rent.html', 
                           predicted_rent=predicted_rent, 
                           properties=matching_properties,
                           cities=cities,
                           furnishing_statuses=furnishing_statuses,
                           tenant_preferences=tenant_preferences,
                           area_types=area_types,
                           model_name=model_name,
                           prediction_accuracy=prediction_accuracy)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    review_form = ReviewForm()
    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    
    # Check if user has favorited this property
    is_favorited = False
    if current_user.is_authenticated:
        favorite = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()
        is_favorited = favorite is not None
    
    return render_template('property_detail.html', property=property, review_form=review_form, 
                           reviews=reviews, is_favorited=is_favorited)

@app.route('/property/<int:property_id>/review', methods=['POST'])
@login_required
def add_review(property_id):
    property = Property.query.get_or_404(property_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Check if user already reviewed this property
        existing_review = Review.query.filter_by(user_id=current_user.id, property_id=property_id).first()
        
        if existing_review:
            flash('You have already reviewed this property. You can edit your review instead.', 'warning')
        else:
            review = Review(
                content=form.content.data,
                rating=form.rating.data,
                user_id=current_user.id,
                property_id=property_id
            )
            db.session.add(review)
            db.session.commit()
            flash('Your review has been added!', 'success')
    
    return redirect(url_for('property_detail', property_id=property_id))

@app.route('/property/<int:property_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Check if already favorited
    favorite = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    
    if favorite:
        # Remove from favorites
        db.session.delete(favorite)
        db.session.commit()
        flash('Property removed from favorites!', 'success')
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, property_id=property_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Property added to favorites!', 'success')
    
    return redirect(url_for('property_detail', property_id=property_id))

@app.route('/customer/favorites')
@login_required
def customer_favorites():
    if current_user.role != 'customer':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('customer/favorites.html', favorites=favorites)

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)