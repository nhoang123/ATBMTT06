"""
Dịch vụ mã hóa cho hệ thống gửi báo cáo tài chính
Bao gồm: AES-GCM, RSA, SHA-512, nén zlib
"""

import os
import zlib
import json
import base64
import hashlib
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import SHA512
from Crypto.Signature import pkcs1_15


class CryptoService:
    """Dịch vụ mã hóa và bảo mật cho gửi file tài chính"""
    
    def __init__(self):
        """Khởi tạo dịch vụ mã hóa"""
        self.rsa_key_size = 1024  # Kích thước khóa RSA 1024-bit
        self.aes_key_size = 32    # AES-256 (32 bytes)
        self.nonce_size = 16      # Nonce 16 bytes cho AES-GCM
        
    def generate_rsa_keypair(self):
        """
        Tạo cặp khóa RSA 1024-bit (public/private)
        Returns:
            tuple: (private_key, public_key) objects
        """
        key = RSA.generate(self.rsa_key_size)
        private_key = key
        public_key = key.publickey()
        return private_key, public_key
    
    def generate_aes_key(self):
        """
        Tạo khóa AES ngẫu nhiên 256-bit
        Returns:
            bytes: Session key cho AES
        """
        return os.urandom(self.aes_key_size)
    
    def compress_data(self, data):
        """
        Nén dữ liệu sử dụng zlib
        Args:
            data (bytes): Dữ liệu cần nén
        Returns:
            bytes: Dữ liệu đã nén
        """
        return zlib.compress(data)
    
    def decompress_data(self, compressed_data):
        """
        Giải nén dữ liệu từ zlib
        Args:
            compressed_data (bytes): Dữ liệu đã nén
        Returns:
            bytes: Dữ liệu gốc
        """
        return zlib.decompress(compressed_data)
    
    def encrypt_aes_gcm(self, data, session_key):
        """
        Mã hóa dữ liệu bằng AES-GCM
        Args:
            data (bytes): Dữ liệu cần mã hóa
            session_key (bytes): Khóa phiên AES
        Returns:
            tuple: (nonce, ciphertext, tag)
        """
        # Tạo nonce ngẫu nhiên
        nonce = os.urandom(self.nonce_size)
        
        # Khởi tạo cipher AES-GCM
        cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
        
        # Mã hóa và lấy tag xác thực
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        return nonce, ciphertext, tag
    
    def decrypt_aes_gcm(self, nonce, ciphertext, tag, session_key):
        """
        Giải mã dữ liệu AES-GCM và kiểm tra tính toàn vẹn
        Args:
            nonce (bytes): Nonce đã sử dụng
            ciphertext (bytes): Dữ liệu mã hóa
            tag (bytes): Tag xác thực
            session_key (bytes): Khóa phiên AES
        Returns:
            bytes: Dữ liệu gốc đã giải mã
        Raises:
            ValueError: Nếu tag không hợp lệ
        """
        # Khởi tạo cipher với nonce
        cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
        
        # Giải mã và xác minh tag
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext
    
    def rsa_encrypt(self, data, public_key):
        """
        Mã hóa dữ liệu bằng RSA PKCS#1 v1.5
        Args:
            data (bytes): Dữ liệu cần mã hóa
            public_key: Khóa công khai RSA
        Returns:
            bytes: Dữ liệu đã mã hóa
        """
        cipher = PKCS1_v1_5.new(public_key)
        return cipher.encrypt(data)
    
    def rsa_decrypt(self, encrypted_data, private_key):
        """
        Giải mã dữ liệu RSA PKCS#1 v1.5
        Args:
            encrypted_data (bytes): Dữ liệu đã mã hóa
            private_key: Khóa bí mật RSA
        Returns:
            bytes: Dữ liệu gốc
        """
        cipher = PKCS1_v1_5.new(private_key)
        # Sử dụng sentinel để xử lý lỗi giải mã
        sentinel = os.urandom(32)
        return cipher.decrypt(encrypted_data, sentinel)
    
    def sign_data(self, data, private_key):
        """
        Ký số dữ liệu bằng RSA/SHA-512
        Args:
            data (bytes): Dữ liệu cần ký
            private_key: Khóa bí mật RSA
        Returns:
            bytes: Chữ ký số
        """
        # Tạo hash SHA-512
        h = SHA512.new(data)
        
        # Ký bằng RSA
        signature = pkcs1_15.new(private_key).sign(h)
        return signature
    
    def verify_signature(self, data, signature, public_key):
        """
        Xác minh chữ ký số RSA/SHA-512
        Args:
            data (bytes): Dữ liệu gốc
            signature (bytes): Chữ ký cần xác minh
            public_key: Khóa công khai RSA
        Returns:
            bool: True nếu chữ ký hợp lệ
        """
        try:
            # Tạo hash SHA-512
            h = SHA512.new(data)
            
            # Xác minh chữ ký
            pkcs1_15.new(public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False
    
    def calculate_sha512_hash(self, *data_parts):
        """
        Tính hash SHA-512 của nhiều phần dữ liệu
        Args:
            *data_parts: Các phần dữ liệu cần hash
        Returns:
            str: Hash hex string
        """
        hasher = hashlib.sha512()
        for part in data_parts:
            if isinstance(part, str):
                part = part.encode('utf-8')
            hasher.update(part)
        return hasher.hexdigest()
    
    def create_metadata(self, filename, file_type="text/plain"):
        """
        Tạo metadata cho file (tên + timestamp + loại)
        Args:
            filename (str): Tên file
            file_type (str): Loại file
        Returns:
            str: Metadata JSON string
        """
        metadata = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "file_type": file_type
        }
        return json.dumps(metadata, separators=(',', ':'))
    
    def encode_base64(self, data):
        """
        Mã hóa dữ liệu thành Base64
        Args:
            data (bytes): Dữ liệu cần mã hóa
        Returns:
            str: Chuỗi Base64
        """
        return base64.b64encode(data).decode('utf-8')
    
    def decode_base64(self, data_str):
        """
        Giải mã dữ liệu từ Base64
        Args:
            data_str (str): Chuỗi Base64
        Returns:
            bytes: Dữ liệu gốc
        """
        return base64.b64decode(data_str.encode('utf-8'))


class SecureFileTransfer:
    """Lớp xử lý truyền file an toàn theo đề tài 4"""
    
    def __init__(self):
        """Khởi tạo dịch vụ truyền file an toàn"""
        self.crypto = CryptoService()
        self.sender_private_key = None
        self.sender_public_key = None
        self.receiver_private_key = None
        self.receiver_public_key = None
        self.session_key = None
        
    def initialize_sender(self):
        """
        Khởi tạo người gửi với cặp khóa RSA
        Returns:
            str: Public key PEM để chia sẻ với người nhận
        """
        self.sender_private_key, self.sender_public_key = self.crypto.generate_rsa_keypair()
        return self.sender_public_key.export_key().decode('utf-8')
    
    def initialize_receiver(self):
        """
        Khởi tạo người nhận với cặp khóa RSA
        Returns:
            str: Public key PEM để chia sẻ với người gửi
        """
        self.receiver_private_key, self.receiver_public_key = self.crypto.generate_rsa_keypair()
        return self.receiver_public_key.export_key().decode('utf-8')
    
    def set_receiver_keys(self, receiver_private_key, receiver_public_key):
        """
        Thiết lập khóa của người nhận (cho việc giải mã)
        Args:
            receiver_private_key: Private key của receiver
            receiver_public_key: Public key của receiver
        """
        self.receiver_private_key = receiver_private_key
        self.receiver_public_key = receiver_public_key
    
    def set_receiver_public_key(self, public_key_pem):
        """
        Thiết lập khóa công khai của người nhận
        Args:
            public_key_pem (str): Khóa công khai dạng PEM
        """
        self.receiver_public_key = RSA.import_key(public_key_pem.encode('utf-8'))
    
    def prepare_file_package(self, file_path):
        """
        Chuẩn bị gói tin file theo luồng xử lý đề tài 4
        Args:
            file_path (str): Đường dẫn file cần gửi
        Returns:
            tuple: (metadata_signature, encrypted_session_key, file_package)
        """
        # Đọc nội dung file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Tạo metadata và ký
        filename = os.path.basename(file_path)
        metadata = self.crypto.create_metadata(filename)
        metadata_signature = self.crypto.sign_data(
            metadata.encode('utf-8'), 
            self.sender_private_key
        )
        
        # Tạo session key và mã hóa bằng RSA
        self.session_key = self.crypto.generate_aes_key()
        encrypted_session_key = self.crypto.rsa_encrypt(
            self.session_key, 
            self.receiver_public_key
        )
        
        # Nén file
        compressed_data = self.crypto.compress_data(file_content)
        
        # Mã hóa file nén bằng AES-GCM
        nonce, ciphertext, tag = self.crypto.encrypt_aes_gcm(
            compressed_data, 
            self.session_key
        )
        
        # Tính hash SHA-512(nonce || ciphertext || tag)
        file_hash = self.crypto.calculate_sha512_hash(nonce, ciphertext, tag)
        
        # Tạo gói tin file
        file_package = {
            "nonce": self.crypto.encode_base64(nonce),
            "cipher": self.crypto.encode_base64(ciphertext),
            "tag": self.crypto.encode_base64(tag),
            "hash": file_hash,
            "sig": self.crypto.encode_base64(metadata_signature)
        }
        
        return (
            self.crypto.encode_base64(metadata_signature),
            self.crypto.encode_base64(encrypted_session_key),
            file_package
        )
    
    def verify_and_decrypt_package(self, metadata, metadata_signature, encrypted_session_key, file_package, sender_public_key_pem):
        """
        Xác minh và giải mã gói tin file (phía người nhận)
        Args:
            metadata (str): Metadata JSON
            metadata_signature (str): Chữ ký metadata (Base64)
            encrypted_session_key (str): Session key đã mã hóa (Base64)
            file_package (dict): Gói tin file
            sender_public_key_pem (str): Khóa công khai người gửi
        Returns:
            tuple: (success, result) - success: bool, result: bytes hoặc error message
        """
        try:
            # Import khóa công khai người gửi
            sender_public_key = RSA.import_key(sender_public_key_pem.encode('utf-8'))
            
            # Xác minh chữ ký metadata
            metadata_sig_bytes = self.crypto.decode_base64(metadata_signature)
            if not self.crypto.verify_signature(
                metadata.encode('utf-8'), 
                metadata_sig_bytes, 
                sender_public_key
            ):
                return False, "Chữ ký metadata không hợp lệ"
            
            # Giải mã session key (sử dụng private key của receiver)
            encrypted_key_bytes = self.crypto.decode_base64(encrypted_session_key)
            session_key = self.crypto.rsa_decrypt(encrypted_key_bytes, self.receiver_private_key)
            
            # Giải mã các thành phần từ Base64
            nonce = self.crypto.decode_base64(file_package["nonce"])
            ciphertext = self.crypto.decode_base64(file_package["cipher"])
            tag = self.crypto.decode_base64(file_package["tag"])
            received_hash = file_package["hash"]
            
            # Kiểm tra hash toàn vẹn
            calculated_hash = self.crypto.calculate_sha512_hash(nonce, ciphertext, tag)
            if received_hash != calculated_hash:
                return False, "Hash toàn vẹn không khớp"
            
            # Giải mã AES-GCM
            try:
                decrypted_compressed = self.crypto.decrypt_aes_gcm(
                    nonce, ciphertext, tag, session_key
                )
            except ValueError:
                return False, "Tag AES-GCM không hợp lệ"
            
            # Giải nén dữ liệu
            original_data = self.crypto.decompress_data(decrypted_compressed)
            
            return True, original_data
            
        except Exception as e:
            return False, f"Lỗi xử lý: {str(e)}"
