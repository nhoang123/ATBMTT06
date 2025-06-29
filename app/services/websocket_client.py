"""
WebSocket Client để test gửi file tài chính an toàn
Thực hiện vai trò người gửi theo đề tài 4
"""

import json
import asyncio
import websockets
import logging
from pathlib import Path
from app.services.crypto_service import SecureFileTransfer

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureFileClient:
    """WebSocket Client gửi file an toàn"""
    
    def __init__(self, server_uri="ws://localhost:8765"):
        """
        Khởi tạo client
        Args:
            server_uri (str): URI của WebSocket server
        """
        self.server_uri = server_uri
        self.websocket = None
        self.transfer_service = SecureFileTransfer()
        self.receiver_public_key = None
        self.state = 'disconnected'
        
    async def connect(self):
        """Kết nối tới WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_uri)
            self.state = 'connected'
            logger.info(f"Đã kết nối tới server: {self.server_uri}")
            return True
        except Exception as e:
            logger.error(f"Không thể kết nối server: {e}")
            return False
    
    async def disconnect(self):
        """Ngắt kết nối khỏi server"""
        if self.websocket:
            await self.websocket.close()
            self.state = 'disconnected'
            logger.info("Đã ngắt kết nối khỏi server")
    
    async def send_message(self, message_data):
        """
        Gửi message tới server
        Args:
            message_data (dict): Dữ liệu message
        Returns:
            dict: Phản hồi từ server
        """
        if not self.websocket:
            raise Exception("Chưa kết nối tới server")
        
        # Gửi message
        await self.websocket.send(json.dumps(message_data))
        logger.info(f"Đã gửi message type: {message_data.get('type')}")
        
        # Đợi phản hồi
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def perform_handshake(self):
        """
        Thực hiện bước handshake
        Returns:
            bool: True nếu thành công
        """
        try:
            # Gửi "Hello!"
            response = await self.send_message({
                'type': 'hello',
                'message': 'Hello!'
            })
            
            if (response.get('type') == 'handshake_response' and 
                response.get('message') == 'Ready!'):
                self.state = 'handshake_complete'
                logger.info("Handshake thành công")
                return True
            else:
                logger.error(f"Handshake thất bại: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi handshake: {e}")
            return False
    
    async def exchange_keys(self):
        """
        Trao đổi khóa công khai
        Returns:
            bool: True nếu thành công
        """
        try:
            # Khởi tạo sender và lấy public key
            sender_public_key = self.transfer_service.initialize_sender()
            
            # Gửi public key tới server
            response = await self.send_message({
                'type': 'key_exchange',
                'action': 'send_public_key',
                'public_key': sender_public_key
            })
            
            if response.get('status') == 'success':
                # Lưu public key của receiver
                self.receiver_public_key = response.get('public_key')
                self.transfer_service.set_receiver_public_key(self.receiver_public_key)
                self.state = 'keys_exchanged'
                logger.info("Trao đổi khóa thành công")
                return True
            else:
                logger.error(f"Trao đổi khóa thất bại: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi trao đổi khóa: {e}")
            return False
    
    async def send_file(self, file_path):
        """
        Gửi file đã mã hóa tới server
        Args:
            file_path (str): Đường dẫn file cần gửi
        Returns:
            bool: True nếu thành công
        """
        try:
            # Kiểm tra file tồn tại
            if not Path(file_path).exists():
                logger.error(f"File không tồn tại: {file_path}")
                return False
            
            logger.info(f"Đang chuẩn bị gửi file: {file_path}")
            
            # Chuẩn bị gói tin file
            metadata_signature, encrypted_session_key, file_package = \
                self.transfer_service.prepare_file_package(file_path)
            
            # Tạo metadata
            filename = Path(file_path).name
            metadata = self.transfer_service.crypto.create_metadata(filename)
            
            # Gửi gói tin file
            response = await self.send_message({
                'type': 'file_transfer',
                'metadata': metadata,
                'metadata_signature': metadata_signature,
                'encrypted_session_key': encrypted_session_key,
                'file_package': file_package
            })
            
            # Kiểm tra phản hồi
            if response.get('type') == 'ack':
                logger.info(f"File gửi thành công: {response.get('message')}")
                return True
            elif response.get('type') == 'nack':
                logger.error(f"File bị từ chối: {response.get('message')}")
                return False
            else:
                logger.error(f"Phản hồi không mong đợi: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi gửi file: {e}")
            return False
    
    async def send_file_secure(self, file_path):
        """
        Quy trình hoàn chỉnh gửi file an toàn
        Args:
            file_path (str): Đường dẫn file cần gửi
        Returns:
            bool: True nếu thành công
        """
        try:
            logger.info("=== BẮT ĐẦU QUY TRÌNH GỬI FILE AN TOÀN ===")
            
            # 1. Kết nối tới server
            if not await self.connect():
                return False
            
            # 2. Thực hiện handshake
            if not await self.perform_handshake():
                return False
            
            # 3. Trao đổi khóa
            if not await self.exchange_keys():
                return False
            
            # 4. Gửi file
            if not await self.send_file(file_path):
                return False
            
            logger.info("=== GỬI FILE THÀNH CÔNG ===")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi quy trình gửi file: {e}")
            return False
        finally:
            await self.disconnect()


# Hàm test client
async def test_send_file(file_path="test_files/finance.txt"):
    """
    Test gửi file tài chính
    Args:
        file_path (str): Đường dẫn file test
    """
    # Tạo file test nếu chưa có
    test_file = Path(file_path)
    test_file.parent.mkdir(exist_ok=True)
    
    if not test_file.exists():
        # Tạo nội dung file tài chính mẫu
        sample_content = """BÁOTÀI CHÍNH - NGÂN HÀNG ABC
=================================
Ngày báo cáo: 2025-06-29
Số dư tài khoản: 1,250,000,000 VNĐ
Giao dịch trong tháng:
- Thu: 500,000,000 VNĐ
- Chi: 300,000,000 VNĐ
- Lãi suất: 2.5%/năm
- Phí dịch vụ: 50,000 VNĐ

THÔNG TIN BẢO MẬT - KHÔNG SAO CHÉP
"""
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        logger.info(f"Đã tạo file test: {test_file}")
    
    # Khởi tạo client và gửi file
    client = SecureFileClient()
    success = await client.send_file_secure(str(test_file))
    
    if success:
        print("✅ Test thành công - File đã được gửi an toàn!")
    else:
        print("❌ Test thất bại - Có lỗi trong quá trình gửi file")


if __name__ == "__main__":
    # Chạy test
    asyncio.run(test_send_file())
