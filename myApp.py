import socket

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from myApp import create_app
from myApp.exts import db,mqtt
from myApp.user.models import (Flowerpots, FlowerpotsBehaviors, FlowerpotsData,
                               Users)
from sqlalchemy import or_, and_, not_

app=create_app()
manager = Manager(app=app)

# 命令工具
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)



@manager.command
def init():
    print("初始化")


if __name__ == '__main__':
    #hostIp = socket.gethostbyname(socket.gethostname())
    #print(hostIp)
    manager.run()
