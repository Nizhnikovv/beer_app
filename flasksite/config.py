

class Config:
    DB_NAME = "site.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_NAME
    MAIL_SERVER = "smtp.mail.ru"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "dmitrix_n@mail.ru" 
    CELERY_BROKER = "redis://localhost:6379/0"

class ProductionConfig(Config):
    SERVER_NAME = "1221.pro"
    PREFERRED_URL_SCHEME = "https"


class DevelopmentConfig(Config):
    SERVER_NAME = "localhost:8000"


class TestingConfig(Config):
    SERVER_NAME = "localhost:5000"
    DEBUG = True
    TESTING = True
