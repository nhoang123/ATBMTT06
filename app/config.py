from datetime import timedelta

class Config:
    SECRET_KEY = 'your-secret-key-here'  # Change this to a secure random key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_COOKIE_NAME = 'default_session'  # Default session cookie name

class SenderConfig(Config):
    SESSION_COOKIE_NAME = 'sender_session'
    SESSION_COOKIE_PATH = '/sender'

class ReceiverConfig(Config):
    SESSION_COOKIE_NAME = 'receiver_session'
    SESSION_COOKIE_PATH = '/receiver'
