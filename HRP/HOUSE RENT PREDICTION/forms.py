from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField, FloatField, DateField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed
from models import User, Property

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('owner', 'Owner')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms', validators=[NumberRange(min=0)])
    bathrooms = IntegerField('Bathrooms', validators=[NumberRange(min=0)])
    size = FloatField('Size (sq ft)', validators=[NumberRange(min=0)])
    furnishing_status = SelectField('Furnishing Status', choices=[
        ('', 'Select Furnishing Status'),
        ('Furnished', 'Furnished'),
        ('Semi-Furnished', 'Semi-Furnished'),
        ('Unfurnished', 'Unfurnished')
    ])
    tenant_preferred = SelectField('Tenant Preferred', choices=[
        ('', 'Select Tenant Preference'),
        ('Bachelors', 'Bachelors'),
        ('Family', 'Family'),
        ('Bachelors/Family', 'Bachelors/Family')
    ])
    area_type = SelectField('Area Type', choices=[
        ('', 'Select Area Type'),
        ('Super Area', 'Super Area'),
        ('Carpet Area', 'Carpet Area'),
        ('Build Area', 'Build Area')
    ])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    image_file = FileField('Property Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only! (jpg, png, jpeg)')])
    available = BooleanField('Available for Rent', default=True)
    submit = SubmitField('Add Property')
    
    def validate_image_file(self, image_file):
        if image_file.data:
            # Check file size (max 5MB)
            if len(image_file.data.read()) > 5 * 1024 * 1024:
                image_file.data.seek(0)  # Reset file pointer
                raise ValidationError('File size exceeds 5MB limit')
            image_file.data.seek(0)  # Reset file pointer
            
            # Check file extension
            if not image_file.data.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Invalid file extension. Only jpg, jpeg, and png files are allowed')
            
            # Check filename for security
            if any(char in image_file.data.filename for char in '\/":*?<>|'):
                raise ValidationError('Filename contains invalid characters')
            
            # Check filename length
            if len(image_file.data.filename) > 100:
                raise ValidationError('Filename is too long (max 100 characters)')

class BookingForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Book Now')

class SearchForm(FlaskForm):
    location = StringField('Location', validators=[Length(max=100)])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0, message="Price must be positive")])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0, message="Price must be positive")])
    bedrooms = IntegerField('Bedrooms', validators=[Optional(), NumberRange(min=0, max=20, message="Number of bedrooms must be between 0 and 20")])
    bathrooms = IntegerField('Bathrooms', validators=[Optional(), NumberRange(min=0, max=20, message="Number of bathrooms must be between 0 and 20")])
    furnishing_status = SelectField('Furnishing Status', choices=[
        ('', 'Any'),
        ('Furnished', 'Furnished'),
        ('Semi-Furnished', 'Semi-Furnished'),
        ('Unfurnished', 'Unfurnished')
    ], default='')
    tenant_preferred = SelectField('Tenant Preferred', choices=[
        ('', 'Any'),
        ('Bachelors', 'Bachelors'),
        ('Family', 'Family'),
        ('Bachelors/Family', 'Bachelors/Family')
    ], default='')
    min_size = FloatField('Min Size (sq ft)', validators=[Optional(), NumberRange(min=0, message="Size must be positive")])
    max_size = FloatField('Max Size (sq ft)', validators=[Optional(), NumberRange(min=0, message="Size must be positive")])
    submit = SubmitField('Search')
    
    def validate_location(self, location):
        # Prevent SQL injection by checking for suspicious patterns
        if location.data and any(char in location.data for char in "'\"\\;%_"):
            raise ValidationError('Invalid characters in location field')
            
    def validate_max_price(self, max_price):
        if self.min_price.data and max_price.data and self.min_price.data > max_price.data:
            raise ValidationError('Maximum price must be greater than minimum price')
    
    def validate_max_size(self, max_size):
        if self.min_size.data and max_size.data and self.min_size.data > max_size.data:
            raise ValidationError('Maximum size must be greater than minimum size')

class ReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=500)])
    rating = RadioField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], validators=[DataRequired()], coerce=int)
    submit = SubmitField('Submit Review')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[])
    bio = StringField('Bio', validators=[])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    location = StringField('Location', validators=[])
    timezone = StringField('Time Zone', validators=[])
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    verified = BooleanField('Verified')
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')
    
    def validate_confirm_password(self, confirm_password):
        if self.new_password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')
    
    def validate_confirm_password(self, confirm_password):
        if self.password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')

class PredictRentForm(FlaskForm):
    size = FloatField('Size (sqft)', validators=[DataRequired(), NumberRange(min=100, max=10000, message="Size must be between 100 and 10000 sqft")])
    bedroom = IntegerField('Bedrooms (BHK)', validators=[DataRequired(), NumberRange(min=1, max=10, message="Number of bedrooms must be between 1 and 10")])
    bathroom = IntegerField('Bathrooms', validators=[DataRequired(), NumberRange(min=1, max=10, message="Number of bathrooms must be between 1 and 10")])
    city = SelectField('City', validators=[Optional()])
    furnishing_status = SelectField('Furnishing Status', validators=[Optional()])
    tenant_preferred = SelectField('Tenant Preferred', validators=[Optional()])
    area_type = SelectField('Area Type', validators=[Optional()])
    submit = SubmitField('Predict Rent')
    
    def validate_size(self, size):
        # Additional validation to prevent unrealistic values
        if size.data and (size.data < 100 or size.data > 10000):
            raise ValidationError('Property size must be between 100 and 10000 square feet')
        # Sanitize input to prevent potential injection
        if isinstance(size.data, str) and not size.data.isdigit():
            raise ValidationError('Size must be a positive number')