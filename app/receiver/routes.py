from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.receiver import receiver_bp
from app.models import User
from app.services.verify_signature import verify_metadata_signature
import json

@receiver_bp.route('/receiver')
@login_required
def receiver_index():
    user_info = {
        'username': current_user.username,
        'public_key': current_user.public_key,
    }
    return render_template('receiver/index.html', title='Nhận File (Receiver)', current_username=current_user.username, user_info=user_info)

@receiver_bp.route('/api/verify_metadata', methods=['POST'])
@login_required
def verify_metadata():
    data = request.get_json()
    sender_username = data.get('sender_username')
    metadata = data.get('metadata')
    signature = data.get('signature')
    if not sender_username or not metadata or not signature:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin xác thực!'}), 400
    sender = User.query.filter_by(username=sender_username).first()
    if not sender or not sender.public_key:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy public key người gửi!'}), 400
    try:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Metadata không hợp lệ!'}), 400
    if not verify_metadata_signature(sender.public_key, metadata, signature):
        return jsonify({'status': 'error', 'message': 'Chữ ký metadata không hợp lệ!'}), 400
    return jsonify({'status': 'success', 'message': 'Xác thực metadata thành công!'})
