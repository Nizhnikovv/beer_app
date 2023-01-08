import json

with open("/etc/config_beersite.json") as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get("SECRET_KEY")
    DB_NAME = "site.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_NAME
    MAIL_SERVER = "smtp.mail.ru"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "dmitrix_n@mail.ru" 
    MAIL_PASSWORD = config.get("MAIL_PASSWORD")