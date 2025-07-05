from flask import render_template, session, redirect, url_for, request
from flask_login import login_required, current_user
from app.sender import sender_bp
from functools import wraps

def sender_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or session.get('user_type') != 'sender':
            return redirect(url_for('auth.login', next=request.url, user_type='sender'))
        return f(*args, **kwargs)
    return decorated_function

@sender_bp.before_request
def before_request():
    session['user_type'] = 'sender'

@sender_bp.route('/sender')
@sender_login_required
def sender_index():
    # Lấy thông tin chi tiết tài khoản
    user_info = {
        'username': current_user.username,
        'public_key': current_user.public_key,
        # Không trả về private_key_hash vì lý do bảo mật
    }
    return render_template('sender/index.html', title='Gửi File (Sender)', current_username=current_user.username, user_info=user_info)
