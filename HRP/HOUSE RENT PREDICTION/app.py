import os
import uuid
import functools
from datetime import datetime, timedelta
from collections import defaultdict

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, Response, send_from_directory
)
from flask_login import (
    LoginManager, login_user, current_user,
    logout_user, login_required
)
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from config import Config
from database import db
from models import User, Property, Booking, Favorite, Review
from forms import (
    LoginForm, RegistrationForm, PropertyForm, BookingForm, SearchForm,
    EditProfileForm, ChangePasswordForm, ReviewForm,
    RequestResetForm, ResetPasswordForm, PredictRentForm
)

import pandas as pd
import joblib
import folium

from flask_mail import Mail, Message

# Optional: Google OAuth (only if configured)
try:
    from flask_dance.contrib.google import make_google_blueprint, google
    GOOGLE_OAUTH_AVAILABLE = True
except Exception:
    GOOGLE_OAUTH_AVAILABLE = False


# ======================================================
# APP SETUP
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder="Frontend",
    static_folder="Frontend/assets",
    static_url_path="/assets",
)
app.config.from_object(Config)

# DB & Login
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# CSRF & Mail
csrf = CSRFProtect(app)
mail = Mail(app)

# File upload config
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


# ======================================================
# SECURITY HEADERS & ERROR HANDLERS
# ======================================================

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers[
        "Content-Security-Policy"
    ] = (
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
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.error(f"CSRF Error: {e}")
    flash("Security token has expired or is invalid. Please try again.", "danger")
    return redirect(url_for("login"))


@app.errorhandler(413)
def request_entity_too_large(e):
    flash("The file you are trying to upload is too large. Maximum size is 10MB.", "danger")
    return redirect(request.url)


@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "error.html",
        error_code=404,
        error_title="Page Not Found",
        error_message="The page you are looking for does not exist.",
    ), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "error.html",
        error_code=403,
        error_title="Forbidden",
        error_message="You do not have permission to access this resource.",
    ), 403


@app.errorhandler(500)
def internal_server_error(e):
    return render_template(
        "error.html",
        error_code=500,
        error_title="Internal Server Error",
        error_message="Something went wrong on our end. Please try again later.",
    ), 500


# ======================================================
# RATE LIMITING (LOGIN)
# ======================================================

login_attempts = defaultdict(list)

def rate_limit(max_attempts=10, window_seconds=600):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_view(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            now = datetime.now()
            login_attempts[ip] = [
                t for t in login_attempts[ip]
                if (now - t) < timedelta(seconds=window_seconds)
            ]
            if len(login_attempts[ip]) >= max_attempts:
                return render_template(
                    "errors/error.html",
                    error_code=429,
                    error_title="Too Many Attempts",
                    error_message=f"Too many login attempts. Please try again after {window_seconds // 60} minutes.",
                ), 429
            login_attempts[ip].append(now)
            return f(*args, **kwargs)
        return wrapped_view
    return decorator


# ======================================================
# MODEL & DATASET LOADING
# ======================================================

# These files live in the same folder as app.py
MODEL_PATH = os.path.join(BASE_DIR, "house_rent_model.pkl")
UI_DATASET_PATH = os.path.join(BASE_DIR, "House_Rent_10k_major_cities.csv")

model = None
ui_df = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        app.logger.info("ML model loaded successfully.")
    else:
        app.logger.warning(f"Model file not found at {MODEL_PATH}")

    if os.path.exists(UI_DATASET_PATH):
        ui_df = pd.read_csv(UI_DATASET_PATH)
        ui_df.columns = ui_df.columns.str.strip()
        app.logger.info("UI dataset loaded successfully.")
    else:
        app.logger.warning(f"UI dataset not found at {UI_DATASET_PATH}")
except Exception as e:
    app.logger.error(f"Error loading model or dataset: {e}")
    model = None
    ui_df = None


# ======================================================
# LOGIN MANAGER
# ======================================================

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


# ======================================================
# GOOGLE OAUTH (OPTIONAL)
# ======================================================

if GOOGLE_OAUTH_AVAILABLE:
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET"),
        redirect_to="google_login",
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
            from secrets import token_urlsafe
            user = User(name=name, email=email, role="customer", verified=True)
            user.set_password(token_urlsafe(16))
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Logged in with Google!", "success")
        return redirect(url_for("dashboard"))


# ======================================================
# HELPERS
# ======================================================

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", recipients=[user.email])
    msg.body = f"""
To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


def format_inr(value):
    """Formats a number in Indian currency format (e.g., 1,00,000)."""
    if not isinstance(value, (int, float)):
        return value
    s = str(int(value))[::-1]
    groups = []
    i = 0
    while i < len(s):
        if i == 0:
            groups.append(s[i:i+3])
            i += 3
        else:
            groups.append(s[i:i+2])
            i += 2
    return "₹" + ",".join(groups)[::-1].strip(",")

app.jinja_env.filters["inr"] = format_inr


# ======================================================
# STATIC & VITE
# ======================================================

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("Frontend/assets", filename)


@app.route("/@vite/client", methods=["GET"])
def handle_vite_client():
    return Response("", mimetype="application/javascript")


# ======================================================
# PUBLIC PAGES (HOME / ABOUT / CONTACT / LISTING)
# ======================================================

@app.route("/")
def index():
    # Landing page with featured properties from dataset
    featured = []
    if ui_df is not None and not ui_df.empty:
        featured = ui_df.sample(min(6, len(ui_df))).to_dict("records")
    return render_template("index.html", featured_properties=featured)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/listing")
def listing():
    import random

    if ui_df is None or ui_df.empty:
        properties = []
    else:
        properties = ui_df.to_dict("records")

    image_dir = os.path.join(BASE_DIR, "Frontend", "assets", "img", "property")
    image_files = []
    if os.path.isdir(image_dir):
        image_files = [
            f for f in os.listdir(image_dir)
            if os.path.isfile(os.path.join(image_dir, f))
        ]

    for prop in properties:
        if image_files:
            prop["image_url"] = url_for(
                "serve_assets",
                filename=f"img/property/{random.choice(image_files)}",
            )
        else:
            prop["image_url"] = None

    return render_template("listing.html", properties=properties)


# ======================================================
# RENT PREDICTION (PAGE + API)
# ======================================================

@app.route("/rent_prediction", methods=["GET", "POST"])
def rent_prediction():
    form = PredictRentForm()
    prediction_result = None

    if form.validate_on_submit():
        if model is None:
            flash("Prediction model is not available.", "danger")
        else:
            try:
                # Use field names consistent with your original PredictRentForm
                data = {
                    "Size": [form.size.data],
                    "BHK": [form.bhk.data],
                    "Bathroom": [form.bathroom.data],
                    "City": [form.city.data],
                    "Furnishing Status": [form.furnishing_status.data],
                    "Tenant Preferred": [form.tenant_preferred.data],
                    "Area Type": [form.area_type.data],
                }
                input_df = pd.DataFrame(data)
                predicted = model.predict(input_df)[0]
                prediction_result = f"₹{predicted:,.0f}"
            except Exception as e:
                app.logger.error(f"Prediction error: {e}")
                flash("An error occurred during prediction. Please try again.", "danger")

    return render_template("rent-prediction.html", form=form, prediction_result=prediction_result)


@app.route("/predict_rent", methods=["POST"])
@csrf.exempt  # if called from JS without CSRF token
def predict_rent_api():
    if model is None:
        return jsonify({"error": "Model not available"}), 500

    data = request.get_json() or {}
    form = PredictRentForm(data=data)

    if not form.validate():
        return jsonify({"error": "Invalid form submission", "errors": form.errors}), 400

    try:
        input_df = pd.DataFrame({
            "Size": [form.size.data],
            "BHK": [form.bhk.data],
            "Bathroom": [form.bathroom.data],
            "City": [form.city.data],
            "Furnishing Status": [form.furnishing_status.data],
            "Tenant Preferred": [form.tenant_preferred.data],
            "Area Type": [form.area_type.data],
        })
        predicted = model.predict(input_df)[0]

        matching_properties = []
        if ui_df is not None and not ui_df.empty and "Rent" in ui_df.columns:
            min_price = predicted * 0.9
            max_price = predicted * 1.1
            df_match = ui_df[
                (ui_df["Rent"] >= min_price) & (ui_df["Rent"] <= max_price)
            ]
            if form.city.data and form.city.data != "Any":
                df_match = df_match[df_match["City"] == form.city.data]
            matching_properties = df_match.head(50).to_dict("records")

        return jsonify({
            "predicted_rent": f"{predicted:.2f}",
            "matching_properties": matching_properties,
        })
    except Exception as e:
        app.logger.error(f"Prediction API error: {e}")
        return jsonify({"error": "Internal error"}), 500


# ======================================================
# AUTH: LOGIN / REGISTER / SIGNUP / LOGOUT
# ======================================================

class SimpleRegistrationForm(RegistrationForm):
    """Use your existing RegistrationForm but without strict email validator (if needed)."""
    pass

class SimpleLoginForm(LoginForm):
    """Use your existing LoginForm but without strict email validator (if needed)."""
    pass


@app.route("/login", methods=["GET", "POST"])
@rate_limit(max_attempts=5, window_seconds=300)
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = SimpleLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_attempts[request.remote_addr] = []
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("auth/login.html", title="Login", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = SimpleRegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            phone=form.phone.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("auth/register.html", title="Register", form=form)


# 🔥 This fixes the current error in your logs
@app.route("/sign-up")
def signup():
    # Navbar uses url_for('signup'), so we redirect to the register page
    return redirect(url_for("register"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# ======================================================
# DASHBOARDS
# ======================================================

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))
    elif current_user.role == "owner":
        return redirect(url_for("owner_dashboard"))
    else:
        return redirect(url_for("customer_dashboard"))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))
    properties = Property.query.all()
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template(
        "admin/dashboard.html", properties=properties, bookings=bookings, users=users
    )


@app.route("/owner/dashboard")
@login_required
def owner_dashboard():
    if current_user.role != "owner":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template("owner/dashboard.html", properties=properties)


@app.route("/customer/dashboard", methods=["GET", "POST"])
@login_required
def customer_dashboard():
    if current_user.role != "customer":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))

    form = SearchForm()
    properties_query = Property.query

    if form.validate_on_submit():
        try:
            if form.location.data:
                properties_query = properties_query.filter(
                    Property.city.ilike(f"%{form.location.data}%")
                )
            if form.min_price.data is not None:
                properties_query = properties_query.filter(
                    Property.price >= form.min_price.data
                )
            if form.max_price.data is not None:
                properties_query = properties_query.filter(
                    Property.price <= form.max_price.data
                )
            if form.bedrooms.data is not None:
                properties_query = properties_query.filter(
                    Property.bedrooms >= form.bedrooms.data
                )
            if form.bathrooms.data is not None:
                properties_query = properties_query.filter(
                    Property.bathrooms >= form.bathrooms.data
                )
            if form.min_size.data is not None:
                properties_query = properties_query.filter(
                    Property.size >= form.min_size.data
                )
            if form.max_size.data is not None:
                properties_query = properties_query.filter(
                    Property.size <= form.max_size.data
                )
            if form.furnishing_status.data:
                properties_query = properties_query.filter(
                    Property.furnishing_status == form.furnishing_status.data
                )
            if form.tenant_preferred.data:
                properties_query = properties_query.filter(
                    Property.tenant_preferred == form.tenant_preferred.data
                )
        except Exception as e:
            app.logger.error(f"Search error: {e}")
            flash("An error occurred while processing your search.", "danger")

    properties = properties_query.all()

    # Default map on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    for prop in properties:
        if prop.latitude and prop.longitude:
            folium.Marker(
                [prop.latitude, prop.longitude],
                popup=f"<b>{prop.title}</b><br>₹{prop.price}/month<br>"
                      f"<a href='{url_for('customer_property_detail', property_id=prop.id)}'>View</a>",
                tooltip=prop.title,
            ).add_to(m)
    map_html = m._repr_html_()

    return render_template(
        "customer/dashboard.html",
        form=form,
        properties=properties,
        map_html=map_html,
    )


# ======================================================
# OWNER: PROPERTY CRUD
# ======================================================

@app.route("/owner/add_property", methods=["GET", "POST"])
@login_required
def add_property():
    if current_user.role != "owner":
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for("dashboard"))
    form = PropertyForm()
    if form.validate_on_submit():
        prop = Property(
            title=form.title.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            price=form.price.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            owner_id=current_user.id,
        )
        db.session.add(prop)
        db.session.commit()
        flash("Property added successfully!", "success")
        return redirect(url_for("owner_dashboard"))
    return render_template("owner/add_property.html", form=form)


@app.route("/owner/edit_property/<int:property_id>", methods=["GET", "POST"])
@login_required
def edit_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        flash("You are not authorized to edit this property", "danger")
        return redirect(url_for("owner_dashboard"))

    form = PropertyForm(obj=prop)
    if form.validate_on_submit():
        prop.title = form.title.data
        prop.description = form.description.data
        prop.address = form.address.data
        prop.city = form.city.data
        prop.price = form.price.data
        prop.bedrooms = form.bedrooms.data
        prop.bathrooms = form.bathrooms.data
        prop.latitude = form.latitude.data
        prop.longitude = form.longitude.data

        # Image upload
        image_file = form.image_file.data
        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                flash("Invalid file type. Only jpg, jpeg, and png are allowed.", "danger")
                return render_template("owner/edit_property.html", form=form, property=prop)

            if prop.image_file and prop.image_file != "default.jpg":
                old_path = os.path.join(app.root_path, "static", "property_pics", prop.image_file)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(image_file.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            save_dir = os.path.join(app.root_path, "static", "property_pics")
            os.makedirs(save_dir, exist_ok=True)
            image_path = os.path.join(save_dir, filename)
            image_file.save(image_path)
            prop.image_file = filename

        db.session.commit()
        flash("Property updated successfully!", "success")
        return redirect(url_for("owner_dashboard"))

    return render_template("owner/edit_property.html", form=form, property=prop)


@app.route("/owner/delete_property/<int:property_id>", methods=["POST"])
@login_required
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        flash("You are not authorized to delete this property", "danger")
        return redirect(url_for("owner_dashboard"))

    Booking.query.filter_by(property_id=prop.id).delete()
    db.session.delete(prop)
    db.session.commit()
    flash("Property deleted successfully", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/owner/property/<int:property_id>")
@login_required
def owner_property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        flash("You are not authorized to view this property", "danger")
        return redirect(url_for("owner_dashboard"))
    bookings = Booking.query.filter_by(property_id=prop.id).all()
    return render_template("owner/property_detail.html", property=prop, bookings=bookings)


@app.route("/owner/booking/<int:booking_id>/confirm", methods=["POST"])
@login_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    prop = Property.query.get_or_404(booking.property_id)
    if prop.owner_id != current_user.id:
        flash("You are not authorized to confirm this booking", "danger")
        return redirect(url_for("owner_dashboard"))
    booking.status = "confirmed"
    db.session.commit()
    flash("Booking confirmed!", "success")
    return redirect(url_for("owner_property_detail", property_id=prop.id))


@app.route("/owner/booking/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    prop = Property.query.get_or_404(booking.property_id)
    if prop.owner_id != current_user.id:
        flash("You are not authorized to reject this booking", "danger")
        return redirect(url_for("owner_dashboard"))
    booking.status = "rejected"
    db.session.commit()
    flash("Booking rejected", "info")
    return redirect(url_for("owner_property_detail", property_id=prop.id))


# ======================================================
# CUSTOMER: PROPERTY VIEW / BOOKINGS / FAVORITES / REVIEWS
# ======================================================

@app.route("/customer/property/<int:property_id>", methods=["GET", "POST"])
@login_required
def customer_property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    form = BookingForm()
    if form.validate_on_submit():
        overlapping = Booking.query.filter(
            or_(
                (Booking.start_date <= form.start_date.data) & (Booking.end_date >= form.start_date.data),
                (Booking.start_date <= form.end_date.data) & (Booking.end_date >= form.end_date.data),
                (Booking.start_date >= form.start_date.data) & (Booking.end_date <= form.end_date.data),
            )
        ).first()
        if overlapping:
            flash("This property is already booked for the selected dates", "danger")
        else:
            booking = Booking(
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                property_id=prop.id,
                customer_id=current_user.id,
                status="pending",
            )
            db.session.add(booking)
            db.session.commit()
            flash("Booking request sent! The owner will confirm soon.", "success")
            return redirect(url_for("customer_bookings"))

    return render_template("customer/property_detail.html", property=prop, form=form)


@app.route("/customer/bookings")
@login_required
def customer_bookings():
    if current_user.role != "customer":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))
    bookings = Booking.query.filter_by(customer_id=current_user.id).all()
    return render_template("customer/bookings.html", bookings=bookings)


@app.route("/customer/booking/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        flash("You are not authorized to cancel this booking", "danger")
        return redirect(url_for("customer_bookings"))
    if booking.status == "confirmed":
        flash("This booking is already confirmed and cannot be canceled", "warning")
    else:
        db.session.delete(booking)
        db.session.commit()
        flash("Booking canceled successfully", "success")
    return redirect(url_for("customer_bookings"))


@app.route("/property/<int:property_id>")
def property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    review_form = ReviewForm()
    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    is_favorited = False
    if current_user.is_authenticated:
        fav = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()
        is_favorited = fav is not None
    return render_template(
        "property_detail.html",
        property=prop,
        review_form=review_form,
        reviews=reviews,
        is_favorited=is_favorited,
    )


@app.route("/property/<int:property_id>/review", methods=["POST"])
@login_required
def add_review(property_id):
    prop = Property.query.get_or_404(property_id)
    form = ReviewForm()
    if form.validate_on_submit():
        existing = Review.query.filter_by(user_id=current_user.id, property_id=property_id).first()
        if existing:
            flash("You have already reviewed this property.", "warning")
        else:
            review = Review(
                content=form.content.data,
                rating=form.rating.data,
                user_id=current_user.id,
                property_id=property_id,
            )
            db.session.add(review)
            db.session.commit()
            flash("Your review has been added!", "success")
    return redirect(url_for("property_detail", property_id=property_id))


@app.route("/property/<int:property_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(property_id):
    prop = Property.query.get_or_404(property_id)
    fav = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash("Property removed from favorites!", "success")
    else:
        fav = Favorite(user_id=current_user.id, property_id=property_id)
        db.session.add(fav)
        db.session.commit()
        flash("Property added to favorites!", "success")
    return redirect(url_for("property_detail", property_id=property_id))


@app.route("/customer/favorites")
@login_required
def customer_favorites():
    if current_user.role != "customer":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template("customer/favorites.html", favorites=favorites)


# ======================================================
# PROFILE & ACCOUNT
# ======================================================

@app.route("/profile", methods=["GET", "POST"])
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
        if pic_file and hasattr(pic_file, "filename") and pic_file.filename:
            filename = secure_filename(pic_file.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            pic_dir = os.path.join(app.root_path, "static", "profile_pics")
            os.makedirs(pic_dir, exist_ok=True)
            pic_path = os.path.join(pic_dir, filename)
            pic_file.save(pic_path)
            if current_user.profile_pic and current_user.profile_pic != "default.jpg":
                old_pic_path = os.path.join(pic_dir, current_user.profile_pic)
                if os.path.exists(old_pic_path):
                    os.remove(old_pic_path)
            current_user.profile_pic = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    profile_data = {
        "profile_pic": current_user.profile_pic,
        "name": current_user.name,
        "username": current_user.username,
        "bio": current_user.bio,
        "email": current_user.email,
        "phone": current_user.phone,
        "dob": str(current_user.dob) if current_user.dob else "",
        "location": current_user.location,
        "timezone": current_user.timezone,
        "verified": current_user.verified,
        "role": current_user.role,
        "member_since": str(current_user.member_since) if current_user.member_since else "",
        "two_factor_enabled": getattr(current_user, "two_factor_enabled", False),
    }

    if current_user.role == "admin":
        template = "admin/profile.html"
    elif current_user.role == "owner":
        template = "owner/profile.html"
    else:
        template = "customer/profile.html"

    return render_template(template, form=form, profile_data=profile_data)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Current password is incorrect.", "danger")
    return render_template("auth/change_password.html", title="Change Password", form=form)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("login"))
    return render_template("auth/reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("auth/reset_token.html", title="Reset Password", form=form)


# ======================================================
# ADMIN: USERS / PROPERTIES
# ======================================================

@app.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != "admin":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@app.route("/admin/user/delete/<int:user_id>", methods=["POST"])
@login_required
def admin_delete_user(user_id):
    if current_user.role != "admin":
        flash("You are not authorized to perform this action", "danger")
        return redirect(url_for("dashboard"))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account", "danger")
        return redirect(url_for("admin_users"))
    Property.query.filter_by(owner_id=user.id).delete()
    Booking.query.filter_by(customer_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/properties")
@login_required
def admin_properties():
    if current_user.role != "admin":
        flash("You are not authorized to access this page", "danger")
        return redirect(url_for("dashboard"))
    properties = Property.query.all()
    return render_template("admin/properties.html", properties=properties)


@app.route("/admin/property/delete/<int:property_id>", methods=["POST"])
@login_required
def admin_delete_property(property_id):
    if current_user.role != "admin":
        flash("You are not authorized to perform this action", "danger")
        return redirect(url_for("dashboard"))
    prop = Property.query.get_or_404(property_id)
    Booking.query.filter_by(property_id=prop.id).delete()
    db.session.delete(prop)
    db.session.commit()
    flash("Property deleted successfully", "success")
    return redirect(url_for("admin_properties"))


# ======================================================
# MISC / PLACEHOLDER PAGES
# ======================================================

@app.route("/available_properties")
@login_required
def available_properties():
    properties = Property.query.all()
    return render_template("available_properties.html", properties=properties)


@app.route("/bookings")
@login_required
def bookings():
    return render_template("bookings.html")


@app.route("/favorites")
@login_required
def favorites():
    return render_template("favorites.html")


@app.route("/reviews")
@login_required
def reviews_page():
    return render_template("reviews.html")


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


# ======================================================
# DB INIT (LOCAL DEV) + ENTRYPOINT
# ======================================================

def initialize_database():
    with app.app_context():
        db.create_all()
        admin_email = app.config.get("ADMIN_EMAIL", "admin@example.com")
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin = User(
                name="Admin",
                email=admin_email,
                role="admin",
                phone="0000000000",
            )
            admin.set_password(app.config.get("ADMIN_PASSWORD", "admin123"))
            db.session.add(admin)
            db.session.commit()


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
