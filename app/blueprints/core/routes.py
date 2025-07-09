from flask import render_template, redirect, url_for
from flask_login import current_user
from . import core
import os

@core.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_researcher():
            return redirect(url_for('user.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return render_template('core/home.html')

@core.route('/pro')
def pro_info():
    return render_template('core/pro.html')