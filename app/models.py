from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

db = SQLAlchemy()

class FileHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)  # người gửi hoặc nhận
    role = db.Column(db.String(10), nullable=False)      # 'sender' hoặc 'receiver'
    filename = db.Column(db.String(255), nullable=False)
    peer = db.Column(db.String(80), nullable=False)      # người nhận hoặc gửi
    status = db.Column(db.String(20), nullable=False)    # success/error
    time = db.Column(db.String(50), nullable=False)
    error = db.Column(db.Text, nullable=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    public_key = db.Column(db.Text)
    private_key_hash = db.Column(db.String(128))  # Store hash of private key for verification

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_private_key(self, private_key):
        """Store private key hash and generate/store public key"""
        # Store hash of private key
        self.private_key_hash = generate_password_hash(private_key)
        
        # Generate public key from private key
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
            
            self.public_key = public_pem.decode()
            return True
        except Exception as e:
            print(f"Error processing private key: {str(e)}")
            return False

    def verify_private_key(self, private_key):
        """Verify if provided private key matches stored hash"""
        return check_password_hash(self.private_key_hash, private_key)

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    sid = db.Column(db.String(128), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    last_active = db.Column(db.DateTime, nullable=False)
    online = db.Column(db.Boolean, default=True)
