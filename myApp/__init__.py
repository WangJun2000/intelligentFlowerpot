from flask import Flask
import eventlet

from myApp import settings
from myApp.user.veiw import user_bp
from myApp.exts import db,bootstrap,mqtt,socketio
from myApp.user.models import (Flowerpots, FlowerpotsBehaviors, FlowerpotsData,
                               Users)
from sqlalchemy import or_, and_, not_
from myApp.user import mqttCallback

def create_app():
    #eventlet.monkey_patch()
    app = Flask(__name__)
    app.config.from_object(settings.DevelopmentConfig)  # 配置
    app.register_blueprint(user_bp)  # 蓝图
    db.init_app(app=app)  # 将db对象和app关联
    app.app_context().push()
    mqtt.init_app(app=app)    #将mqtt对象和app关联
    socketio.init_app(app=app) #将socketio对象和app关联
    bootstrap.init_app(app=app) #将bootstrap对象初始化
    #print("app") 
    #订阅所有花盆
    flowerpots=Flowerpots.query.filter().all()
    for flowerpot in flowerpots:
        mqtt.subscribe(flowerpot.flowerpotName)
        print("subscribe:"+flowerpot.flowerpotName)
    #print (app.url_map)
    #print(app.config)
    return app


