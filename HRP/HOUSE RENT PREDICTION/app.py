from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from database import db
from models import User, Property, Booking
from forms import LoginForm, RegistrationForm, PropertyForm, BookingForm, SearchForm
import folium
from datetime import datetime
from sqlalchemy import or_
from wtforms import StringField, PasswordField, SelectField, validators  # Add this import

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
                password=app.config['ADMIN_PASSWORD'],
                role='admin',
                phone='0000000000'
            )
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
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SimpleLoginForm()  # Use the new login form without email validation
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
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
            password=form.password.data,
            role=form.role.data,
            phone=form.phone.data
        )
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
    
    # Apply filters
    if form.validate_on_submit():
        if form.location.data:
            properties = properties.filter(Property.city.ilike(f'%{form.location.data}%'))
        if form.min_price.data:
            properties = properties.filter(Property.price >= form.min_price.data)
        if form.max_price.data:
            properties = properties.filter(Property.price <= form.max_price.data)
        if form.bedrooms.data:
            properties = properties.filter(Property.bedrooms >= form.bedrooms.data)
    
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

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)