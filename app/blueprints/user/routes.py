from flask import render_template, redirect, url_for, flash, request, send_file, current_app, jsonify # type: ignore
from flask_login import login_required, current_user # type: ignore
from app.models import Classification, UserPath
import os, json, shutil, math
import subprocess, platform

from werkzeug.utils import secure_filename # type: ignore
from uuid import uuid4
from app import db
from datetime import datetime, timedelta
import tempfile
import zipfile

from . import user
from .forms import ZipUploadForm, EditProfileForm, ChangePasswordForm, ModelSelectionForm, UserPathsForm, OpenPathForm
from wtforms import StringField # type: ignore

from app.utils.classifier import classify_zip, get_available_models
from app.utils.expiration import expire_user_classifications_after_login

DEFAULT_MODEL_DIRECTORY = os.path.join("models", "efficientnetb0_feature_ext_ep40_bs16_augFalse_cl7")
DEFAULT_MODEL_PATH = os.path.join(DEFAULT_MODEL_DIRECTORY, "efficientnetb0_feature_ext_ep40_bs16_augFalse_cl7.keras")


@user.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    expire_user_classifications_after_login(current_user)

    MAX_ZIP_SIZE_MB = 50
    MAX_ZIP_SIZE_BYTES = MAX_ZIP_SIZE_MB * 1024 * 1024

    upload_form = ZipUploadForm()
    model_form = None
    uploaded_filename = request.args.get("uploaded")

    if current_user.is_researcher():
        model_form = ModelSelectionForm()
        model_form.model.choices = get_available_models()

    if upload_form.validate_on_submit():
        zip_data = upload_form.zip_file.data
        filename = secure_filename(zip_data.filename)

        # Sprawdzenie rozmiaru ZIP-a
        zip_data.seek(0, os.SEEK_END)
        file_size = zip_data.tell()
        zip_data.seek(0)

        if file_size > MAX_ZIP_SIZE_BYTES:
            flash(f"Przesłany plik ZIP przekracza limit {MAX_ZIP_SIZE_MB}MB.", "warning")
            return redirect(url_for('user.dashboard'))

        
        upload_path = os.path.join('instance/uploads', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        zip_data.save(upload_path)

        flash('Plik został przesłany poprawnie!', 'success')
        return redirect(url_for('user.dashboard', uploaded=filename))

    return render_template(
        'user/dashboard.html', 
        form=upload_form,
        model_form=model_form,
        uploaded_filename=uploaded_filename,
        available_models=get_available_models() if current_user.is_researcher() else None
    )


@user.route('/classify', methods=['POST'])
@login_required
def classify():
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    filename = request.args.get("filename")
    zip_path = os.path.join('instance/uploads', filename)

    model_path = request.form.get("model_path", "") or DEFAULT_MODEL_PATH

    if not os.path.exists(model_path):
        flash("Wybrany model nie istnieje.", "warning")
        return redirect(url_for('user.dashboard'))

    # Sprawdzenie czy plik istnieje i jest ZIP-em
    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        flash("Przesłany plik nie jest prawidłowym archiwum ZIP.", "warning")
        return redirect(url_for('user.dashboard'))

    # Walidacja zawartości ZIP-a: tylko obrazy
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        bad_files = []
        image_count = 0

        for name in zip_ref.namelist():
            if name.endswith('/') or name.startswith('__MACOSX'):  # pomiń foldery i systemowe pliki
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                bad_files.append(name)
            else:
                image_count += 1

        if not image_count:
            flash("Archiwum ZIP nie zawiera żadnych zdjęć.", "warning")
            return redirect(url_for('user.dashboard'))

        if bad_files:
            preview = ', '.join(bad_files[:3]) + ('...' if len(bad_files) > 3 else '')
            flash(f"ZIP zawiera nieobsługiwane pliki: {preview}", "warning")
            return redirect(url_for('user.dashboard'))

    # Klasyfikacja zdjęć
    results, session_id = classify_zip(zip_path, model_path)

    # Usuń przesłany ZIP po klasyfikacji
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
    except Exception as e:
        print(f"Błąd przy usuwaniu ZIP-a: {e}")

    # Zapisz klasyfikację do bazy
    classification = Classification(
        user_id=current_user.uid,
        model_name=os.path.basename(model_path),
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
        model_name=os.path.basename(model_path),
        download_token=classification.download_token,
        classification_expired=False
    )


@user.route('/classification/preview/data')
@login_required
def classification_preview_data():
    token = request.args.get("token")
    page = int(request.args.get("page", 1))
    per_page = 8

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


def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base} ({counter}){ext}"
        counter += 1

    return new_filename

@user.route('/generate_zip/<token>', methods=['POST'])
@login_required
def generate_zip(token):
    print(f"[START] Generowanie ZIP-a dla tokenu: {token}")
    job = Classification.query.filter_by(download_token=token).first_or_404()

    if job.user_id != current_user.uid:
        flash("Brak dostępu.", "danger")
        print("Brak dostępu – użytkownik nie jest właścicielem.")
        return redirect(url_for('user.classifications'))

    json_path = os.path.join(job.result_folder, job.json_filename or "results.json")
    if not os.path.exists(json_path):
        flash("Brak wyników do spakowania.", "warning")
        print("Brak pliku results.json – przerwano.")
        return redirect(url_for('user.dashboard'))

    try:
        print("Wczytywanie results.json...")
        with open(json_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"Załadowano {len(results)} rekordów z results.json")

        print("Pobieranie poprawek z formularza...")
        corrections = {}
        for key in request.form:
            if key.startswith("corrections[") and key.endswith("]"):
                filename = key[len("corrections["):-1]
                corrections[filename] = request.form[key]

        print(f"Zastosowywanie poprawek do wyników ({len(corrections)} pozycji)...")
        for r in results:
            if r["filename"] in corrections:
                original = r["predicted_label"]
                corrected = corrections[r["filename"]]
                if corrected != original:
                    r["corrected_label"] = corrected
                    print(f"🖊️ {r['filename']}: {original} → {corrected}")
                else:
                    r.pop("corrected_label", None)  # usuwamy jeśli identyczna

        print("Nadpisywanie results.json z poprawkami...")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("results.json zaktualizowany")

        # 📊 Generowanie confusion matrix
        from app.utils.metrics import save_confusion_matrix

        try:
            corrected_results = [
                (r["corrected_label"], r["predicted_label"])
                for r in results if "corrected_label" in r
            ]
            if corrected_results:
                # Tymczasowa ścieżka (do katalogu wynikowego)
                cm_temp_path = os.path.join(job.result_folder, "confusion_matrix.png")
                save_confusion_matrix(corrected_results, cm_temp_path)
                print(f"Zapisano confusion matrix: {cm_temp_path}")

                # Docelowa trwała ścieżka (statyczna)
                cm_static_dir = os.path.join(current_app.root_path, "static", "confusion_matrices", job.download_token)
                os.makedirs(cm_static_dir, exist_ok=True)
                cm_final_path = os.path.join(cm_static_dir, "confusion_matrix.png")
                shutil.copy2(cm_temp_path, cm_final_path)
                print(f"Confusion matrix skopiowana do: {cm_final_path}")
            else:
                print("Brak poprawek – pomijam confusion matrix.")
        except Exception as e:
            print(f"Błąd przy generowaniu confusion matrix: {e}")

        print("Przygotowywanie struktury katalogów klas...")
        from app.models import UserPath
        with tempfile.TemporaryDirectory() as temp_dir:
            for r in results:
                klas = r.get("corrected_label", r["predicted_label"])
                klas_dir = os.path.join(temp_dir, klas)
                os.makedirs(klas_dir, exist_ok=True)

                original_path = os.path.join(job.result_folder, r["filename"])
                if os.path.exists(original_path):
                    shutil.copy2(original_path, os.path.join(klas_dir, r["filename"]))

                    # Kopiowanie do folderów lokalnych użytkownika (jeśli ustawione)
                    dest_path = UserPath.query.filter_by(user_id=current_user.uid, class_label=klas).first()
                    if dest_path and os.path.isdir(dest_path.path):
                        try:
                            dest_filename = get_unique_filename(dest_path.path, r["filename"])
                            shutil.copy2(original_path, os.path.join(dest_path.path, dest_filename))
                            print(f"Skopiowano do lokalnej ścieżki: {dest_path.path}")
                        except Exception as e:
                            print(f"Błąd przy kopiowaniu do {dest_path.path}: {e}")

            downloads_dir = os.path.join(current_app.root_path, "..", "instance", "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            zip_output_path = os.path.join(downloads_dir, f"{token}.zip")

            print("Tworzenie ZIP-a...")
            shutil.make_archive(zip_output_path.replace(".zip", ""), 'zip', temp_dir)
            print("ZIP utworzony")

        job.completed = True
        db.session.commit()
        print("Status zapisany w bazie danych")

        try:
            if os.path.exists(job.result_folder):
                shutil.rmtree(job.result_folder)
                print(f"Folder tymczasowy usunięty: {job.result_folder}")
        except Exception as e:
            print(f"Błąd przy usuwaniu folderu tymczasowego: {e}")

    except Exception as e:
        print("Błąd przy generowaniu ZIP-a:", e)
        flash("Błąd przy generowaniu ZIP-a.", "danger")
        return redirect(url_for('user.dashboard'))

    print("[KONIEC] ZIP gotowy, redirect na download_ready")
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

    user_paths = {entry.class_label: entry.path for entry in UserPath.query.filter_by(user_id=current_user.uid).all()}

    form = OpenPathForm()
    form.class_selector.choices = [(label, f"{label} – {path}") for label, path in user_paths.items()]

    cm_final_path = os.path.join(current_app.root_path, "static", "confusion_matrices", token, "confusion_matrix.png")
    confusion_matrix_exists = os.path.exists(cm_final_path)
    print(f"confusion_matrix_exists: {confusion_matrix_exists}")

    return render_template(
        "user/download_ready.html",
        download_token=token,
        total_images=job.total_images,
        model_name=job.model_name,
        zip_ready=zip_ready,
        user_paths=user_paths,
        open_path_form=form,
        confusion_matrix_exists=confusion_matrix_exists
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
            print(f"Błąd przy czyszczeniu wygasłych danych: {e}")

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

    cm_static_dir = os.path.join(current_app.root_path, "static", "confusion_matrices", job.download_token)
    if os.path.exists(cm_static_dir):
        try:
            shutil.rmtree(cm_static_dir)
            print(f"Usunięto confusion matrix: {cm_static_dir}")
        except Exception as e:
            print(f"Błąd przy usuwaniu confusion matrix: {e}")    

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


@user.route('/account/paths', methods=['GET', 'POST'])
@login_required
def manage_paths():
    form = UserPathsForm()

    if form.validate_on_submit():
        errors = []

        for name, field in form._fields.items():
            if name in ("csrf_token", "submit"):
                continue
            if not isinstance(field, StringField):
                continue  # Pomijamy np. submit, csrf_token

            raw_path = field.data.strip()
            if raw_path:
                normalized_path = os.path.normpath(raw_path)
            
                if not os.path.isdir(normalized_path):
                    errors.append(f"Ścieżka dla pola '{field.label.text}' jest nieprawidłowa lub nie istnieje.")
                    continue

                path_entry = UserPath.query.filter_by(user_id=current_user.uid, class_label=name).first()
                if path_entry:
                    path_entry.path = normalized_path
                else:
                    db.session.add(UserPath(user_id=current_user.uid, class_label=name, path=normalized_path))

        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            db.session.commit()
            flash("Ścieżki zostały zapisane.", "success")
            return redirect(url_for('user.account_settings'))

    # Pre-fill existing paths
    for entry in UserPath.query.filter_by(user_id=current_user.uid).all():
        if hasattr(form, entry.class_label):
            getattr(form, entry.class_label).data = entry.path

    return render_template('user/manage_paths.html', form=form)

@user.route('/open_path', methods=['POST'])
@login_required
def open_path():
    class_label = request.form.get("class_selector")
    token = request.form.get("token")

    if not class_label:
        flash("Nie wybrano klasy.", "warning")
        return redirect(url_for('user.download_ready', token=token))

    user_path = UserPath.query.filter_by(user_id=current_user.uid, class_label=class_label).first()
    if not user_path:
        flash("Nie znaleziono folderu dla wybranej klasy.", "danger")
        return redirect(url_for('user.download_ready', token=token))

    path = user_path.path

    try:
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{path}"')
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        flash(f"Otworzono folder: {path}", "success")
    except Exception as e:
        flash(f"Nie udało się otworzyć folderu: {e}", "danger")

    return redirect(url_for('user.download_ready', token=token))
