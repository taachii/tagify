from flask import render_template
from flask_login import login_required
from . import core

@core.route('/')
def home():
    return render_template('home.html')

@core.route('/pro')
def pro_info():
    return render_template('pro.html')

