# ORM 类 映射到 表
# 类对象 映射到 表中的一条记录
from datetime import datetime

from myApp.exts import db


# 所有用户
class Users(db.Model):
    # db.Column(类型,约束) 映射表中的列
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    userName = db.Column(db.String(40), nullable=False, unique=True)
    userPassword = db.Column(db.String(100), nullable=False)
    registerTime = db.Column(db.DateTime, default=datetime.now)
    flowerpots = db.relationship("Flowerpots", backref="user")
    temporaryAddress = db.Column(db.Float(), unique=True)

    def __str__(self):
        return self.userName

# 所有花盆,用户对应花盆是一对多


class Flowerpots(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    isAuto = db.Column(db.Boolean, nullable=False, default=True)
    flowerpotName = db.Column(db.String(20), nullable=False, unique=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))
    IP=db.Column(db.String(20))
    port=db.Column(db.Integer)
    flowerpotData = db.relationship("FlowerpotsData", backref="flowerpot")
    flowerpotBehavior = db.relationship("FlowerpotsBehaviors", backref="flowerpot")

    def __str__(self):
        return self.flowerpotName

# 所有花盆的历史数据


class FlowerpotsData(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    temperature = db.Column(db.Float(), nullable=False)
    soilHumidity = db.Column(db.Float(), nullable=False)
    lightIntensity = db.Column(db.Float(), nullable=False)
    testTime = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    FlowerpotId = db.Column(db.Integer, db.ForeignKey(
        "flowerpots.id"), nullable=False)

    def __str__(self):
        return str(self.FlowerpotId)

# 所有花盆的历史行为


class FlowerpotsBehaviors(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    setLED = db.Column(db.Float(), nullable=False)#当是-1的时候代表不操作
    setWater = db.Column(db.Float(), nullable=False)#当是-1的时候代表不操作
    isAuto= db.Column(db.Boolean,nullable=False, default=True)#默认是自动操作
    controlTime=db.Column(db.DateTime(),nullable=False,default=datetime.now)
    FlowerpotId = db.Column(db.Integer, db.ForeignKey(
        "flowerpots.id"), nullable=False)

    def __str__(self):
        return str(self.FlowerpotId)
