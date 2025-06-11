from flask import render_template
from flask_login import login_required
from . import core
from .forms import ZipUploadForm
import os
from werkzeug.utils import secure_filename

@core.route('/')
def home():
    return render_template('home.html')

@core.route('/pro')
def pro_info():
    return render_template('pro.html')

@core.route('/dashboard', methods=['GET', 'POST'])
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
        return redirect(url_for('core.dashboard'))

    return render_template('dashboard.html', form=form)

