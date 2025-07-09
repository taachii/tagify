from flask_login import UserMixin
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Enum as SQLAEnum
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from uuid import uuid4

class UserRole(Enum):
    ADMIN = "admin"
    REGULAR = "regular"
    RESEARCHER = "researcher"

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(SQLAEnum(UserRole), nullable=False, default=UserRole.REGULAR)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<User: {self.username}, Role: {self.role.value}>'

    def get_id(self):
        return str(self.uid)

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_regular(self):
        return self.role == UserRole.REGULAR

    def is_researcher(self):
        return self.role == UserRole.RESEARCHER

    def check_password(self, password_plaintext):
        return check_password_hash(self.password, password_plaintext)

    def set_password(self, new_password_plaintext):
        self.password = generate_password_hash(new_password_plaintext)


class Classification(db.Model):
    __tablename__ = 'classifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    model_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    zip_filename = db.Column(db.String, nullable=False)
    result_folder = db.Column(db.String, nullable=False)
    download_token = db.Column(db.String, unique=True, nullable=False)
    json_filename = db.Column(db.String, nullable=True)
    is_expired = db.Column(db.Boolean, default=False)
    total_images = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='classifications')

    @property
    def time_left(self):
        expiration_time = self.created_at + timedelta(hours=24)
        now = datetime.utcnow()
        remaining = expiration_time - now
        if remaining.total_seconds() <= 0:
            return None
        return remaining
