from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from . import auth
from .forms import RegistrationForm, LoginForm
from app.models import User, UserRole
from app import db

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Użytkownik już istnieje.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=UserRole.REGULAR
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Rejestracja zakończona sukcesem!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Zalogowano jako {user.username} ({user.role.value})', 'success')

            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_researcher():
                return redirect(url_for('user.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))

        flash('Nieprawidłowy login lub hasło.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany.', 'success')
    return redirect(url_for('core.home'))
