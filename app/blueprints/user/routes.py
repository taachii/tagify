from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from . import user
from app import db
from .forms import ZipUploadForm, EditProfileForm, ChangePasswordForm

@user.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ZipUploadForm()
    uploaded_filename = request.args.get("uploaded")

    if form.validate_on_submit():
        zip_data = form.zip_file.data
        filename = secure_filename(zip_data.filename)
        upload_path = os.path.join('instance/uploads', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        zip_data.save(upload_path)

        flash('Plik został przesłany poprawnie!', 'success')
        return redirect(url_for('user.dashboard', uploaded=filename))

    return render_template('user/dashboard.html', form=form, uploaded_filename=uploaded_filename)


@user.route('/classify', methods=['POST'])
@login_required
def classify():
    filename = request.args.get("filename")
    model_name = request.form.get("model")
    
    # TODO: uruchom klasyfikację dla pliku i wybranego modelu
    
    flash(f'Rozpoczęto klasyfikację ({model_name}) dla pliku {filename}', 'success')
    return redirect(url_for('user.dashboard'))



@user.route('/account/settings')
@login_required
def account_settings():
    return render_template('user/account_settings.html')


@user.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Profil zaktualizowany", "success")
        return redirect(url_for('user.account_settings'))
    return render_template('user/edit_profile.html', form=form)

@user.route('/account/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Nieprawidłowe obecne hasło", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Hasło zostało zmienione", "success")
            return redirect(url_for('user.account_settings'))
    return render_template('user/change_password.html', form=form)