from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models import UserRole

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Musisz być zalogowany.", "warning")
                return redirect(url_for("auth.login"))

            if current_user.role != required_role:
                flash("Brak uprawnień do tej strony.", "danger")
                return redirect(url_for("dashboard"))

            return f(*args, **kwargs)
        return wrapped
    return decorator