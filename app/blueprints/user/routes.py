from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.models import Classification
import os, json, shutil
from app.utils.classifier import classify_zip
from werkzeug.utils import secure_filename
from uuid import uuid4
from app import db

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
    zip_path = os.path.join('instance/uploads', filename)

    model_mapping = {
        "resnet50": "models/resnet50_fe.h5",
    }
    model_path = model_mapping.get(model_name)
    if not model_path or not os.path.exists(model_path):
        flash("Wybrany model nie jest dostępny.", "danger")
        return redirect(url_for('user.dashboard'))

    results, session_id = classify_zip(zip_path, model_path)

    classification = Classification(
        user_id=current_user.uid,
        model_name=model_name,
        zip_filename=filename,
        result_folder=os.path.join("app", "static", "classified_temp", session_id),
        download_token=str(uuid4()),
        json_filename="results.json",
        total_images=len(results),
        completed=True
    )
    db.session.add(classification)
    db.session.commit()

    return render_template(
        "user/classification_preview.html", 
        results=results, 
        model_name=model_name,
        download_token=classification.download_token,
        classification_expired=classification.is_expired
    )


@user.route('/classifications')
@login_required
def classifications():
    jobs = Classification.query.filter_by(user_id=current_user.uid).order_by(Classification.created_at.desc()).all()
    return render_template('user/classifications.html', classifications=jobs)


@user.route('/classifications/<int:classification_id>')
@login_required
def preview_classification(classification_id):
    job = Classification.query.get_or_404(classification_id)
    if job.user_id != current_user.uid:
        flash("Brak dostępu do tej klasyfikacji.", "danger")
        return redirect(url_for('user.classifications'))

    json_path = os.path.join(job.result_folder, job.json_filename or "results.json")
    if not os.path.exists(json_path):
        flash("Brak wyników dla tej klasyfikacji.", "warning")
        return redirect(url_for('user.classifications'))

    with open(json_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    return render_template("user/classification_preview.html", results=results, model_name=job.model_name)


@user.route('/classifications/<int:classification_id>/delete', methods=['POST'])
@login_required
def delete_classification(classification_id):
    job = Classification.query.get_or_404(classification_id)
    if job.user_id != current_user.uid:
        flash("Brak dostępu do tego wpisu.", "danger")
        return redirect(url_for('user.classifications'))

    try:
        if os.path.exists(job.result_folder):
            shutil.rmtree(job.result_folder)
    except Exception as e:
        print(f"Błąd podczas usuwania plików: {e}")

    db.session.delete(job)
    db.session.commit()

    flash("Wpis został usunięty.", "success")
    return redirect(url_for('user.classifications'))


@user.route('/download/<token>')
@login_required
def download_zip(token):
    from app.models import Classification
    job = Classification.query.filter_by(download_token=token).first_or_404()

    if job.user_id != current_user.uid:
        flash("Brak dostępu do pliku.", "danger")
        return redirect(url_for('user.classifications'))

    if job.is_expired:
        flash("Ten plik wygasł i nie jest już dostępny do pobrania.", "warning")
        return redirect(url_for('user.classifications'))

    zip_output_path = os.path.join(job.result_folder, 'classified.zip')

    # ZIP folderu jeśli jeszcze nie istnieje
    if not os.path.exists(zip_output_path):
        shutil.make_archive(zip_output_path.replace('.zip', ''), 'zip', job.result_folder)

    return send_file(zip_output_path, as_attachment=True)


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