"""
Script demo test các chức năng của hệ thống
"""

import asyncio
import json
from pathlib import Path
from app.services.websocket_client import SecureFileClient
from app.services.websocket_server import SecureFileServer

async def demo_secure_transfer():
    """Demo quy trình truyền file an toàn"""
    
    print("🎬 DEMO QUY TRÌNH TRUYỀN FILE AN TOÀN")
    print("="*50)
    
    # Kiểm tra file test
    test_file = Path("test_files/finance.txt")
    if not test_file.exists():
        print("❌ File test không tồn tại!")
        return
    
    print(f"📁 File test: {test_file}")
    print(f"📊 Kích thước: {test_file.stat().st_size} bytes")
    
    # Tạo client và test kết nối
    client = SecureFileClient()
    
    try:
        print("\n🔗 Đang kết nối tới WebSocket server...")
        if await client.connect():
            print("✅ Kết nối thành công!")
            
            print("\n🤝 Thực hiện handshake...")
            if await client.perform_handshake():
                print("✅ Handshake thành công!")
                
                print("\n🔑 Trao đổi khóa công khai...")
                if await client.exchange_keys():
                    print("✅ Trao đổi khóa thành công!")
                    
                    print("\n📦 Gửi file đã mã hóa...")
                    if await client.send_file(str(test_file)):
                        print("✅ Gửi file thành công!")
                        return True
                    else:
                        print("❌ Gửi file thất bại!")
                else:
                    print("❌ Trao đổi khóa thất bại!")
            else:
                print("❌ Handshake thất bại!")
        else:
            print("❌ Không thể kết nối server!")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        await client.disconnect()
        
    return False

async def demo_crypto_functions():
    """Demo các chức năng mã hóa"""
    
    print("\n🔐 DEMO CÁC CHỨC NĂNG MÃ HÓA")
    print("="*50)
    
    from app.services.crypto_service import CryptoService, SecureFileTransfer
    
    # Test CryptoService
    crypto = CryptoService()
    
    # Test tạo khóa
    print("🗝️ Tạo cặp khóa RSA 1024-bit...")
    private_key, public_key = crypto.generate_rsa_keypair()
    print(f"   ✓ Private key size: {private_key.size_in_bits()} bits")
    print(f"   ✓ Public key size: {public_key.size_in_bits()} bits")
    
    # Test AES key
    print("\n🔑 Tạo Session Key AES-256...")
    session_key = crypto.generate_aes_key()
    print(f"   ✓ Session key size: {len(session_key) * 8} bits")
    
    # Test nén dữ liệu
    print("\n📦 Test nén dữ liệu...")
    test_data = b"Day la du lieu tai chinh rat quan trong can bao mat!"
    compressed = crypto.compress_data(test_data)
    print(f"   ✓ Dữ liệu gốc: {len(test_data)} bytes")
    print(f"   ✓ Sau nén: {len(compressed)} bytes")
    print(f"   ✓ Tỷ lệ nén: {len(compressed)/len(test_data)*100:.1f}%")
    
    # Test mã hóa AES-GCM
    print("\n🔐 Test mã hóa AES-GCM...")
    nonce, ciphertext, tag = crypto.encrypt_aes_gcm(compressed, session_key)
    print(f"   ✓ Nonce: {len(nonce)} bytes")
    print(f"   ✓ Ciphertext: {len(ciphertext)} bytes") 
    print(f"   ✓ Tag: {len(tag)} bytes")
    
    # Test giải mã
    print("\n🔓 Test giải mã AES-GCM...")
    decrypted_compressed = crypto.decrypt_aes_gcm(nonce, ciphertext, tag, session_key)
    decrypted_data = crypto.decompress_data(decrypted_compressed)
    print(f"   ✓ Giải mã thành công: {decrypted_data == test_data}")
    
    # Test hash
    print("\n#️⃣ Test hash SHA-512...")
    file_hash = crypto.calculate_sha512_hash(nonce, ciphertext, tag)
    print(f"   ✓ Hash: {file_hash[:32]}...")
    
    # Test ký số
    print("\n✍️ Test ký số RSA/SHA-512...")
    metadata = '{"filename": "finance.txt", "timestamp": "2025-06-29"}'
    signature = crypto.sign_data(metadata.encode(), private_key)
    print(f"   ✓ Signature size: {len(signature)} bytes")
    
    # Test xác minh chữ ký
    print("\n✅ Test xác minh chữ ký...")
    is_valid = crypto.verify_signature(metadata.encode(), signature, public_key)
    print(f"   ✓ Chữ ký hợp lệ: {is_valid}")

def demo_file_structure():
    """Demo cấu trúc file hệ thống"""
    
    print("\n📁 CẤU TRÚC FILE HỆ THỐNG")
    print("="*50)
    
    directories = ["uploads", "received_files", "test_files"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            files = list(dir_path.iterdir())
            print(f"📂 {dir_name}/")
            if files:
                for file in files:
                    if file.is_file():
                        size = file.stat().st_size
                        print(f"   📄 {file.name} ({size} bytes)")
            else:
                print("   (trống)")
        else:
            print(f"❌ {dir_name}/ không tồn tại")

if __name__ == "__main__":
    print("🎯 DEMO HỆ THỐNG GỬI FILE TÀI CHÍNH AN TOÀN")
    print("=" * 60)
    
    # Demo cấu trúc file
    demo_file_structure()
    
    # Demo các chức năng mã hóa
    asyncio.run(demo_crypto_functions())
    
    # Demo truyền file an toàn
    print("\n⏳ Đang demo truyền file... (cần WebSocket server chạy)")
    success = asyncio.run(demo_secure_transfer())
    
    if success:
        print("\n🎉 DEMO HOÀN TẤT - TẤT CẢ CHỨC NĂNG HOẠT ĐỘNG TỐT!")
    else:
        print("\n⚠️  DEMO HOÀN TẤT - Một số chức năng cần kiểm tra")
        
    print("\n📋 Để test đầy đủ:")
    print("   1. Đảm bảo WebSocket server đang chạy")
    print("   2. Mở http://127.0.0.1:5000 trên browser")
    print("   3. Test từng chức năng trên giao diện web")
