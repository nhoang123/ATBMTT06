from flask import render_template, redirect, url_for, Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import User
from app.services.verify_signature import verify_metadata_signature
import json

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def home():
    # Sau khi đăng nhập, cho phép chọn vai trò
    return render_template('main/choose_role.html', title='Chọn vai trò')

@bp.route('/index')
@login_required
def index():
    return redirect(url_for('home'))

@bp.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    file = request.files.get('file')
    receiver_username = request.form.get('receiver_username')
    metadata_json = request.form.get('metadata')
    signature = request.form.get('signature')
    if not file or not receiver_username or not metadata_json or not signature:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin file, metadata hoặc chữ ký!'}), 400
    try:
        metadata = json.loads(metadata_json)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Metadata không hợp lệ!'}), 400
    # Lấy public key người gửi từ DB
    sender = User.query.filter_by(username=current_user.username).first()
    if not sender or not sender.public_key:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy public key người gửi!'}), 400
    # Xác thực chữ ký
    if not verify_metadata_signature(sender.public_key, metadata, signature):
        return jsonify({'status': 'error', 'message': 'Chữ ký metadata không hợp lệ!'}), 400
    # TODO: Lưu file, metadata, ...
    # file.save(...)
    return jsonify({'status': 'success', 'message': 'Tải file và xác thực metadata thành công!'})

@bp.route('/api/send_session_key', methods=['POST'])
@login_required
def send_session_key():
    data = request.get_json()
    receiver_username = data.get('receiver_username')
    encrypted_session_key = data.get('encrypted_session_key')
    if not receiver_username or not encrypted_session_key:
        return jsonify({'status': 'error', 'message': 'Thiếu thông tin session key!'}), 400
    # TODO: Lưu session key đã mã hóa vào DB hoặc gửi cho người nhận (tùy luồng ứng dụng)
    # Ví dụ: lưu tạm vào file hoặc DB, hoặc gửi qua WebSocket
    # Ở đây chỉ demo xác nhận đã nhận
    return jsonify({'status': 'success', 'message': 'Đã nhận session key mã hóa!'})
