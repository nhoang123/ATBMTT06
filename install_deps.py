"""
Script cài đặt dependencies cho hệ thống gửi file tài chính an toàn
"""

import subprocess
import sys
import os

def install_dependencies():
    """Cài đặt tất cả dependencies cần thiết"""
    
    print("🔧 Đang cài đặt dependencies...")
    
    # Danh sách packages cần thiết
    packages = [
        'Flask',
        'python-dotenv', 
        'pycryptodome',
        'websockets'
    ]
    
    try:
        for package in packages:
            print(f"📦 Cài đặt {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            
        print("✅ Cài đặt dependencies thành công!")
        
        # Tạo thư mục cần thiết
        print("📁 Tạo thư mục...")
        directories = ['uploads', 'received_files', 'test_files']
        for dir_name in directories:
            os.makedirs(dir_name, exist_ok=True)
            print(f"   ✓ {dir_name}/")
            
        print("🎉 Hệ thống đã sẵn sàng!")
        print("\n📋 Hướng dẫn chạy:")
        print("   1. python install_deps.py  (file này)")
        print("   2. python run.py")
        print("   3. Mở browser: http://localhost:5000")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
