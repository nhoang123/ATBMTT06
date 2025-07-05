from flask_socketio import SocketIO, emit, join_room
from flask import request
import logging
from . import socketio
from app.models import db, UserSession
from datetime import datetime, timedelta

# Lưu mapping username <-> sid
user_sid_map = {}

@socketio.on('register_username')
def register_username(data):
    username = data.get('username')
    if username:
        user_sid_map[username] = request.sid
        logging.info(f'[SOCKET] Đăng ký user_sid_map: {user_sid_map}')
        # Lưu session vào DB
        now = datetime.utcnow()
        # Xóa session cũ của user nếu có
        UserSession.query.filter_by(username=username).delete()
        session = UserSession(username=username, sid=request.sid, login_time=now, last_active=now, online=True)
        db.session.add(session)
        db.session.commit()

@socketio.on('disconnect')
def on_disconnect():
    # Xóa user khỏi map khi disconnect
    for user, sid in list(user_sid_map.items()):
        if sid == request.sid:
            del user_sid_map[user]
            logging.info(f'[SOCKET] user_sid_map sau disconnect: {user_sid_map}')
            # Đánh dấu offline trong DB
            sess = UserSession.query.filter_by(username=user, sid=sid, online=True).first()
            if sess:
                sess.online = False
                sess.last_active = datetime.utcnow()
                db.session.commit()

# Tự động xóa session khi timeout (có thể chạy định kỳ bằng scheduler hoặc khi truy vấn API)
def cleanup_sessions(timeout_minutes=60):
    now = datetime.utcnow()
    timeout = now - timedelta(minutes=timeout_minutes)
    sessions = UserSession.query.filter(UserSession.online==True, UserSession.last_active < timeout).all()
    for sess in sessions:
        sess.online = False
        db.session.commit()

@socketio.on('handshake_hello')
def handle_handshake_hello(data):
    # data: {sender, receiver, message}
    sender = data.get('sender')
    receiver = data.get('receiver')
    message = data.get('message')
    logging.info(f'[SOCKET] Nhận handshake_hello: {data}')
    # Gửi tới receiver nếu đang online
    if receiver in user_sid_map:
        logging.info(f'[SOCKET] Emit handshake_hello tới {receiver} (sid={user_sid_map[receiver]})')
        emit('handshake_hello', {
            'message': f"Hello: {receiver} Tôi là: {sender}",
            'sender': sender,
            'receiver': receiver
        }, room=user_sid_map[receiver])
    else:
        logging.warning(f'[SOCKET] Không tìm thấy receiver {receiver} trong user_sid_map khi handshake_hello')

@socketio.on('handshake_ready')
def handle_handshake_ready(data):
    # data: {sender, receiver, message}
    sender = data.get('sender')  # người nhận
    receiver = data.get('receiver')  # người gửi
    message = data.get('message')
    logging.info(f'[SOCKET] Nhận handshake_ready: {data}')
    # Gửi lại cho người gửi
    if receiver in user_sid_map:
        logging.info(f'[SOCKET] Emit handshake_ready tới {receiver} (sid={user_sid_map[receiver]})')
        emit('handshake_ready', {
            'message': f"Hi: {receiver} tôi đã sẵn sàng!",
            'sender': sender,
            'receiver': receiver
        }, room=user_sid_map[receiver])
    else:
        logging.warning(f'[SOCKET] Không tìm thấy receiver {receiver} trong user_sid_map khi handshake_ready')

@socketio.on('send_session_key')
def ws_send_session_key(data):
    # data: {sender, receiver, encrypted_session_key}
    receiver = data.get('receiver')
    if receiver in user_sid_map:
        emit('receive_session_key', {
            'sender': data.get('sender'),
            'encrypted_session_key': data.get('encrypted_session_key')
        }, room=user_sid_map[receiver])

@socketio.on('send_file_data')
def ws_send_file_data(data):
    # data: {sender, receiver, filename, encrypted_file, encrypted_session_key, sender_private_key}
    receiver = data.get('receiver')
    if receiver in user_sid_map:
        emit('receive_file_data', {
            'sender': data.get('sender'),
            'filename': data.get('filename'),
            'encrypted_file': data.get('encrypted_file'),
            'encrypted_session_key': data.get('encrypted_session_key'),
            'sender_private_key': data.get('sender_private_key')
        }, room=user_sid_map[receiver])

@socketio.on('file_ack')
def handle_file_ack(data):
    # data: {sender, receiver, status, message}
    sender = data.get('receiver')  # người gửi file (sender)
    receiver = data.get('sender')  # người nhận file (receiver)
    status = data.get('status')
    message = data.get('message')
    if sender in user_sid_map:
        emit('file_status_notify', {
            'from': receiver,
            'to': sender,
            'status': status,
            'message': message
        }, room=user_sid_map[sender])
