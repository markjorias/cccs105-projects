from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import Admin, Receptionist
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import hashlib

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect to home/dashboard if already logged in
    if 'user_id' in session:
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if user_type == 'admin':
            user = Admin.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.admin_id
                session['user_type'] = 'admin'
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        elif user_type == 'receptionist':
            user = Receptionist.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.receptionist_id
                session['user_type'] = 'receptionist'
                return redirect(url_for('main.index'))
            else:
                flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))