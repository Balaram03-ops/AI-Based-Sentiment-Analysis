from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from Config import Config
from extensions import db, login_manager

from models.user import User
from models.history import History
from models.admin import Admin
from models.shared_chat import SharedChat

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import joblib
import os
import json
import secrets
from datetime import datetime


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# LOAD CONFIGURATION
# =========================================================

app.config.from_object(Config)


# =========================================================
# INITIALIZE EXTENSIONS
# =========================================================

db.init_app(app)

login_manager.init_app(app)

login_manager.login_view = "login"


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# MACHINE LEARNING MODEL PATHS
# =========================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR,
    "vectorizer.pkl"
)


# =========================================================
# CHECK MODEL FILES
# =========================================================

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )


if not os.path.exists(VECTORIZER_PATH):

    raise FileNotFoundError(
        f"Vectorizer file not found: {VECTORIZER_PATH}"
    )


# =========================================================
# LOAD 3-CLASS MACHINE LEARNING MODEL
# =========================================================

try:

    model = joblib.load(
        MODEL_PATH
    )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    print("=" * 70)
    print("3-CLASS SENTIMENT ANALYSIS MODEL LOADED SUCCESSFULLY")
    print("=" * 70)

    print(
        "Model Path:",
        MODEL_PATH
    )

    print(
        "Vectorizer Path:",
        VECTORIZER_PATH
    )

    if hasattr(model, "classes_"):

        print(
            "Model Classes:",
            model.classes_
        )

        print(
            "Number of Classes:",
            len(model.classes_)
        )

    print("=" * 70)


except Exception as e:

    raise RuntimeError(
        f"Unable to load model/vectorizer: {e}"
    )


# =========================================================
# VERIFY 3-CLASS MODEL
# =========================================================

if hasattr(model, "classes_"):

    if len(model.classes_) != 3:

        print("=" * 70)

        print(
            "WARNING: MODEL DOES NOT HAVE EXACTLY 3 CLASSES"
        )

        print(
            "Detected Classes:",
            model.classes_
        )

        print("=" * 70)


# =========================================================
# SENTIMENT NORMALIZATION FUNCTION
# =========================================================

def normalize_sentiment(prediction):

    """
    Converts different possible model outputs into:

        Positive
        Negative
        Neutral
    """

    value = str(
        prediction
    ).strip().lower()


    # -----------------------------------------------------
    # POSITIVE
    # -----------------------------------------------------

    if value in [
        "positive",
        "pos",
        "1"
    ]:

        return "Positive"


    # -----------------------------------------------------
    # NEGATIVE
    # -----------------------------------------------------

    if value in [
        "negative",
        "neg",
        "-1"
    ]:

        return "Negative"


    # -----------------------------------------------------
    # NEUTRAL
    # -----------------------------------------------------

    if value in [
        "neutral",
        "neu",
        "0"
    ]:

        return "Neutral"


    # -----------------------------------------------------
    # UNKNOWN VALUE
    # -----------------------------------------------------

    return str(
        prediction
    )


# =========================================================
# FLASK LOGIN USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    try:

        return db.session.get(
            User,
            int(user_id)
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# =========================================================
# PROFILE PHOTO UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "profile_pics"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# CREATE PROFILE PHOTO FOLDER SAFELY
# =========================================================

if os.path.exists(UPLOAD_FOLDER):

    if not os.path.isdir(UPLOAD_FOLDER):

        raise RuntimeError(
            f"ERROR: '{UPLOAD_FOLDER}' exists "
            "but it is NOT a folder. "
            "Please delete it and create a folder "
            "named 'profile_pics'."
        )

else:

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


# =========================================================
# ALLOWED IMAGE EXTENSIONS
# =========================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif"
}


# =========================================================
# CHECK ALLOWED IMAGE FILE
# =========================================================

def allowed_file(filename):

    return (
        "."
        in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    try:

        db.create_all()

        print("=" * 70)
        print("DATABASE INITIALIZED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:

        print(
            "Database initialization error:",
            e
        )


# =========================================================
# USER REGISTRATION
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    # -----------------------------------------------------
    # IF ALREADY LOGGED IN
    # -----------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )


    # -----------------------------------------------------
    # POST REQUEST
    # -----------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # -------------------------------------------------
        # CHECK EMPTY FIELDS
        # -------------------------------------------------

        if (
            not username
            or
            not email
            or
            not password
        ):

            flash(
                "All fields are required!",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------------------------------
        # CHECK EXISTING USER
        # -------------------------------------------------

        existing_user = User.query.filter(
            (User.username == username)
            |
            (User.email == email)
        ).first()


        if existing_user:

            flash(
                "Username or Email already exists!",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = generate_password_hash(
            password
        )


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )


        # -------------------------------------------------
        # SAVE USER
        # -------------------------------------------------

        try:

            db.session.add(
                new_user
            )

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            app.logger.exception(
                "Registration error: %s",
                e
            )

            flash(
                "Unable to create account.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        flash(
            "Registration Successful! Please Login.",
            "success"
        )

        return redirect(
            url_for("login")
        )


    # -----------------------------------------------------
    # GET REQUEST
    # -----------------------------------------------------

    return render_template(
        "register.html"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not email or not password:

            flash(
                "Email and Password are required!",
                "danger"
            )

            return redirect(
                url_for("admin_login")
            )


        # -------------------------------------------------
        # FIND ADMIN
        # -------------------------------------------------

        admin = Admin.query.filter_by(
            email=email
        ).first()


        # -------------------------------------------------
        # CHECK ADMIN PASSWORD
        # -------------------------------------------------

        if (
            admin
            and
            check_password_hash(
                admin.password,
                password
            )
        ):

            # Save admin information in session

            session["admin_id"] = admin.id

            session["admin_name"] = admin.name

            session["admin_email"] = admin.email


            flash(
                "Admin Login Successful!",
                "success"
            )

            return redirect(
                url_for("admin_dashboard")
            )


        # -------------------------------------------------
        # INVALID LOGIN
        # -------------------------------------------------

        flash(
            "Invalid Admin Email or Password!",
            "danger"
        )


    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route(
    "/admin/dashboard"
)
def admin_dashboard():

    # -----------------------------------------------------
    # CHECK ADMIN LOGIN
    # -----------------------------------------------------

    if "admin_id" not in session:

        flash(
            "Please login as Admin first.",
            "warning"
        )

        return redirect(
            url_for("admin_login")
        )


    # -----------------------------------------------------
    # TOTAL USERS
    # -----------------------------------------------------

    total_users = User.query.count()


    # -----------------------------------------------------
    # GET ALL PREDICTION HISTORY
    # -----------------------------------------------------

    histories = History.query.order_by(
        History.created_at.desc()
    ).all()


    # -----------------------------------------------------
    # TOTAL PREDICTIONS
    # -----------------------------------------------------

    total_predictions = History.query.count()


    # -----------------------------------------------------
    # SENTIMENT COUNTS
    # -----------------------------------------------------

    positive_count = sum(
        1
        for h in histories
        if normalize_sentiment(
            h.prediction
        ).lower() == "positive"
    )


    negative_count = sum(
        1
        for h in histories
        if normalize_sentiment(
            h.prediction
        ).lower() == "negative"
    )


    neutral_count = sum(
        1
        for h in histories
        if normalize_sentiment(
            h.prediction
        ).lower() == "neutral"
    )


    # -----------------------------------------------------
    # SEND DATA TO ADMIN DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "admin_dashboard.html",

        total_users=total_users,

        total_predictions=total_predictions,

        positive_count=positive_count,

        negative_count=negative_count,

        neutral_count=neutral_count,

        histories=histories
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.pop(
        "admin_id",
        None
    )

    session.pop(
        "admin_name",
        None
    )

    session.pop(
        "admin_email",
        None
    )

    flash(
        "Admin logged out successfully.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# USER LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # -----------------------------------------------------
    # ALREADY LOGGED IN
    # -----------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )


    # -----------------------------------------------------
    # POST REQUEST
    # -----------------------------------------------------

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # -------------------------------------------------
        # EMPTY FIELD CHECK
        # -------------------------------------------------

        if (
            not email
            or
            not password
        ):

            flash(
                "Email and Password are required!",
                "danger"
            )

            return redirect(
                url_for("login")
            )


        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = User.query.filter_by(
            email=email
        ).first()


        # -------------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------------

        if (
            user
            and
            check_password_hash(
                user.password,
                password
            )
        ):

            login_user(
                user
            )

            flash(
                "Login Successful!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )


        # -------------------------------------------------
        # INVALID LOGIN
        # -------------------------------------------------

        flash(
            "Invalid Email or Password!",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# USER LOGOUT
# =========================================================

@app.route(
    "/logout"
)
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("login")
    )



# =========================================================
# DASHBOARD
# =========================================================

@app.route(
    "/dashboard"
)
@login_required
def dashboard():

    # -----------------------------------------------------
    # CURRENT USER HISTORY
    # -----------------------------------------------------

    histories = History.query.filter_by(
        user_id=current_user.id
    ).order_by(
        History.created_at.desc()
    ).all()


    # -----------------------------------------------------
    # TOTAL PREDICTIONS
    # -----------------------------------------------------

    total_predictions = len(
        histories
    )


    # -----------------------------------------------------
    # SENTIMENT COUNTS
    # -----------------------------------------------------

    positive_count = sum(
        1
        for h in histories
        if normalize_sentiment(
            h.prediction
        ).lower() == "positive"
    )


    negative_count = sum(
        1
        for h in histories
        if normalize_sentiment(
            h.prediction
        ).lower() == "negative"
    )


    neutral_count = sum(
        1
        for h in histories
        if normalize_sentiment(
            h.prediction
        ).lower() == "neutral"
    )


    # -----------------------------------------------------
    # DAILY PREDICTION TREND
    # -----------------------------------------------------

    daily_counts = {}


    for h in histories:

        if h.created_at:

            date_key = h.created_at.strftime(
                "%d-%m-%Y"
            )

            daily_counts[date_key] = (
                daily_counts.get(
                    date_key,
                    0
                )
                +
                1
            )


    # -----------------------------------------------------
    # SORT DATES
    # -----------------------------------------------------

    sorted_dates = sorted(
        daily_counts.keys(),
        key=lambda x: datetime.strptime(
            x,
            "%d-%m-%Y"
        )
    )


    # -----------------------------------------------------
    # CHART DATA
    # -----------------------------------------------------

    trend_labels = sorted_dates

    trend_counts = [
        daily_counts[date]
        for date in sorted_dates
    ]


    # -----------------------------------------------------
    # MODEL COMPARISON DATA
    # -----------------------------------------------------

    comparison_path = os.path.join(
        BASE_DIR,
        "model_comparison.json"
    )

    model_comparison = []


    if os.path.exists(
        comparison_path
    ):

        try:

            with open(
                comparison_path,
                "r",
                encoding="utf-8"
            ) as file:

                comparison_data = json.load(
                    file
                )


            # -------------------------------------------------
            # FORMAT 1: LIST
            # -------------------------------------------------

            if isinstance(
                comparison_data,
                list
            ):

                model_comparison = comparison_data


            # -------------------------------------------------
            # FORMAT 2: DICTIONARY
            # -------------------------------------------------

            elif isinstance(
                comparison_data,
                dict
            ):

                if "models" in comparison_data:

                    model_comparison = (
                        comparison_data["models"]
                    )

                elif "comparison" in comparison_data:

                    model_comparison = (
                        comparison_data["comparison"]
                    )

                else:

                    # Direct model-name dictionary

                    model_comparison = []

                    for model_name, metrics in comparison_data.items():

                        if isinstance(
                            metrics,
                            dict
                        ):

                            model_comparison.append({

                                "model": model_name,

                                "accuracy": metrics.get(
                                    "accuracy",
                                    0
                                ),

                                "precision": metrics.get(
                                    "precision",
                                    0
                                ),

                                "recall": metrics.get(
                                    "recall",
                                    0
                                ),

                                "f1_score": metrics.get(
                                    "f1_score",
                                    0
                                )
                            })


        except Exception as e:

            app.logger.exception(
                "Model comparison loading error: %s",
                e
            )

            model_comparison = []


    # -----------------------------------------------------
    # SEND DATA TO DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "dashboard.html",

        user=current_user,

        total_predictions=total_predictions,

        positive_count=positive_count,

        negative_count=negative_count,

        neutral_count=neutral_count,

        histories=histories,

        trend_labels=trend_labels,

        trend_counts=trend_counts,

        model_comparison=model_comparison
    )


# =========================================================
# PROFILE PAGE
# =========================================================

@app.route(
    "/profile"
)
@login_required
def profile():

    return render_template(
        "profile.html",
        user=current_user
    )


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.route(
    "/update-profile",
    methods=["POST"]
)
@login_required
def update_profile():

    # -----------------------------------------------------
    # GET USERNAME
    # -----------------------------------------------------

    username = request.form.get(
        "username",
        ""
    ).strip()


    # -----------------------------------------------------
    # CHECK USERNAME
    # -----------------------------------------------------

    if not username:

        flash(
            "Username cannot be empty.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )


    # -----------------------------------------------------
    # CHECK DUPLICATE USERNAME
    # -----------------------------------------------------

    existing_user = User.query.filter(
        User.username == username,
        User.id != current_user.id
    ).first()


    if existing_user:

        flash(
            "Username already exists!",
            "danger"
        )

        return redirect(
            url_for("profile")
        )


    # -----------------------------------------------------
    # UPDATE USERNAME
    # -----------------------------------------------------

    current_user.username = username


    # -----------------------------------------------------
    # GET PROFILE PHOTO
    # -----------------------------------------------------

    file = request.files.get(
        "profile_pic"
    )


    # -----------------------------------------------------
    # PROFILE PHOTO UPLOAD
    # -----------------------------------------------------

    if file and file.filename:

        # -------------------------------------------------
        # CHECK FILE EXTENSION
        # -------------------------------------------------

        if not allowed_file(
            file.filename
        ):

            flash(
                "Only PNG, JPG, JPEG and GIF images are allowed.",
                "danger"
            )

            return redirect(
                url_for("profile")
            )


        # -------------------------------------------------
        # SECURE FILE NAME
        # -------------------------------------------------

        original_filename = secure_filename(
            file.filename
        )


        # -------------------------------------------------
        # CHECK SECURE FILE NAME
        # -------------------------------------------------

        if (
            not original_filename
            or
            "." not in original_filename
        ):

            flash(
                "Invalid image file.",
                "danger"
            )

            return redirect(
                url_for("profile")
            )


        # -------------------------------------------------
        # GET EXTENSION
        # -------------------------------------------------

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()


        # -------------------------------------------------
        # CREATE USER FILE NAME
        # -------------------------------------------------

        filename = (
            f"user_{current_user.id}."
            f"{extension}"
        )


        # -------------------------------------------------
        # FULL SAVE PATH
        # -------------------------------------------------

        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )


        # -------------------------------------------------
        # DELETE OLD PHOTO
        # -------------------------------------------------

        old_profile_pic = (
            current_user.profile_pic
        )


        if old_profile_pic:

            old_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                old_profile_pic
            )


            if os.path.exists(
                old_path
            ):

                try:

                    os.remove(
                        old_path
                    )

                except OSError as e:

                    app.logger.warning(
                        "Could not delete old profile photo: %s",
                        e
                    )


        # -------------------------------------------------
        # SAVE NEW PHOTO
        # -------------------------------------------------

        try:

            file.save(
                save_path
            )

        except OSError as e:

            app.logger.exception(
                "Profile photo save error: %s",
                e
            )

            flash(
                "Unable to save profile photo.",
                "danger"
            )

            return redirect(
                url_for("profile")
            )


        # -------------------------------------------------
        # SAVE FILE NAME IN DATABASE
        # -------------------------------------------------

        current_user.profile_pic = filename


    # -----------------------------------------------------
    # SAVE DATABASE
    # -----------------------------------------------------

    try:

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        app.logger.exception(
            "Profile update error: %s",
            e
        )

        flash(
            "Unable to update profile.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )


    flash(
        "Profile updated successfully!",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# =========================================================
# HOME / SENTIMENT ANALYSIS PAGE
# =========================================================

@app.route("/")
@login_required
def home():

    return render_template(
        "index.html"
    )



# =========================================================
# SENTIMENT PREDICTION
# =========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
@login_required
def predict():

    # -----------------------------------------------------
    # GET TEXT FROM FORM
    # -----------------------------------------------------

    text = request.form.get(
        "text",
        ""
    ).strip()


    # -----------------------------------------------------
    # CHECK EMPTY TEXT
    # -----------------------------------------------------

    if not text:

        flash(
            "Please enter some text for sentiment analysis.",
            "warning"
        )

        return redirect(
            url_for("dashboard")
        )


    try:

        # -------------------------------------------------
        # TRANSFORM TEXT
        # -------------------------------------------------

        features = vectorizer.transform(
            [text]
        )


        # -------------------------------------------------
        # PREDICT SENTIMENT
        # -------------------------------------------------

        prediction = model.predict(
            features
        )[0]


        # -------------------------------------------------
        # NORMALIZE SENTIMENT
        # -------------------------------------------------

        sentiment = normalize_sentiment(
            prediction
        )


        # -------------------------------------------------
        # CONFIDENCE SCORE
        # -------------------------------------------------

        confidence = None


        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = model.predict_proba(
                features
            )[0]

            confidence = (
                float(
                    max(probabilities)
                )
                *
                100
            )


        # -------------------------------------------------
        # SAVE PREDICTION TO DATABASE
        # -------------------------------------------------

        new_history = History(
            user_id=current_user.id,
            text=text,
            prediction=sentiment,
            confidence=confidence
        )


        db.session.add(
            new_history
        )

        db.session.commit()


        # -------------------------------------------------
        # GET CURRENT USER HISTORY
        # -------------------------------------------------

        histories = History.query.filter_by(
            user_id=current_user.id
        ).order_by(
            History.created_at.desc()
        ).all()


        # -------------------------------------------------
        # TOTAL PREDICTIONS
        # -------------------------------------------------

        total_predictions = len(
            histories
        )


        # -------------------------------------------------
        # POSITIVE COUNT
        # -------------------------------------------------

        positive_count = sum(
            1
            for h in histories
            if normalize_sentiment(
                h.prediction
            ).lower() == "positive"
        )


        # -------------------------------------------------
        # NEGATIVE COUNT
        # -------------------------------------------------

        negative_count = sum(
            1
            for h in histories
            if normalize_sentiment(
                h.prediction
            ).lower() == "negative"
        )


        # -------------------------------------------------
        # NEUTRAL COUNT
        # -------------------------------------------------

        neutral_count = sum(
            1
            for h in histories
            if normalize_sentiment(
                h.prediction
            ).lower() == "neutral"
        )


        # -------------------------------------------------
        # DAILY PREDICTION TREND
        # -------------------------------------------------

        daily_counts = {}


        for h in histories:

            if h.created_at:

                date_key = h.created_at.strftime(
                    "%d-%m-%Y"
                )

                daily_counts[date_key] = (
                    daily_counts.get(
                        date_key,
                        0
                    )
                    +
                    1
                )


        # -------------------------------------------------
        # SORT DATES
        # -------------------------------------------------

        sorted_dates = sorted(
            daily_counts.keys(),
            key=lambda x: datetime.strptime(
                x,
                "%d-%m-%Y"
            )
        )


        # -------------------------------------------------
        # CHART DATA
        # -------------------------------------------------

        trend_labels = sorted_dates

        trend_counts = [
            daily_counts[date]
            for date in sorted_dates
        ]


        # -------------------------------------------------
        # MODEL COMPARISON DATA
        # -------------------------------------------------

        comparison_path = os.path.join(
            BASE_DIR,
            "model_comparison.json"
        )

        model_comparison = []


        if os.path.exists(
            comparison_path
        ):

            try:

                with open(
                    comparison_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    comparison_data = json.load(
                        file
                    )


                if isinstance(
                    comparison_data,
                    list
                ):

                    model_comparison = (
                        comparison_data
                    )


                elif isinstance(
                    comparison_data,
                    dict
                ):

                    if "models" in comparison_data:

                        model_comparison = (
                            comparison_data["models"]
                        )

                    elif "comparison" in comparison_data:

                        model_comparison = (
                            comparison_data["comparison"]
                        )


            except Exception as e:

                app.logger.exception(
                    "Model comparison loading error: %s",
                    e
                )

                model_comparison = []


        # -------------------------------------------------
        # SHOW DASHBOARD WITH RESULT
        # -------------------------------------------------

        return render_template(
        "index.html",

    user=current_user,

    total_predictions=total_predictions,

    positive_count=positive_count,

    negative_count=negative_count,

    neutral_count=neutral_count,

    histories=histories,

    trend_labels=trend_labels,

    trend_counts=trend_counts,

    model_comparison=model_comparison,

    prediction=sentiment,

    confidence=confidence,

    text=text
)
    # -----------------------------------------------------
    # ERROR HANDLING
    # -----------------------------------------------------

    except Exception as e:

        db.session.rollback()

        app.logger.exception(
            "Prediction Error: %s",
            e
        )

        flash(
            "An error occurred while analyzing the text.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

# =========================================================
# SHARE PREDICTION
# =========================================================

@app.route(
    "/share",
    methods=["POST"]
)
@login_required
def share_prediction():

    # -----------------------------------------------------
    # GET DATA FROM FORM
    # -----------------------------------------------------

    text = request.form.get(
        "text",
        ""
    ).strip()

    prediction = request.form.get(
        "prediction",
        ""
    ).strip()

    confidence = request.form.get(
        "confidence",
        "0"
    ).strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not text:

        flash(
            "Nothing to share.",
            "warning"
        )

        return redirect(
            url_for("home")
        )


    if not prediction:

        flash(
            "Prediction information is missing.",
            "warning"
        )

        return redirect(
            url_for("home")
        )


    # -----------------------------------------------------
    # CONVERT CONFIDENCE TO FLOAT
    # -----------------------------------------------------

    try:

        confidence_value = float(
            confidence
        )

    except (
        ValueError,
        TypeError
    ):

        confidence_value = 0.0


    # -----------------------------------------------------
    # KEEP CONFIDENCE IN VALID RANGE
    # -----------------------------------------------------

    if confidence_value < 0:

        confidence_value = 0.0


    if confidence_value > 100:

        confidence_value = 100.0


    # -----------------------------------------------------
    # NORMALIZE SHARED SENTIMENT
    # -----------------------------------------------------

    prediction = normalize_sentiment(
        prediction
    )


    # -----------------------------------------------------
    # GENERATE UNIQUE SHARE TOKEN
    # -----------------------------------------------------

    share_token = secrets.token_urlsafe(
        16
    )


    # -----------------------------------------------------
    # CREATE SHARED CHAT OBJECT
    # -----------------------------------------------------

    shared_chat = SharedChat(
        share_token=share_token,
        user_id=current_user.id,
        text=text,
        prediction=prediction,
        confidence=confidence_value
    )


    # -----------------------------------------------------
    # SAVE TO MYSQL
    # -----------------------------------------------------

    try:

        db.session.add(
            shared_chat
        )

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        app.logger.exception(
            "Share prediction error: %s",
            e
        )

        flash(
            "Unable to share prediction.",
            "danger"
        )

        return redirect(
            url_for("home")
        )


    # -----------------------------------------------------
    # CREATE PUBLIC SHARE URL
    # -----------------------------------------------------

    share_url = url_for(
        "view_shared_chat",
        share_token=share_token,
        _external=True
    )


    # -----------------------------------------------------
    # SHOW SHARE RESULT PAGE
    # -----------------------------------------------------

    return render_template(
        "share_result.html",

        share_url=share_url,

        shared_chat=shared_chat
    )


# =========================================================
# VIEW SHARED CHAT
# =========================================================

@app.route(
    "/shared/<share_token>"
)
def view_shared_chat(share_token):

    shared_chat = SharedChat.query.filter_by(
        share_token=share_token
    ).first()


    # -----------------------------------------------------
    # CHECK SHARE TOKEN
    # -----------------------------------------------------

    if not shared_chat:

        flash(
            "Shared prediction not found or link is invalid.",
            "danger"
        )

        # If user is logged in, go to home.
        # Otherwise go to login.

        if current_user.is_authenticated:

            return redirect(
                url_for("home")
            )

        return redirect(
            url_for("login")
        )


    # -----------------------------------------------------
    # SHOW SHARED CHAT
    # -----------------------------------------------------

    return render_template(
        "shared_chat.html",
        shared_chat=shared_chat
    )


# =========================================================
# PREDICTION HISTORY
# SEARCH + 3-CLASS FILTER
# =========================================================

@app.route(
    "/history"
)
@login_required
def history():

    # -----------------------------------------------------
    # GET SEARCH
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        ""
    ).strip()


    # -----------------------------------------------------
    # GET SENTIMENT
    # -----------------------------------------------------

    sentiment = request.args.get(
        "sentiment",
        ""
    ).strip().lower()


    # -----------------------------------------------------
    # CURRENT USER HISTORY
    # -----------------------------------------------------

    query = History.query.filter_by(
        user_id=current_user.id
    )


    # -----------------------------------------------------
    # SEARCH TEXT
    # -----------------------------------------------------

    if search:

        query = query.filter(
            History.text.ilike(
                f"%{search}%"
            )
        )


    # -----------------------------------------------------
    # 3-CLASS SENTIMENT FILTER
    # -----------------------------------------------------

    if sentiment in [
        "positive",
        "negative",
        "neutral"
    ]:

        query = query.filter(
            History.prediction.ilike(
                sentiment
            )
        )


    # -----------------------------------------------------
    # LATEST FIRST
    # -----------------------------------------------------

    histories = query.order_by(
        History.created_at.desc()
    ).all()


    # -----------------------------------------------------
    # SEND DATA TO HTML
    # -----------------------------------------------------

    return render_template(
        "history.html",

        histories=histories,

        search=search,

        sentiment=sentiment
    )


# =========================================================
# DELETE PREDICTION HISTORY
# =========================================================

@app.route(
    "/history/delete/<int:history_id>",
    methods=["POST"]
)
@login_required
def delete_history(history_id):

    # -----------------------------------------------------
    # FIND CURRENT USER'S HISTORY ONLY
    # -----------------------------------------------------

    history_item = History.query.filter_by(
        id=history_id,
        user_id=current_user.id
    ).first()


    # -----------------------------------------------------
    # CHECK HISTORY
    # -----------------------------------------------------

    if not history_item:

        flash(
            "Prediction history not found!",
            "danger"
        )

        return redirect(
            url_for("history")
        )


    # -----------------------------------------------------
    # DELETE HISTORY
    # -----------------------------------------------------

    try:

        db.session.delete(
            history_item
        )

        db.session.commit()


    except Exception as e:

        db.session.rollback()

        app.logger.exception(
            "History delete error: %s",
            e
        )

        flash(
            "Unable to delete prediction.",
            "danger"
        )

        return redirect(
            url_for("history")
        )


    # -----------------------------------------------------
    # SUCCESS MESSAGE
    # -----------------------------------------------------

    flash(
        "Prediction deleted successfully!",
        "success"
    )

    return redirect(
        url_for("history")
    )


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "AI SENTIMENT ANALYSIS - 3 CLASS APPLICATION"
    )

    print("=" * 70)


    print(
        "Current Working Directory:",
        os.getcwd()
    )

    print()


    print(
        "Model Path:",
        MODEL_PATH
    )

    print()


    print(
        "Vectorizer Path:",
        VECTORIZER_PATH
    )

    print()


    print(
        "Upload Folder:",
        UPLOAD_FOLDER
    )

    print()


    if hasattr(
        model,
        "classes_"
    ):

        print(
            "Final Model Classes:",
            model.classes_
        )

    print("=" * 70)


    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )