from flask import Flask
from app.models import db, User
from flask_login import LoginManager
from flask_socketio import SocketIO

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Đường dẫn login, đổi nếu cần
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)  # Khởi tạo SocketIO với app

    # Đăng ký blueprint auth
    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.key import key_bp
    app.register_blueprint(key_bp)

    from app.sender import sender_bp
    app.register_blueprint(sender_bp)
    from app.receiver import receiver_bp
    app.register_blueprint(receiver_bp)

    # Đăng ký các sự kiện WebSocket
    from app import ws

    # Tạo bảng CSDL nếu chưa có
    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
