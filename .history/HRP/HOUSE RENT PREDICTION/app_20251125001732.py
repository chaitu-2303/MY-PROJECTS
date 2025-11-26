from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, send_from_directory
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from database import db
from models import User, Property, Booking, Favorite, Review
from forms import (
    LoginForm, RegistrationForm, PropertyForm, BookingForm, SearchForm,
    EditProfileForm, ChangePasswordForm, ReviewForm,
    RequestResetForm, ResetPasswordForm, PredictRentForm
)
import folium
from datetime import datetime, timedelta
from sqlalchemy import or_, func
from wtforms import StringField, PasswordField, SelectField, validators
import os
import uuid
from werkzeug.utils import secure_filename
from flask_dance.contrib.google import make_google_blueprint, google
import pandas as pd
from flask_wtf.csrf import CSRFProtect, CSRFError
import functools
from collections import defaultdict
from flask_mail import Mail, Message
import joblib  # NEW: for loading pre-trained ML model

# =========================================================
# Flask app setup
# =========================================================

MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

app = Flask(
    __name__,
    template_folder='Frontend',         # Set Frontend folder as template directory
    static_folder='Frontend/assets',    # Set Frontend/assets as static files directory
    static_url_path='/assets'           # Set static URL path to match references in templates
)
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session expires after 7 days

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Mail
mail = Mail(app)

# Rate limiting for login attempts
login_attempts = defaultdict(list)

# =========================================================
# ML MODEL: load pre-trained model (.pkl) and small dataset
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pre-trained model path (created by train_model.py)
MODEL_PATH = os.path.join(BASE_DIR, "house_rent_model.pkl")

# Small dataset used only for UI / matching (NOT for training here)
UI_DATASET_PATH = os.path.join(BASE_DIR, "House_Rent_Dataset.csv")

model = None
df = pd.DataFrame()

try:
    # Load pre-trained pipeline (with preprocessing + model)
    model = joblib.load(MODEL_PATH)
    app.logger.info(f"✅ Loaded ML model from: {MODEL_PATH}")
except Exception as e:
    app.logger.error(f"❌ Could not load ML model from {MODEL_PATH}: {e}")
    model = None

try:
    # Load smaller dataset for featured listings / matching properties
    df = pd.read_csv(UI_DATASET_PATH, engine='python', on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    if 'Rent' in df.columns:
        # Ensure Rent is numeric
        df['Rent'] = df['Rent'].astype(str).str.replace(',', '').astype(float)
    app.logger.info(f"✅ Loaded UI dataset from: {UI_DATASET_PATH} with shape {df.shape}")
except Exception as e:
    app.logger.error(f"❌ Could not load UI dataset from {UI_DATASET_PATH}: {e}")
    df = pd.DataFrame()

# =========================================================
# Error & security handlers
# =========================================================

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.error(f"CSRF Error: {e}")
    flash('Security token has expired or is invalid. Please try again.', 'danger')
    return redirect(url_for('login'))

@app.errorhandler(413)
def request_entity_too_large(e):
    app.logger.error(f"File too large error: {e}")
    flash('The file you are trying to upload is too large. Maximum size is 10MB.', 'danger')
    return redirect(request.url)

# Configure secure headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://unpkg.com; "
        "img-src 'self' data:; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "connect-src 'self' localhost:* 127.0.0.1:*; "
        "form-action 'self'; "
        "frame-ancestors 'self'; "
        "base-uri 'self'"
    )
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response

# Handle Vite client requests to prevent 404 errors
@app.route('/@vite/client', methods=['GET'])
def handle_vite_client():
    return Response('', mimetype='application/javascript')

# =========================================================
# Rate limiting decorator
# =========================================================

def rate_limit(max_attempts=10, window_seconds=600):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_view(*args, **kwargs):
            ip = request.remote_addr
            now = datetime.now()
            login_attempts[ip] = [
                attempt for attempt in login_attempts[ip]
                if (now - attempt) < timedelta(seconds=window_seconds)
            ]
            if len(login_attempts[ip]) >= max_attempts:
                return render_template(
                    'errors/error.html',
                    error_code=429,
                    error_title='Too Many Attempts',
                    error_message=f'Too many login attempts. Please try again after {window_seconds//60} minutes.'
                ), 429
            login_attempts[ip].append(now)
            return f(*args, **kwargs)
        return wrapped_view
    return decorator

# =========================================================
# Frontend routes (dataset integration)
# =========================================================

@app.route('/landing')
def landing():
    """
    Public landing page using the small dataset for featured properties.
    (Not the root path to avoid conflict with auth redirect.)
    """
    if df.empty:
        featured_properties = []
    else:
        featured_properties = df.sample(min(6, len(df))).to_dict('records')
    return render_template('index.html', featured_properties=featured_properties)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/sign-up')
def signup():
    return render_template('sign-up.html')

@app.route('/listing')
def listing():
    """
    Property listing page using the small dataset, with random images.
    """
    import random
    if df.empty:
        properties = []
    else:
        properties = df.to_dict('records')

    image_dir = os.path.join(BASE_DIR, 'Frontend', 'assets', 'img', 'property')
    image_files = [
        f for f in os.listdir(image_dir)
        if os.path.isfile(os.path.join(image_dir, f))
    ]

    for prop in properties:
        if image_files:
            prop['image_url'] = url_for('serve_assets', filename=f'img/property/{random.choice(image_files)}')
        else:
            prop['image_url'] = url_for('serve_assets', filename='img/property/default.jpg')

    return render_template('listing.html', properties=properties)

# =========================================================
# Rent prediction (HTML page)
# =========================================================

@app.route('/rent_prediction', methods=['GET', 'POST'])
def rent_prediction():
    form = PredictRentForm()
    prediction_result = None

    if form.validate_on_submit():
        if model is None:
            flash('Prediction model is not available. Please contact admin.', 'danger')
        else:
            try:
                data = {
                    'Size': [form.size.data],
                    'BHK': [form.bhk.data],
                    'Bathroom': [form.bathroom.data],
                    'City': [form.city.data],
                    'Furnishing Status': [form.furnishing_status.data],
                    'Tenant Preferred': [form.tenant_preferred.data],
                    'Area Type': [form.area_type.data]
                }
                input_df = pd.DataFrame(data)

                # Pre-trained pipeline handles preprocessing internally
                prediction = model.predict(input_df)[0]
                prediction_result = f'₹{prediction:,.2f}'

            except Exception as e:
                app.logger.error(f"Prediction error (rent_prediction): {e}")
                flash('An error occurred during prediction. Please check your inputs.', 'danger')

    return render_template('rent-prediction.html', form=form, prediction_result=prediction_result)

@app.route('/rent-prediction.html')
def rent_prediction_page():
    form = PredictRentForm()
    return render_template('rent-prediction.html', form=form, prediction_result=None)

# =========================================================
# Auth & user management
# =========================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class SimpleRegistrationForm(RegistrationForm):
    email = StringField('Email', validators=[validators.DataRequired()])
    name = StringField('Name', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('owner', 'Property Owner')])
    phone = StringField('Phone', validators=[validators.DataRequired()])

class SimpleLoginForm(LoginForm):
    email = StringField('Email', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

def initialize_database():
    with app.app_context():
        db.create_all()
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

# Root route -> go to login
@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
@rate_limit(max_attempts=5, window_seconds=300)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SimpleLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if request.remote_addr in login_attempts:
                login_attempts[request.remote_addr] = []
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SimpleRegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'owner':
        return redirect(url_for('owner_dashboard'))
    else:
        return redirect(url_for('customer_dashboard'))

# =========================================================
# Admin / Owner / Customer routes (unchanged logic)
# =========================================================

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
    Booking.query.filter_by(property_id=property.id).delete()
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully', 'success')
    return redirect(url_for('admin_properties'))

@app.route('/owner/dashboard')
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('owner/dashboard.html', properties=properties)

# File upload security
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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
        
        if form.image_file.data:
            try:
                image_file = form.image_file.data
                if image_file.filename == '':
                    flash('No file selected', 'warning')
                elif not allowed_file(image_file.filename):
                    flash('Invalid file type. Only jpg, jpeg, and png files are allowed', 'danger')
                    return render_template('owner/edit_property.html', form=form, property=property)
                
                if property.image_file and property.image_file != 'default.jpg':
                    old_file_path = os.path.join(app.root_path, 'static/property_pics', property.image_file)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(image_file.filename)
                filename = str(uuid.uuid4().hex) + '_' + filename
                os.makedirs(os.path.join(app.root_path, 'static/property_pics'), exist_ok=True)
                file_path = os.path.join(app.root_path, 'static/property_pics', filename)
                image_file.save(file_path)
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

@app.route('/customer/dashboard', methods=['GET', 'POST'])
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('dashboard'))
    form = SearchForm()
    properties = Property.query
    
    if form.validate_on_submit():
        try:
            if form.location.data:
                properties = properties.filter(Property.city.ilike(f'%{form.location.data}%'))
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
            if form.furnishing_status.data:
                properties = properties.filter(Property.furnishing_status == form.furnishing_status.data)
            if form.tenant_preferred.data:
                properties = properties.filter(Property.tenant_preferred == form.tenant_preferred.data)
        except Exception as e:
            app.logger.error(f"Search error: {str(e)}")
            flash('An error occurred while processing your search. Please try again.', 'danger')
    
    properties = properties.all()
    
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    for property in properties:
        if property.latitude and property.longitude:
            folium.Marker(
                [property.latitude, property.longitude],
                popup=f'<b>{property.title}</b><br>₹{property.price}/month<br><a href="{url_for("customer_property_detail", property_id=property.id)}">View</a>',
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
        overlapping_booking = Booking.query.filter(
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
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.dob = form.dob.data
        current_user.location = form.location.data
        current_user.timezone = form.timezone.data
        current_user.verified = form.verified.data

        pic_file = form.profile_pic.data
        if hasattr(pic_file, 'filename') and pic_file.filename:
            filename = secure_filename(pic_file.filename)
            filename = str(uuid.uuid4().hex) + '_' + filename
            pic_dir = os.path.join(app.root_path, 'static/profile_pics')
            os.makedirs(p

::contentReference[oaicite:0]{index=0}
