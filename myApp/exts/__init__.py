# 创建一个映射对象
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

db = SQLAlchemy()
bootstrap = Bootstrap()
mqtt = Mqtt()
socketio= SocketIO()
