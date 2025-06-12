from flask import render_template
from flask_login import login_required, current_user
from app.decorators import role_required
from app.models import User
from . import admin

@admin.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)
