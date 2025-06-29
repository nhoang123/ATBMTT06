"""
WebSocket Server xử lý giao tiếp an toàn cho gửi file tài chính
Thực hiện handshake, trao khóa và truyền file theo đề tài 4
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


class SecureFileServer:
    """WebSocket Server xử lý truyền file an toàn"""
    
    def __init__(self):
        """Khởi tạo server"""
        self.clients = {}  # Lưu thông tin clients kết nối
        self.file_transfer = SecureFileTransfer()
        
    async def handle_client(self, websocket):
        """
        Xử lý kết nối từ client
        Args:
            websocket: WebSocket connection
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client {client_id} đã kết nối")
        
        try:
            # Đăng ký client
            self.clients[client_id] = {
                'websocket': websocket,
                'state': 'connected',
                'transfer_service': SecureFileTransfer()
            }
            
            # Xử lý các message từ client
            async for message in websocket:
                await self.process_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} đã ngắt kết nối")
        except Exception as e:
            logger.error(f"Lỗi xử lý client {client_id}: {e}")
        finally:
            # Cleanup khi client ngắt kết nối
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def process_message(self, client_id, message):
        """
        Xử lý message từ client theo luồng đề tài 4
        Args:
            client_id (str): ID của client
            message (str): Message JSON từ client
        """
        try:
            data = json.loads(message)
            message_type = data.get('type')
            client_info = self.clients[client_id]
            websocket = client_info['websocket']
            
            logger.info(f"Client {client_id} gửi message type: {message_type}")
            
            # 1. HANDSHAKE - Bắt tay ban đầu
            if message_type == 'hello':
                await self.handle_handshake(client_id, data)
                
            # 2. KEY_EXCHANGE - Trao đổi khóa công khai
            elif message_type == 'key_exchange':
                await self.handle_key_exchange(client_id, data)
                
            # 3. FILE_TRANSFER - Gửi file đã mã hóa
            elif message_type == 'file_transfer':
                await self.handle_file_transfer(client_id, data)
                
            # 4. RECEIVER_READY - Người nhận sẵn sàng
            elif message_type == 'receiver_ready':
                await self.handle_receiver_ready(client_id, data)
                
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Loại message không hỗ trợ: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Message không đúng định dạng JSON'
            }))
        except Exception as e:
            logger.error(f"Lỗi xử lý message: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Lỗi server: {str(e)}'
            }))
    
    async def handle_handshake(self, client_id, data):
        """
        Xử lý bước handshake
        Args:
            client_id (str): ID client
            data (dict): Dữ liệu handshake
        """
        websocket = self.clients[client_id]['websocket']
        
        if data.get('message') == 'Hello!':
            # Phản hồi "Ready!" để hoàn thành handshake
            self.clients[client_id]['state'] = 'ready'
            await websocket.send(json.dumps({
                'type': 'handshake_response',
                'message': 'Ready!'
            }))
            logger.info(f"Handshake thành công với client {client_id}")
        else:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Handshake không hợp lệ'
            }))
    
    async def handle_key_exchange(self, client_id, data):
        """
        Xử lý trao đổi khóa công khai
        Args:
            client_id (str): ID client
            data (dict): Dữ liệu chứa public key
        """
        websocket = self.clients[client_id]['websocket']
        transfer_service = self.clients[client_id]['transfer_service']
        
        try:
            if data.get('action') == 'send_public_key':
                # Nhận public key từ người gửi
                sender_public_key = data.get('public_key')
                
                # Khởi tạo receiver và gửi public key của receiver
                receiver_public_key = transfer_service.initialize_receiver()
                
                # Lưu public key của sender
                self.clients[client_id]['sender_public_key'] = sender_public_key
                self.clients[client_id]['state'] = 'keys_exchanged'
                
                await websocket.send(json.dumps({
                    'type': 'key_exchange_response',
                    'public_key': receiver_public_key,
                    'status': 'success'
                }))
                
                logger.info(f"Trao đổi khóa thành công với client {client_id}")
                
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Lỗi trao đổi khóa: {str(e)}'
            }))
    
    async def handle_file_transfer(self, client_id, data):
        """
        Xử lý gói tin file đã mã hóa
        Args:
            client_id (str): ID client
            data (dict): Gói tin file
        """
        websocket = self.clients[client_id]['websocket']
        transfer_service = self.clients[client_id]['transfer_service']
        
        try:
            # Lấy thông tin từ gói tin
            metadata = data.get('metadata')
            metadata_signature = data.get('metadata_signature')
            encrypted_session_key = data.get('encrypted_session_key')
            file_package = data.get('file_package')
            sender_public_key = self.clients[client_id].get('sender_public_key')
            
            if not all([metadata, metadata_signature, encrypted_session_key, file_package, sender_public_key]):
                await websocket.send(json.dumps({
                    'type': 'nack',
                    'message': 'Thiếu thông tin trong gói tin'
                }))
                return
            
            # Xác minh và giải mã gói tin file
            success, result = transfer_service.verify_and_decrypt_package(
                metadata, metadata_signature, encrypted_session_key, 
                file_package, sender_public_key
            )
            
            if not success:
                await websocket.send(json.dumps({
                    'type': 'nack',
                    'message': f'Xác minh thất bại: {result}'
                }))
                return
            
            # Lưu file đã giải mã
            metadata_obj = json.loads(metadata)
            filename = metadata_obj.get('filename', 'finance.txt')
            
            # Tạo thư mục received nếu chưa có
            received_dir = Path('received_files')
            received_dir.mkdir(exist_ok=True)
            
            # Lưu file
            file_path = received_dir / filename
            with open(file_path, 'wb') as f:
                f.write(result)  # result là dữ liệu đã giải mã
            
            # Gửi ACK
            await websocket.send(json.dumps({
                'type': 'ack',
                'message': f'File {filename} đã được nhận và lưu thành công',
                'saved_path': str(file_path)
            }))
            
            logger.info(f"File {filename} từ client {client_id} đã được lưu tại {file_path}")
                
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'nack',
                'message': f'Lỗi xử lý file: {str(e)}'
            }))
            logger.error(f"Lỗi xử lý file từ client {client_id}: {e}")
    
    async def handle_receiver_ready(self, client_id, data):
        """
        Xử lý thông báo receiver sẵn sàng nhận file
        Args:
            client_id (str): ID client
            data (dict): Dữ liệu receiver ready
        """
        websocket = self.clients[client_id]['websocket']
        
        # Cập nhật trạng thái
        self.clients[client_id]['state'] = 'receiver_ready'
        
        await websocket.send(json.dumps({
            'type': 'receiver_status',
            'message': 'Server sẵn sàng nhận file',
            'status': 'ready'
        }))
        
        logger.info(f"Client {client_id} đã sẵn sàng làm receiver")


# Hàm khởi chạy WebSocket server
async def start_secure_server(host='localhost', port=8765):
    """
    Khởi chạy WebSocket server
    Args:
        host (str): Địa chỉ host
        port (int): Port server
    """
    server = SecureFileServer()
    
    logger.info(f"Đang khởi chạy Secure File Transfer Server tại ws://{host}:{port}")
    
    # Khởi chạy WebSocket server
    async with websockets.serve(server.handle_client, host, port):
        logger.info("Server đã sẵn sàng nhận kết nối...")
        await asyncio.Future()  # Chạy mãi mãi


if __name__ == "__main__":
    # Chạy server
    asyncio.run(start_secure_server())
