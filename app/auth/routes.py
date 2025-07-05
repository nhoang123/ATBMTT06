from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm, ChangeKeyForm
from . import bp

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        
        # Validate and store private key, generate public key
        if not user.set_private_key(form.private_key.data):
            flash('Invalid RSA private key format', 'error')
            return render_template('auth/register.html', title='Register', form=form)
        
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.', 'error')
            
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        user_type = session.get('user_type')
        if user_type == 'sender':
            return redirect(url_for('sender.sender_index'))
        elif user_type == 'receiver':
            return redirect(url_for('receiver.receiver_index'))
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Set user type in session based on next URL
        next_page = request.args.get('next')
        user_type = request.args.get('user_type')
        if user_type in ['sender', 'receiver']:
            session['user_type'] = user_type
        
        login_user(user)
        if not next_page or urlparse(next_page).netloc != '':
            if user_type == 'sender':
                next_page = url_for('sender.sender_index')
            elif user_type == 'receiver':
                next_page = url_for('receiver.receiver_index')
            else:
                next_page = url_for('main.index')
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    user_type = session.get('user_type')
    logout_user()
    session.pop('user_type', None)
    flash('Successfully logged out', 'success')
    return redirect(url_for('auth.login', user_type=user_type))

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Mật khẩu cũ không đúng!', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', title='Đổi mật khẩu', form=form)

@bp.route('/change_key', methods=['GET', 'POST'])
@login_required
def change_key():
    form = ChangeKeyForm()
    if form.validate_on_submit():
        if not current_user.set_private_key(form.private_key.data):
            flash('Private key không hợp lệ!', 'danger')
        else:
            db.session.commit()
            flash('Đổi khóa thành công!', 'success')
            return redirect(url_for('main.index'))
    return render_template('auth/change_key.html', title='Đổi khóa', form=form)
