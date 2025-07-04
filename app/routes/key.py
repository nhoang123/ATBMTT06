from flask import Blueprint, jsonify, request
from app.models import User, db
from flask_login import login_required, current_user

key_bp = Blueprint('key', __name__)

@key_bp.route('/api/public_key/<username>', methods=['GET'])
def get_public_key(username):
    """API lấy public key của user khác theo username"""
    user = User.query.filter_by(username=username).first()
    if user and user.public_key:
        return jsonify({
            'status': 'success',
            'username': username,
            'public_key': user.public_key
        })
    return jsonify({'status': 'error', 'message': 'User không tồn tại hoặc chưa có public key'}), 404

@key_bp.route('/api/public_key/update', methods=['POST'])
@login_required
def update_public_key():
    """API cập nhật public key cho user hiện tại (cần xác thực)"""
    data = request.get_json()
    new_public_key = data.get('public_key')
    if not new_public_key:
        return jsonify({'status': 'error', 'message': 'Thiếu public_key'}), 400
    current_user.public_key = new_public_key
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Cập nhật public key thành công'})
