from extensions import db

from datetime import datetime


class SharedChat(db.Model):

    __tablename__ = "shared_chats"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # UNIQUE SHARE TOKEN
    # =====================================================

    share_token = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    # =====================================================
    # USER ID
    # =====================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # =====================================================
    # SHARED TEXT
    # =====================================================

    text = db.Column(
        db.Text,
        nullable=False
    )

    # =====================================================
    # SENTIMENT PREDICTION
    # =====================================================

    prediction = db.Column(
        db.String(50),
        nullable=False
    )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    confidence = db.Column(
        db.Float,
        nullable=False
    )

    # =====================================================
    # CREATED DATE
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # =====================================================
    # RELATIONSHIP WITH USER
    # =====================================================

    user = db.relationship(
        "User",
        backref=db.backref(
            "shared_chats",
            lazy=True
        )
    )

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<SharedChat "
            f"{self.id} - "
            f"{self.prediction}>"
        )