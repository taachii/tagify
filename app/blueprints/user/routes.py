from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from werkzeug.utils import secure_filename
import os

from . import user
from .forms import ZipUploadForm

@user.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ZipUploadForm()
    if form.validate_on_submit():
        zip_data = form.zip_file.data
        filename = secure_filename(zip_data.filename)
        upload_path = os.path.join('instance/uploads', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        zip_data.save(upload_path)
        flash('Plik został przesłany poprawnie!', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/dashboard.html', form=form)