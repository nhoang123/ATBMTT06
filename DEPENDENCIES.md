# 📦 DEPENDENCIES VÀ THƯ VIỆN

## 🎯 Tổng quan

Dự án sử dụng các thư viện Python sau để xây dựng hệ thống gửi báo cáo tài chính an toàn:

## 🔧 Core Dependencies

### 1. **Flask Framework**

```
Flask==2.3.3              # Web framework chính
python-dotenv==1.0.0       # Quản lý biến môi trường
Werkzeug==2.3.7           # WSGI utilities
```

### 2. **Database & Authentication**

```
Flask-SQLAlchemy==3.0.5    # ORM cho database
Flask-Login==0.6.3         # Quản lý session đăng nhập
```

### 3. **Forms & Validation**

```
Flask-WTF==1.1.1          # Form handling với CSRF protection
WTForms==3.0.1            # Form validation và rendering
```

### 4. **WebSocket & Real-time**

```
Flask-SocketIO==5.3.6     # Socket.IO support cho Flask
websockets==11.0.3        # WebSocket client/server
python-socketio==5.8.0    # Socket.IO server implementation
```

### 5. **Cryptography Libraries**

```
pycryptodome==3.18.0      # AES-GCM, RSA, SHA-512 (Crypto.*)
cryptography==41.0.7      # RSA, serialization (cryptography.*)
```

## 🔐 Chức năng Cryptography

### PyCryptodome (3.18.0)

- **AES-GCM**: Mã hóa symmetric với authentication
- **RSA**: Mã hóa asymmetric và chữ ký số
- **SHA-512**: Hash functions
- **PKCS#1 v1.5**: RSA padding scheme

### Cryptography (41.0.7)

- **RSA key generation**: Tạo cặp khóa RSA
- **Key serialization**: Import/Export khóa PEM
- **Backend support**: Default cryptographic backend

## 🌐 WebSocket Features

### websockets (11.0.3)

- **Async WebSocket**: Client/Server non-blocking
- **SSL/TLS support**: Secure WebSocket connections
- **Message framing**: Binary và text messages

### Flask-SocketIO (5.3.6)

- **Real-time communication**: Bidirectional events
- **Room support**: Nhóm clients
- **Session management**: User sessions

## 📝 Form & Security

### Flask-WTF (1.1.1)

- **CSRF Protection**: Chống tấn công Cross-Site Request Forgery
- **File uploads**: Xử lý upload files
- **Form validation**: Validation tích hợp

### WTForms (3.0.1)

- **Field types**: StringField, PasswordField, TextAreaField
- **Validators**: DataRequired, Length, ValidationError
- **Custom validation**: Custom validator methods

## 💾 Database Features

### Flask-SQLAlchemy (3.0.5)

- **ORM**: Object-Relational Mapping
- **Migration support**: Database schema changes
- **Query interface**: Fluent query API

## 🔍 Import Usage trong Code

### Cryptography Imports

```python
# PyCryptodome
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import SHA512
from Crypto.Signature import pkcs1_15

# Cryptography library
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
```

### Flask Imports

```python
from flask import Flask, Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from flask_login import LoginManager, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
```

### WebSocket Imports

```python
import websockets
import asyncio
from flask_socketio import SocketIO
```

## 🚀 Cài đặt

### Automatic Installation

```bash
python install_deps.py
```

### Manual Installation

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import flask, cryptography, websockets; print('All dependencies OK!')"
```

## ⚡ Performance Notes

1. **pycryptodome vs cryptography**:

   - pycryptodome: Nhanh hơn cho AES-GCM
   - cryptography: Tốt hơn cho RSA operations

2. **websockets vs Flask-SocketIO**:

   - websockets: Raw WebSocket, performance cao
   - Flask-SocketIO: Tích hợp Flask, dễ sử dụng

3. **Memory Usage**:
   - AES-GCM: Low memory footprint
   - RSA: Higher memory cho key operations
   - File streaming: Chunked processing

## 🔧 Troubleshooting

### Common Issues

1. **Import Error**: Đảm bảo virtual environment active
2. **Cryptography build**: Cần Visual C++ trên Windows
3. **WebSocket ports**: Kiểm tra firewall settings

### Debug Commands

```bash
pip list | grep -E "(flask|crypto|websocket)"
python -c "from app.services.crypto_service import CryptoService; print('Crypto OK')"
```
