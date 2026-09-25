from extensions import db
from flask_login import UserMixin


# =========================================================
# USER MODEL
# =========================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"


    # =====================================================
    # USER ID
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )


    # =====================================================
    # USERNAME
    # =====================================================

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )


    # =====================================================
    # EMAIL
    # =====================================================

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )


    # =====================================================
    # PASSWORD
    # =====================================================

    password = db.Column(
        db.String(255),
        nullable=False
    )


    # =====================================================
    # PROFILE PHOTO
    # =====================================================

    profile_pic = db.Column(
        db.String(200),
        nullable=True
    )


    # =====================================================
    # CREATED AT
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )


    # =====================================================
    # REPRESENT USER
    # =====================================================

    def __repr__(self):

        return (
            f"<User {self.username}>"
        )