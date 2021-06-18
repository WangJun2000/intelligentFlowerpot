from myApp.exts import db,bootstrap,mqtt,socketio
from myApp.user.models import (Flowerpots, FlowerpotsBehaviors, FlowerpotsData,
                               Users)
from sqlalchemy import or_, and_, not_
from flask import redirect,url_for
import requests,json,random

lastSetLED=0

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('test')
    print("mqtt connected")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(message.payload)
    data=json.loads(message.payload.decode())
    data["flowerpotName"]=message.topic
    #对光照强度进行转换
    light=data["lightIntensity"]
    if light<16:
       data["lightIntensity"]=1000
    elif light<=18:
        data["lightIntensity"]=(864-731)/(16-18)*(light-16)+864
    elif light<=29:
        data["lightIntensity"]=(731-512)/(18-29)*(light-18)+731
    elif light<=32:
        data["lightIntensity"]=(512-469)/(29-32)*(light-29)+512
    elif light<=68:
        data["lightIntensity"]=(469-144)/(32-68)*(light-32)+469
    elif light<=77:
        data["lightIntensity"]=(144-125)/(68-77)*(light-68)+144
    elif light<=90:
        data["lightIntensity"]=(125-108)/(77-90)*(light-77)+125
    elif light<=100:
        data["lightIntensity"]=(108-85)/(90-100)*(light-90)+108
    elif light<=136:
        data["lightIntensity"]=(85-58)/(100-136)*(light-100)+85
    elif light<=156:
        data["lightIntensity"]=(58-30)/(136-156)*(light-136)+58
    elif light<=237:
        data["lightIntensity"]=(30-12)/(156-237)*(light-156)+30
    elif light<=320:
        data["lightIntensity"]=(12-7)/(237-320)*(light-237)+12
    elif light<=456:
        data["lightIntensity"]=(7-2)/(320-456)*(light-320)+7
    elif light<=600:
        data["lightIntensity"]=(2-1)/(456-600)*(light-456)+2
    elif light<=952:
        data["lightIntensity"]=(1-0)/(600-952)*(light-600)+1
    else:
        data["lightIntensity"]=0
    isAutoFile=open("isAuto"+data["flowerpotName"]+".txt","r")
    isAuto=isAutoFile.read()
    isAutoFile.close()
    #如果是自动控制的,把控制数据传到保存数据的网址上
    if isAuto=="True":
        if data["soilHumidity"]<0.5:
            setWater=3
        else:
            setWater=0
        try:
            with open("lastSetLED"+data["flowerpotName"]+".txt","r+") as lastSetLEDFile:
                lastSetLED=int(lastSetLEDFile.read())
                lastSetLEDFile.close()
        except FileNotFoundError:
            with open("lastSetLED"+data["flowerpotName"]+".txt","w") as lastSetLEDFile:
                lastSetLEDFile.write("0")
                lastSetLED=0
                lastSetLEDFile.close()
        if data["lightIntensity"]<10:
            setLED=min(lastSetLED+10,100)
        else:
            setLED=max(lastSetLED-10,0)
        lastSetLED=setLED
        with open("lastSetLED"+data["flowerpotName"]+".txt","r+") as lastSetLEDFile:
            lastSetLEDFile.truncate(0)
            lastSetLEDFile.write(str(lastSetLED))
            lastSetLEDFile.close()
        data["isAuto"]=True
        data["setWater"]=setWater
        data["setLED"]=setLED
        send={}
        send["setWater"]=setWater
        send["setLED"]=setLED
        send["isAuto"]=True
        mqtt.publish("control"+message.topic,payload=json.dumps(send),qos=1)
    else:
        data["isAuto"]=False
        needSend=False
        send={}
        send["setWater"]=-1
        send["setLED"]=-1
        send["isAuto"]=False
        controlWaterFile=open("controlWater"+data["flowerpotName"]+".txt","r+")
        controlWater=controlWaterFile.read()
        print(controlWater)
        if controlWater=="":
            controlWaterFile.close()
        else:
            needSend=True
            send["setWater"]=int(controlWater)
            controlWaterFile.truncate(0)
            controlWaterFile.close()
        controlLEDFile=open("controlLED"+data["flowerpotName"]+".txt","r+")
        controlLED=controlLEDFile.read()
        if controlLED=="":
            controlLEDFile.close()
        else:
            needSend=True
            send["setLED"]=int(controlLED)
            controlLEDFile.truncate(0)
            controlLEDFile.close()
        if needSend:
            mqtt.publish("control"+message.topic,payload=json.dumps(send),qos=1)
        
    print("收到数据")
    print(data)
    '''headers={}
    user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/61.0",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
                    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                    ]
    headers['User-Agent'] = random.choice(user_agent_list)
    headers['Proxy-Connection']="close"'''
    url="http://106.13.121.233:80/saveFlowerpotsData"
    res = requests.get(url=url,params=data)
    print(res.text)

@mqtt.on_publish()
def handle_publish(client, userdata, mid):
    print('Published message with mid {}.'.format(mid))
    pass

@mqtt.on_disconnect()
def handle_disconnect(client,userdata,rc):
    if rc!=0:
        print("意外失去连接%s"%rc)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_ERR:
        print('Error: {}'.format(buf))