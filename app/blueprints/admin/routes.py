from flask import render_template, request, redirect, url_for
from flask_login import login_required
from app.decorators import role_required
from app.models import db, User, UserRole
from . import admin
from .forms import EditUserForm

@admin.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

@admin.route('/dashboard/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    form.role.data = user.role.value

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_user.html', form=form, user=user)

@admin.route('/dashboard/user/<int:user_id>/deactivate', methods=['POST'])
@login_required
@role_required('admin')
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin.route('/dashboard/user/<int:user_id>/activate', methods=['POST'])
@login_required
@role_required('admin')
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin.route('/dashboard/user/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))
