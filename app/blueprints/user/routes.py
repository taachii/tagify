from flask import render_template, redirect, url_for, flash, request, send_file, current_app, jsonify
from flask_login import login_required, current_user
from app.models import Classification
import os, json, shutil, math

from werkzeug.utils import secure_filename
from uuid import uuid4
from app import db
from datetime import datetime, timedelta
import tempfile

from . import user
from .forms import ZipUploadForm, EditProfileForm, ChangePasswordForm

from app.utils.classifier import classify_zip
from app.utils.expiration import expire_user_classifications_after_login


@user.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    expire_user_classifications_after_login(current_user)

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
    model_name = "resnet50"
    zip_path = os.path.join('instance/uploads', filename)

    model_mapping = {
        "resnet50": "models/resnet50_feature_ext_ep40_bs16_augFalse/resnet50_feature_ext_ep40_bs16_augFalse.h5",
    }

    model_path = model_mapping.get(model_name)
    if not model_path or not os.path.exists(model_path):
        flash("Wybrany model nie jest dostępny.", "danger")
        return redirect(url_for('user.dashboard'))

    # Klasyfikacja zdjęć z ZIP-a
    results, session_id = classify_zip(zip_path, model_path)

    # Usuń przesłany plik ZIP po zakończonej klasyfikacji
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"🧹 Usunięto przesłany ZIP: {zip_path}")
    except Exception as e:
        print(f"⚠️ Błąd przy usuwaniu ZIP-a: {e}")

    # Zapisz klasyfikację w bazie
    classification = Classification(
        user_id=current_user.uid,
        model_name=model_name,
        zip_filename=filename,
        result_folder=os.path.join("app", "static", "classified_temp", session_id),
        download_token=str(uuid4()),
        json_filename="results.json",
        total_images=len(results),
        completed=False
    )
    db.session.add(classification)
    db.session.commit()

    return render_template(
        "user/classification_preview.html",
        results=results,
        model_name=model_name,
        download_token=classification.download_token,
        classification_expired=False
    )


@user.route('/classification/preview/data')
@login_required
def classification_preview_data():
    token = request.args.get("token")
    page = int(request.args.get("page", 1))
    per_page = 10

    job = Classification.query.filter_by(download_token=token).first_or_404()

    if job.user_id != current_user.uid:
        return jsonify({"error": "Brak dostępu"}), 403

    json_path = os.path.join(job.result_folder, job.json_filename or "results.json")
    if not os.path.exists(json_path):
        return jsonify({"error": "Brak wyników"}), 404

    with open(json_path, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    total = len(all_results)
    total_pages = math.ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page

    results = all_results[start:end]

    return jsonify({
        "results": results,
        "page": page,
        "total_pages": total_pages,
        "token": token
    })


@user.route('/generate_zip/<token>', methods=['POST'])
@login_required
def generate_zip(token):
    print(f"🔁 [START] Generowanie ZIP-a dla tokenu: {token}")
    job = Classification.query.filter_by(download_token=token).first_or_404()

    if job.user_id != current_user.uid:
        flash("Brak dostępu.", "danger")
        print("⛔ Brak dostępu – użytkownik nie jest właścicielem.")
        return redirect(url_for('user.classifications'))

    json_path = os.path.join(job.result_folder, job.json_filename or "results.json")
    if not os.path.exists(json_path):
        flash("Brak wyników do spakowania.", "warning")
        print("⚠️ Brak pliku results.json – przerwano.")
        return redirect(url_for('user.dashboard'))

    try:
        print("📄 Wczytywanie results.json...")
        with open(json_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"✅ Załadowano {len(results)} rekordów z results.json")

        print("🛠️ Pobieranie poprawek z formularza...")
        corrections = {}
        for key in request.form:
            if key.startswith("corrections[") and key.endswith("]"):
                filename = key[len("corrections["):-1]
                corrections[filename] = request.form[key]

        print(f"🔁 Zastosowywanie poprawek do wyników ({len(corrections)} pozycji)...")
        for r in results:
            if r["filename"] in corrections:
                old = r["predicted_label"]
                new = corrections[r["filename"]]
                r["predicted_label"] = new
                print(f"🖊️ {r['filename']}: {old} → {new}")

        print("💾 Nadpisywanie results.json z poprawkami...")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("✅ results.json zaktualizowany")

        print("📁 Przygotowywanie struktury katalogów klas...")
        with tempfile.TemporaryDirectory() as temp_dir:
            for r in results:
                klas = r["predicted_label"]
                klas_dir = os.path.join(temp_dir, klas)
                os.makedirs(klas_dir, exist_ok=True)

                original_path = os.path.join(job.result_folder, r["filename"])
                if os.path.exists(original_path):
                    shutil.copy2(original_path, os.path.join(klas_dir, r["filename"]))

            downloads_dir = os.path.join(current_app.root_path, "..", "instance", "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            zip_output_path = os.path.join(downloads_dir, f"{token}.zip")

            print("📦 Tworzenie ZIP-a...")
            shutil.make_archive(zip_output_path.replace(".zip", ""), 'zip', temp_dir)
            print("✅ ZIP utworzony")

        job.completed = True
        db.session.commit()
        print("🗂️ Status zapisany w bazie danych")

    except Exception as e:
        print("❌ Błąd przy generowaniu ZIP-a:", e)
        flash("Błąd przy generowaniu ZIP-a.", "danger")
        return redirect(url_for('user.dashboard'))

    print("✅ [KONIEC] ZIP gotowy, redirect na download_ready")
    return redirect(url_for('user.download_ready', token=token))


@user.route('/download_ready/<token>')
@login_required
def download_ready(token):
    job = Classification.query.filter_by(download_token=token).first_or_404()

    if job.user_id != current_user.uid:
        flash("Brak dostępu.", "danger")
        return redirect(url_for('user.classifications'))

    zip_path = os.path.join(current_app.root_path, "..", "instance", "downloads", f"{token}.zip")
    zip_ready = os.path.exists(zip_path)

    return render_template(
        "user/download_ready.html",
        download_token=token,
        total_images=job.total_images,
        model_name=job.model_name,
        zip_ready=zip_ready
    )


@user.route('/download/<token>')
@login_required
def download_zip(token):
    job = Classification.query.filter_by(download_token=token).first_or_404()

    if job.user_id != current_user.uid:
        flash("Brak dostępu do pliku.", "danger")
        return redirect(url_for('user.classifications'))

    expiration_limit = timedelta(hours=24)
    if job.created_at + expiration_limit < datetime.utcnow():
        job.is_expired = True
        db.session.commit()

        try:
            if os.path.exists(job.result_folder):
                shutil.rmtree(job.result_folder)
            zip_path = os.path.join(current_app.root_path, "..", "instance", "downloads", f"{token}.zip")
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception as e:
            print(f"❌ Błąd przy czyszczeniu wygasłych danych: {e}")

        flash("Ten plik wygasł i został usunięty.", "warning")
        return redirect(url_for('user.classifications'))

    zip_output_path = os.path.join(current_app.root_path, "..", "instance", "downloads", f"{token}.zip")

    if not os.path.exists(zip_output_path):
        flash("Brak pliku ZIP.", "warning")
        return redirect(url_for('user.classifications'))

    return send_file(zip_output_path, as_attachment=True, download_name="classified.zip")


@user.route('/classifications')
@login_required
def classifications():
    expire_user_classifications_after_login(current_user)

    jobs = Classification.query.filter_by(user_id=current_user.uid).order_by(Classification.created_at.desc()).all()
    return render_template(
        'user/classifications.html', 
        classifications=jobs, 
        now=datetime.utcnow(), 
        timedelta=timedelta
    )


@user.route('/classifications/<int:classification_id>/delete', methods=['POST'])
@login_required
def delete_classification(classification_id):
    job = Classification.query.get_or_404(classification_id)
    
    if job.user_id != current_user.uid:
        flash("Brak dostępu do tego wpisu.", "danger")
        return redirect(url_for('user.classifications'))

    try:
        # Usuń folder wynikowy
        if os.path.exists(job.result_folder):
            shutil.rmtree(job.result_folder)

        # Usuń powiązany plik ZIP
        zip_path = os.path.join(current_app.root_path, "..", "instance", "downloads", f"{job.download_token}.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)

    except Exception as e:
        print(f"Błąd podczas usuwania plików: {e}")

    db.session.delete(job)
    db.session.commit()

    flash("Wpis i plik ZIP zostały usunięte.", "success")
    return redirect(url_for('user.classifications'))


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
