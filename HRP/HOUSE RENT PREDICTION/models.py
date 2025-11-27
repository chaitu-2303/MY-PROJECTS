from database import db
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import secrets
import jwt
from flask import current_app

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)  # Unique handle
    bio = db.Column(db.String(250), nullable=True)  # Short description
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, owner, customer
    phone = db.Column(db.String(20))
    dob = db.Column(db.Date)  # New field
    location = db.Column(db.String(100), nullable=True)
    timezone = db.Column(db.String(50), nullable=True)
    member_since = db.Column(db.DateTime, default=db.func.current_timestamp())
    profile_pic = db.Column(db.String(120), default='default.jpg')  # New field
    verified = db.Column(db.Boolean, default=False)  # New field
    two_factor_enabled = db.Column(db.Boolean, default=False)
    properties = db.relationship('Property', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def get_reset_token(self, expires_sec=1800):
        # Create a JWT token with user ID and expiration time
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_sec)
        }
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    
    @staticmethod
    def verify_reset_token(token):
        try:
            # Decode the token and extract user ID
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = payload['user_id']
        except:
            return None
        return User.query.get(user_id)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    size = db.Column(db.Float)  # Size in square feet
    furnishing_status = db.Column(db.String(50))  # Furnished, Semi-Furnished, Unfurnished
    tenant_preferred = db.Column(db.String(50))  # Bachelors, Family, Bachelors/Family
    area_type = db.Column(db.String(50))  # Super Area, Carpet Area, Build Area
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_file = db.Column(db.String(120), default='default_property.jpg')
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bookings = db.relationship('Booking', backref='property', lazy=True)
    
    @property
    def average_rating(self):
        reviews = Review.query.filter_by(property_id=self.id).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    property = db.relationship('Property', backref='favorited_by', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    property = db.relationship('Property', backref='reviews', lazy=True)

class PredictionResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    predicted_rent = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(100))
    area_locality = db.Column(db.String(150))
    bhk = db.Column(db.Integer)
    bathroom = db.Column(db.Integer)
    size = db.Column(db.Float)
    furnishing_status = db.Column(db.String(50))
    tenant_preferred = db.Column(db.String(50))
    area_type = db.Column(db.String(50))
    point_of_contact = db.Column(db.String(50))
    notes = db.Column(db.Text)
    user = db.relationship('User', backref='predictions', lazy=True)
