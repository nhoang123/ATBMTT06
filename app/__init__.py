from flask import Flask
from app.models import db, User
from flask_login import LoginManager
from flask_socketio import SocketIO
from app.config import Config, SenderConfig, ReceiverConfig

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Đường dẫn login, đổi nếu cần
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Đăng ký blueprint auth
    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.key import key_bp
    app.register_blueprint(key_bp)

    # Đăng ký sender blueprint với cấu hình sender
    from app.sender import sender_bp
    app_sender = Flask(__name__)
    app_sender.config.from_object(SenderConfig)
    sender_bp.config = app_sender.config
    app.register_blueprint(sender_bp, url_prefix='/sender')

    # Đăng ký receiver blueprint với cấu hình receiver
    from app.receiver import receiver_bp
    app_receiver = Flask(__name__)
    app_receiver.config.from_object(ReceiverConfig)
    receiver_bp.config = app_receiver.config
    app.register_blueprint(receiver_bp, url_prefix='/receiver')

    # Đăng ký các sự kiện WebSocket
    from app import ws

    # Tạo bảng CSDL nếu chưa có
    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
