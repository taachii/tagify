from flask import render_template
from flask_login import login_required
from . import core
import os
from werkzeug.utils import secure_filename

@core.route('/')
def home():
    return render_template('core/home.html')

@core.route('/pro')
def pro_info():
    return render_template('core/pro.html')