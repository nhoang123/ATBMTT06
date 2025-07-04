from flask import render_template
from flask_login import login_required, current_user
from app.sender import sender_bp

@sender_bp.route('/sender')
@login_required
def sender_index():
    # Lấy thông tin chi tiết tài khoản
    user_info = {
        'username': current_user.username,
        'public_key': current_user.public_key,
        # Không trả về private_key_hash vì lý do bảo mật
    }
    return render_template('sender/index.html', title='Gửi File (Sender)', current_username=current_user.username, user_info=user_info)
