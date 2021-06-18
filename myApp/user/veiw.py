import hashlib
import os,json
import random
import threading
#import paho.mqtt.client as mqtt1
from datetime import datetime,timedelta
from flask import (Blueprint, redirect, render_template, request,
                   send_from_directory,url_for,jsonify)

from sqlalchemy import or_, and_, not_
from myApp.exts import db,mqtt
from myApp.user.models import (Flowerpots, FlowerpotsBehaviors, FlowerpotsData,
                               Users)
                        

user_bp = Blueprint('user', __name__)


# 根目录
@user_bp.route('/')
def index():
    return render_template('index.html')

# 网站信息界面
@user_bp.route('/about')
def about():
    return "这是智能电子系统设计与实践课程智能花盆组的实验网站"+"<a href='/'>点此回首页</a>"

# 登录界面
@user_bp.route('/login', methods=['POST', 'GET'])
def login():
    # 不处理GET请求
    if request.method == "GET":
        return render_template('login.html')

    if request.method == 'POST':
        # print(request.path)
        # print(request.full_path)
        user_info = request.form
        userName = user_info.get("userName")
        userPassword = user_info.get("password")
        user = Users.query.filter_by(userName=userName).first()

        if user == None:
            return render_template('login.html', msg="该用户不存在,请先注册")
        else:
            if user.userPassword != hashlib.sha256(userPassword.encode("utf8")).hexdigest():
                return render_template('login.html', msg="用户名和密码不匹配")
            else:
                randAddress = random.random()
                user.temporaryAddress = randAddress
                db.session.add(user)
                db.session.commit()
                return redirect('/user/'+str(randAddress))


# 注册界面
@user_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':
        user_info = request.form
        userName = user_info.get("userName")
        userPassword = user_info.get("password")
        userRePassword = user_info.get("rePassword")

        #用户名或者密码为空
        if userName=="" or userPassword=="":
            return redirect(url_for("user.signup"))
        # 两次密码一致
        if userPassword == userRePassword:
            # 查询是否有这个用户
            if Users.query.filter_by(userName=userName).first() != None:
                return "该用户已存在"
            else:
                user = Users()
                user.userName = userName
                user.userPassword = hashlib.sha256(
                    userPassword.encode('utf8')).hexdigest()
                user.registerTime = datetime.now()
                # 添加到数据库
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("user.login"))
        else:
            return "两次密码不一致"

#绑定花盆
@user_bp.route('/bindFlowerpot',methods=['POST', 'GET'])
def bindFlowerpot():
    if request.method == 'GET':
        return render_template("bindFlowerpot.html")

    if request.method == 'POST':
        user_info = request.form
        flowerpotName = user_info.get("flowerpotName")
        userName = user_info.get("userName")
        userPassword = user_info.get("password")
        user=Users.query.filter_by(userName=userName).first()
        flowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
        if  user== None:
                return "该用户不存在"+"<a href='/'>点此回首页</a>"
        if flowerpot== None:
            return "该花盆不存在"+"<a href='/'>点此回首页</a>"
        else:
            if flowerpot.userId!=None:
                return "该花盆已被绑定"+"<a href='/'>点此回首页</a>"
            else:
                if user.userPassword == hashlib.sha256(userPassword.encode('utf8')).hexdigest():
                    flowerpot.userId=user.id
                    db.session.commit()
                    return "绑定成功"+"<a href='/login'>点此重新登录</a>"
                else:
                    return "密码不正确"+"<a href='/'>点此回首页</a>"
        

#注销
@user_bp.route('/logout')
def logout():
    userName=request.args.get("name")
    user = Users.query.filter_by(userName=userName).first()
    if user==None:
        return "没有该用户"+"<a href='/'>点此回首页</a>"
    user.temporaryAddress=None
    db.session.commit()
    return redirect(url_for('user.login'))


# 导入花盆
@user_bp.route('/registerFlowerpot', methods=['POST', 'GET'])
def registerFlowerpot():
    if request.method == 'GET':
        return render_template("registerFlowerpot.html")
    if request.method == 'POST':
        user_info = request.form
        flowerpotName = user_info.get("flowerpotName")
        if Flowerpots.query.filter_by(flowerpotName=flowerpotName).first() != None:
            return "该花盆已存在"+"<a href='/registerFlowerpot'>点此重新导入</a>"   
        else:
            flowerpot = Flowerpots()
            flowerpot.flowerpotName = flowerpotName
            db.session.add(flowerpot)
            db.session.commit()
            return "花盆导入成功"+"<a href='/registerFlowerpot'>点此重新导入</a>"


# 用户界面
@user_bp.route('/user/<float:userName_encrypt>', methods=['POST', 'GET'])
def show_user(userName_encrypt):
    if request.method == 'GET':
        user = Users.query.filter_by(temporaryAddress=userName_encrypt).first()
        if user == None:
            return "不存在该用户"+"<a href='/login'>点此重新登录</a>"
        else:
            userName = user.userName
            flowerpots = Flowerpots.query.filter(Flowerpots.userId == user.id).order_by(Flowerpots.flowerpotName).all()
            if len(flowerpots)==0:
                return render_template("show.html", name=userName, flowerpots=flowerpots)
            else:
                #默认转到第一个花盆
                currentFlowerpot=flowerpots[0]
                return redirect('/user/'+str(userName_encrypt)+'/'+currentFlowerpot.flowerpotName)
    if request.method == 'POST':

        return "等待开发"


#用户的花盆
@user_bp.route('/user/<float:userName_encrypt>/<flowerpotName>', methods=['POST', 'GET'])
def user_flowerpot(userName_encrypt,flowerpotName):
    if request.method == 'POST':
        return "暂未开发"
    if request.method =='GET':
        user = Users.query.filter_by(temporaryAddress=userName_encrypt).first()
        if user == None:
            return "不存在该用户"+"<a href='/login'>点此重新登录</a>"
        else:
            userName = user.userName
            flowerpots = Flowerpots.query.filter(Flowerpots.userId == user.id).order_by(Flowerpots.flowerpotName).all()
            hasFlowerpot=0
            for flowerpot in flowerpots:
                if flowerpot.flowerpotName==flowerpotName:
                    hasFlowerpot=1
                    currentFlowerpot=flowerpot
                    break
            if hasFlowerpot:
                latestStatus=FlowerpotsData.query.filter(FlowerpotsData.FlowerpotId == currentFlowerpot.id).order_by(-FlowerpotsData.id).first()
                return render_template("flowerpot.html", name=userName, flowerpots=flowerpots,currentFlowerpot=currentFlowerpot,latestStatus=latestStatus)
            else:
                return "该花盆不存在"+"<a href='/login'>点此重新登录</a>"


#用户花盆的历史记录查询
@user_bp.route('/user/<float:userName_encrypt>/<flowerpotName>/history', methods=['POST', 'GET'])
def getHistory(userName_encrypt,flowerpotName):
    if request.method == "POST":
        pass
    if request.method == 'GET':
        user = Users.query.filter_by(temporaryAddress=userName_encrypt).first()
        time=request.args.get("time")
        #print(time)
        if user == None:
            return "不存在该用户"+"<a href='/login'>点此重新登录</a>"
        else:
            userName = user.userName
            flowerpots = Flowerpots.query.filter(Flowerpots.userId == user.id).order_by(Flowerpots.flowerpotName).all()
            hasFlowerpot=0
            for flowerpot in flowerpots:
                if flowerpot.flowerpotName==flowerpotName:
                    hasFlowerpot=1
                    currentFlowerpot=flowerpot
                    break
            if hasFlowerpot:
                flowerpotData=None
                flowerpotBehavior=None
                if time == "10":
                    flowerpotData=FlowerpotsData.query.filter(and_(FlowerpotsData.FlowerpotId == currentFlowerpot.id,FlowerpotsData.testTime>datetime.now()+timedelta(minutes=-10))).all()
                    #print(flowerpotData)
                elif time == "60":
                    flowerpotData=FlowerpotsData.query.filter(and_(FlowerpotsData.FlowerpotId == currentFlowerpot.id,FlowerpotsData.testTime>datetime.now()+timedelta(hours=-1))).all()
                elif time == "1440":
                    flowerpotData=FlowerpotsData.query.filter(and_(FlowerpotsData.FlowerpotId == currentFlowerpot.id,FlowerpotsData.testTime>datetime.now()+timedelta(days=-1))).all()
                elif time == "all":
                    flowerpotData=FlowerpotsData.query.filter(FlowerpotsData.FlowerpotId == currentFlowerpot.id).all()
                else:
                    pass
                #print(flowerpotData)
                return render_template("flowerpotHistory.html", name=userName, flowerpots=flowerpots,currentFlowerpot=currentFlowerpot,flowerpotData=flowerpotData)
            else:
                return "该花盆不存在"+"<a href='/login'>点此重新登录</a>"


#用户花盆的操作历史查询
@user_bp.route('/user/<float:userName_encrypt>/<flowerpotName>/controlhistory', methods=['POST', 'GET'])
def getControlHistory(userName_encrypt,flowerpotName):
    if request.method == "POST":
        pass
    if request.method == 'GET':
        user = Users.query.filter_by(temporaryAddress=userName_encrypt).first()
        time=request.args.get("time")
        #print(time)
        if user == None:
            return "不存在该用户"+"<a href='/login'>点此重新登录</a>"
        else:
            userName = user.userName
            flowerpots = Flowerpots.query.filter(Flowerpots.userId == user.id).order_by(Flowerpots.flowerpotName).all()
            hasFlowerpot=0
            for flowerpot in flowerpots:
                if flowerpot.flowerpotName==flowerpotName:
                    hasFlowerpot=1
                    currentFlowerpot=flowerpot
                    break
            if hasFlowerpot:
                flowerpotBehavior=None
                if time == "10":
                    flowerpotBehavior=FlowerpotsBehaviors.query.filter(and_(FlowerpotsBehaviors.FlowerpotId == currentFlowerpot.id,FlowerpotsBehaviors.controlTime>datetime.now()+timedelta(minutes=-10))).all()
                elif time == "60":
                    flowerpotBehavior=FlowerpotsBehaviors.query.filter(and_(FlowerpotsBehaviors.FlowerpotId == currentFlowerpot.id,FlowerpotsBehaviors.controlTime>datetime.now()+timedelta(hours=-1))).all()
                elif time == "1440":
                    flowerpotBehavior=FlowerpotsBehaviors.query.filter(and_(FlowerpotsBehaviors.FlowerpotId == currentFlowerpot.id,FlowerpotsBehaviors.controlTime>datetime.now()+timedelta(days=-1))).all()
                elif time == "all":
                    flowerpotBehavior=FlowerpotsBehaviors.query.filter(FlowerpotsBehaviors.FlowerpotId == currentFlowerpot.id).all()
                else:
                    pass
                #print(flowerpotBehavior)
                return render_template("flowerpotControlHistory.html", name=userName, flowerpots=flowerpots,currentFlowerpot=currentFlowerpot,flowerpotBehavior=flowerpotBehavior)
            else:
                return "该花盆不存在"+"<a href='/login'>点此重新登录</a>"

#处理ajax请求,更新花盆是人工还是自动状态
@user_bp.route('/change',methods=['GET','POST'])
def change():
    if request.method == 'POST':
        pass
    if request.method == 'GET':
        flowerpotName=request.args.get('flowerpotName')
        flowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
        if flowerpot==None:
            return "没有这个花盆"
        else:
            flowerpot.isAuto=bool(1-flowerpot.isAuto)
            db.session.commit()
            send={}
            send["setWater"]=-1
            send["setLED"]=-1
            send["isAuto"]=flowerpot.isAuto
            print(flowerpotName)
            print(send)
            #mqtt.publish("control"+flowerpotName,payload=json.dumps(send),qos=1)
            isAutoFile=open("isAuto"+flowerpotName+".txt","w")
            isAutoFile.write(str(flowerpot.isAuto))
            isAutoFile.close()
            return ''
            

#人工控制浇水量
@user_bp.route('/peoplewater',methods=['GET','POST'])
def peoplewater():
    if request.method == 'POST':
        pass
    if request.method == 'GET':
        flowerpotName=request.args.get('flowerpotName')
        watergrade=request.args.get('watergrade')
        flowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
        if flowerpot==None:
            return "没有这个花盆"
        else:
            flowerpotBehavior=FlowerpotsBehaviors()
            flowerpotBehavior.setLED=-1
            flowerpotBehavior.setWater=watergrade
            flowerpotBehavior.isAuto=False
            flowerpotBehavior.FlowerpotId=flowerpot.id
            data={}
            data["setWater"]=watergrade
            data["setLED"]=-1
            data["isAuto"]=False
            #print (threading.currentThread())
            #mqtt.publish("control"+flowerpotName,payload=json.dumps(data),qos=2)
            db.session.add(flowerpotBehavior)
            db.session.commit()
            controlWaterFile=open("controlWater"+flowerpotName+".txt","w")
            controlWaterFile.write(str(watergrade))
            controlWaterFile.close()
            return 'success'

#人工设置光强
@user_bp.route('/peoplesetLED',methods=['GET','POST'])
def peoplesetLED():
    if request.method == 'POST':
        pass
    if request.method == 'GET':
        flowerpotName=request.args.get('flowerpotName')
        lightIntensity=request.args.get('lightIntensity')
        flowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
        if flowerpot==None:
            return "没有这个花盆"
        else:
            flowerpotBehavior=FlowerpotsBehaviors()
            flowerpotBehavior.setLED=lightIntensity
            flowerpotBehavior.setWater=-1
            flowerpotBehavior.isAuto=False
            flowerpotBehavior.FlowerpotId=flowerpot.id
            data={}
            data["setWater"]=-1
            data["setLED"]=lightIntensity
            data["isAuto"]=False
            #mqtt.publish("control"+flowerpotName,payload=json.dumps(data),qos=2)
            db.session.add(flowerpotBehavior)
            db.session.commit()
            controlLEDFile=open("controlLED"+flowerpotName+".txt","w")
            controlLEDFile.write(str(lightIntensity))
            controlLEDFile.close()
            return 'success'

#获取花盆的最新状态
@user_bp.route('/upadate')
def update():
    flowerpotName=request.args.get('flowerpotName')
    currentFlowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
    latestStatus=FlowerpotsData.query.filter(FlowerpotsData.FlowerpotId == currentFlowerpot.id).order_by(-FlowerpotsData.id).first()
    if latestStatus!=None:
        return jsonify(testTime=str(latestStatus.testTime),temperature=latestStatus.temperature,soilHumidity=latestStatus.soilHumidity,lightIntensity=latestStatus.lightIntensity)
    else:
        return ""
        

#添加花盆的历史信息
@user_bp.route('/history')
def history():
    flowerpotName=request.args.get('flowerpotName')
    IP=request.args.get('IP')
    port=request.args.get('port')
    temperature=request.args.get('temperature')
    soilHumidity=request.args.get('soilHumidity')
    lightIntensity=request.args.get("lightIntensity")
    currentFlowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
    if currentFlowerpot==None:
        return render_template("history.html")
    else:
        currentFlowerpot.IP=IP
        currentFlowerpot.port=port
        flowerpotData=FlowerpotsData()
        flowerpotData.temperature=temperature
        flowerpotData.soilHumidity=soilHumidity
        flowerpotData.lightIntensity=lightIntensity
        flowerpotData.FlowerpotId=currentFlowerpot.id
        db.session.add(flowerpotData)
        db.session.commit()
        return  render_template("history.html",msg="添加历史数据成功")

#用于测试
@user_bp.route('/test')
def test():
    return "test"

#用于储存单片机传给mqtt的数据
@user_bp.route('/saveFlowerpotsData')
def saveFlowerpotsData():
    flowerpotName=request.args.get('flowerpotName')
    temperature=request.args.get("temperature")
    soilHumidity=request.args.get("soilHumidity")
    lightIntensity=request.args.get("lightIntensity")
    isAuto=request.args.get("isAuto")
    currentFlowerpot= Flowerpots.query.filter_by(flowerpotName=flowerpotName).first()
    if currentFlowerpot==None:
        return "不存在此花盆"
    else:
        flowerpotData=FlowerpotsData()
        flowerpotData.temperature=temperature
        flowerpotData.soilHumidity=soilHumidity
        flowerpotData.lightIntensity=lightIntensity
        flowerpotData.FlowerpotId=currentFlowerpot.id
        db.session.add(flowerpotData)
        #判断是否是自动控制,如果是就根据当前环境做控制,并且把控制数据导入数据库
        if isAuto == "True":
            flowerpotBehavior=FlowerpotsBehaviors()
            setWater=request.args.get("setWater")
            setLED=request.args.get("setLED")
            flowerpotBehavior.setWater=setWater
            flowerpotBehavior.setLED=setLED
            flowerpotBehavior.isAuto=True
            flowerpotBehavior.FlowerpotId = currentFlowerpot.id
            db.session.add(flowerpotBehavior)
            #print(3)
        db.session.commit()
        return "保存成功"