from flask_socketio import SocketIO, emit, join_room
from flask import request
from . import socketio

# Lưu mapping username <-> sid
user_sid_map = {}

@socketio.on('register_username')
def register_username(data):
    username = data.get('username')
    if username:
        user_sid_map[username] = request.sid

@socketio.on('disconnect')
def on_disconnect():
    # Xóa user khỏi map khi disconnect
    for user, sid in list(user_sid_map.items()):
        if sid == request.sid:
            del user_sid_map[user]

@socketio.on('handshake_hello')
def handle_handshake_hello(data):
    # data: {sender, receiver, message}
    sender = data.get('sender')
    receiver = data.get('receiver')
    message = data.get('message')
    # Gửi tới receiver nếu đang online
    if receiver in user_sid_map:
        emit('handshake_hello', {
            'message': f"Hello: {receiver} Tôi là: {sender}",
            'sender': sender,
            'receiver': receiver
        }, room=user_sid_map[receiver])

@socketio.on('handshake_ready')
def handle_handshake_ready(data):
    # data: {sender, receiver, message}
    sender = data.get('sender')  # người nhận
    receiver = data.get('receiver')  # người gửi
    message = data.get('message')
    # Gửi lại cho người gửi
    if receiver in user_sid_map:
        emit('handshake_ready', {
            'message': f"Hi: {receiver} tôi đã sẵn sàng!",
            'sender': sender,
            'receiver': receiver
        }, room=user_sid_map[receiver])

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
