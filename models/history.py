from extensions import db
from datetime import datetime


# =========================================================
# HISTORY MODEL
# =========================================================

class History(db.Model):

    __tablename__ = "history"


    # =====================================================
    # HISTORY ID
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )


    # =====================================================
    # USER ID
    # =====================================================

    user_id = db.Column(
        db.Integer,
        nullable=False
    )


    # =====================================================
    # PREDICTION TEXT
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
    # MODEL CONFIDENCE
    # =====================================================

    confidence = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )


    # =====================================================
    # CREATED AT
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    # =====================================================
    # REPRESENT HISTORY
    # =====================================================

    def __repr__(self):

        return (
            f"<History "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"prediction={self.prediction}>"
        )