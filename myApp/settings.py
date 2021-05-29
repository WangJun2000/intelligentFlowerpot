#配置文件
class Config:
    DEBUG= False
    SQLALCHEMY_DATABASE_URI ='sqlite:///myApp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    MQTT_BROKER_URL="0.0.0.0"
    MQTT_BROKER_PORT=1883
    MQTT_USERNAME = ""
    MQTT_PASSWORD = ""
    USE_RELOADER = False
    MQTT_TLS_ENABLED= False

class DevelopmentConfig(Config ):
    ENV = 'development'
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG= False