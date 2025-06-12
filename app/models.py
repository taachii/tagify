from flask_login import UserMixin
from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLAEnum
from app import db

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
