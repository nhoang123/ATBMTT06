"""
Script cài đặt dependencies cho hệ thống gửi file tài chính an toàn
"""

import subprocess
import sys
import os

def install_dependencies():
    """Cài đặt tất cả dependencies cần thiết"""
    
    print("🔧 Đang cài đặt dependencies...")
    
    try:
        # Cài đặt từ requirements.txt
        print("📦 Cài đặt từ requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            
        print("✅ Cài đặt dependencies thành công!")
        
        # Tạo thư mục cần thiết
        print("📁 Tạo thư mục...")
        directories = ['uploads', 'received_files', 'test_files', 'instance']
        for dir_name in directories:
            os.makedirs(dir_name, exist_ok=True)
            print(f"   ✓ {dir_name}/")
            
        print("🎉 Hệ thống đã sẵn sàng!")
        print("\n📋 Hướng dẫn chạy:")
        print("   1. python install_deps.py  (file này)")
        print("   2. python run.py")
        print("   3. Mở browser: http://localhost:5000")
        print("\n🔒 Chức năng chính:")
        print("   - Tạo file test báo cáo tài chính")
        print("   - Mã hóa file bằng AES-GCM + RSA")
        print("   - Truyền file an toàn qua WebSocket")
        print("   - Xác minh chữ ký số và toàn vẹn dữ liệu")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt: {e}")
        print("💡 Thử chạy: pip install --upgrade pip")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Không tìm thấy requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
