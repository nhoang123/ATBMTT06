from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash
import os
import asyncio
import threading
from pathlib import Path
from flask_login import login_required, current_user
from app.services.websocket_server import start_secure_server
from app.services.websocket_client import SecureFileClient
from app.models import db, User, FileHistory, UserSession
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from datetime import datetime

main = Blueprint('main', __name__)

# Biến global để theo dõi server
websocket_server_running = False

@main.route('/')
@login_required
def home():
    # Sau khi đăng nhập, cho phép chọn vai trò
    return render_template('main/choose_role.html', title='Chọn vai trò')

@main.route('/index')
@login_required
def index():
    return redirect(url_for('main.home'))

@main.route('/register_key', methods=['GET', 'POST'])
@login_required
def register_key():
    if request.method == 'POST':
        private_key = request.form.get('private_key')
        if not private_key:
            flash('Vui lòng nhập khóa riêng (private key)', 'danger')
            return render_template('register_key.html')
        try:
            private_key_obj = serialization.load_pem_private_key(
                private_key.encode(),
                password=None,
                backend=default_backend()
            )
            public_key = private_key_obj.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            # Lưu public key vào user
            user = User.query.get(current_user.id)
            user.public_key = public_pem.decode()
            db.session.commit()
            flash('Đăng ký khóa thành công!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash('Khóa riêng không hợp lệ hoặc lỗi xử lý!', 'danger')
            return render_template('register_key.html')
    return render_template('register_key.html')

@main.route('/start_server', methods=['POST'])
def start_server():
    """Khởi chạy WebSocket server"""
    global websocket_server_running
    
    try:
        if not websocket_server_running:
            # Chạy server trong thread riêng
            def run_server():
                global websocket_server_running
                websocket_server_running = True
                asyncio.run(start_secure_server())
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            return jsonify({
                'status': 'success',
                'message': 'WebSocket server đã được khởi chạy tại ws://localhost:8765'
            })
        else:
            return jsonify({
                'status': 'info',
                'message': 'Server đã đang chạy'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khởi chạy server: {str(e)}'
        })

@main.route('/upload_file', methods=['POST'])
def upload_file():
    """Upload file tài chính lên server"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Không có file được chọn'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Tên file không hợp lệ'
            })
        
        # Tạo thư mục upload nếu chưa có
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        # Lưu file upload
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        return jsonify({
            'status': 'success',
            'message': f'File {file.filename} đã được upload thành công',
            'file_path': str(file_path)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi upload file: {str(e)}'
        })

@main.route('/send_file', methods=['POST'])
def send_file_secure():
    """Gửi file qua WebSocket một cách an toàn"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'status': 'error',
                'message': 'Thiếu đường dẫn file'
            })
        
        if not Path(file_path).exists():
            return jsonify({
                'status': 'error',
                'message': 'File không tồn tại'
            })
        
        # Gửi file qua WebSocket client
        async def send_file_async():
            client = SecureFileClient()
            return await client.send_file_secure(file_path)
        
        # Chạy async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(send_file_async())
        loop.close()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'File đã được gửi an toàn thành công'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Gửi file thất bại'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi gửi file: {str(e)}'
        })

@main.route('/list_received_files')
def list_received_files():
    """Liệt kê các file đã nhận"""
    try:
        received_dir = Path('received_files')
        if not received_dir.exists():
            return jsonify({
                'status': 'success',
                'files': []
            })
        
        files = []
        for file_path in received_dir.iterdir():
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'path': str(file_path)
                })
        
        return jsonify({
            'status': 'success',
            'files': files
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi liệt kê file: {str(e)}'
        })

@main.route('/download_file/<path:filename>')
def download_file(filename):
    """Download file đã nhận"""
    try:
        file_path = Path('received_files') / filename
        if file_path.exists():
            return send_file(str(file_path), as_attachment=True)
        else:
            return jsonify({
                'status': 'error',
                'message': 'File không tồn tại'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi download file: {str(e)}'
        })

@main.route('/create_test_file')
def create_test_file():
    """Tạo file tài chính mẫu để test"""
    try:
        # Tạo thư mục test nếu chưa có
        test_dir = Path('test_files')
        test_dir.mkdir(exist_ok=True)
        
        # Nội dung file tài chính mẫu
        sample_content = """BÁOTÀI CHÍNH NGÂN HÀNG ABC
====================================
Ngày báo cáo: 2025-06-29
Mã ngân hàng: ABC123
Số tài khoản: 1234567890

SỐ DƯ TÀI KHOẢN
- Số dư đầu kỳ: 1,000,000,000 VNĐ
- Số dư cuối kỳ: 1,250,000,000 VNĐ
- Tăng/giảm: +250,000,000 VNĐ

GIAO DỊCH TRONG THÁNG
=====================
1. Thu nhập:
   - Lương: 50,000,000 VNĐ
   - Thưởng: 30,000,000 VNĐ
   - Đầu tư: 420,000,000 VNĐ
   - Tổng thu: 500,000,000 VNĐ

2. Chi tiêu:
   - Sinh hoạt: 150,000,000 VNĐ
   - Đầu tư: 100,000,000 VNĐ
   - Khác: 50,000,000 VNĐ
   - Tổng chi: 300,000,000 VNĐ

LÃI SUẤT & PHỤ PHI
==================
- Lãi suất tiết kiệm: 2.5%/năm
- Phí quản lý tài khoản: 50,000 VNĐ/tháng
- Phí chuyển khoản: 5,000 VNĐ/giao dịch

THÔNG TIN BẢO MẬT
=================
- Dữ liệu này chứa thông tin tài chính nhạy cảm
- Không được sao chép hoặc chia sẻ
- Mã hóa bắt buộc khi truyền tải
- Chỉ người được ủy quyền mới được truy cập

Chữ ký số: [Sẽ được tạo tự động]
Mã hash: [Sẽ được tạo tự động]
"""
        
        # Lưu file
        test_file = test_dir / 'finance.txt'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        return jsonify({
            'status': 'success',
            'message': f'File test đã được tạo: {test_file}',
            'file_path': str(test_file),
            'size': len(sample_content.encode('utf-8'))
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi tạo file test: {str(e)}'
        })

@main.route('/api/file_history', methods=['POST', 'GET'])
@login_required
def file_history():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        role = data.get('role')
        filename = data.get('filename')
        peer = data.get('peer')
        status = data.get('status')
        time = data.get('time')
        error = data.get('error', None)
        if not all([username, role, filename, peer, status, time]):
            return jsonify({'status': 'error', 'message': 'Thiếu thông tin lịch sử file!'}), 400
        entry = FileHistory(
            username=username,
            role=role,
            filename=filename,
            peer=peer,
            status=status,
            time=time,
            error=error
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Đã lưu lịch sử file!'})
    else:
        # GET: lấy lịch sử gửi/nhận file của user hiện tại
        role = request.args.get('role')  # 'sender' hoặc 'receiver'
        q = FileHistory.query.filter_by(username=current_user.username)
        if role:
            q = q.filter_by(role=role)
        q = q.order_by(FileHistory.id.desc()).limit(50)
        result = [
            {
                'filename': h.filename,
                'peer': h.peer,
                'status': h.status,
                'time': h.time,
                'error': h.error
            } for h in q
        ]
        return jsonify({'status': 'success', 'history': result})

@main.route('/api/session_status')
def session_status():
    username = request.args.get('username')
    # Cleanup session timeout trước khi trả kết quả
    from app.ws import cleanup_sessions
    cleanup_sessions(timeout_minutes=60)
    q = UserSession.query
    if username:
        q = q.filter_by(username=username)
    q = q.order_by(UserSession.last_active.desc())
    result = [
        {
            'username': s.username,
            'sid': s.sid,
            'login_time': s.login_time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_active': s.last_active.strftime('%Y-%m-%d %H:%M:%S'),
            'online': s.online
        } for s in q
    ]
    return jsonify({'status': 'success', 'sessions': result})
