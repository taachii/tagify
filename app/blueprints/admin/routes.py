from flask import render_template, request, redirect, url_for, jsonify
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

@admin.route('/dashboard/data')
@login_required
@role_required('admin')
def dashboard_data():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = User.query
    if search:
        query = query.filter(User.username.ilike(f"{search}%"))

    pagination = query.order_by(User.uid.asc()).paginate(page=page, per_page=5)
    users_data = [{
        'uid': user.uid,
        'username': user.username,
        'email': user.email,
        'role': user.role.name,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_active': user.is_active
    } for user in pagination.items]

    return jsonify({
        'users': users_data,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'page': pagination.page,
        'total_pages': pagination.pages
    })

@admin.route('/dashboard/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    # Ustawienie pola roli tylko przy GET
    if request.method == 'GET':
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
