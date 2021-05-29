from myApp.exts import db,bootstrap,mqtt,socketio
from myApp.user.models import (Flowerpots, FlowerpotsBehaviors, FlowerpotsData,
                               Users)
from sqlalchemy import or_, and_, not_
from flask import redirect,url_for
import requests,json,random

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('test')
    print("mqtt connected")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(message.payload)
    data=json.loads(message.payload.decode())
    data["flowerpotName"]=message.topic
    #如果是自动控制的,把控制数据传到保存数据的网址上
    if data["isAuto"] == True:
        setWater=random.choice([1,2,3,4,5])
        setLED=random.randint(0,99)
        data["setWater"]=setWater
        data["setLED"]=setLED
        send={}
        send["setWater"]=setWater
        send["setLED"]=setLED
        send["isAuto"]=True
        mqtt.publish("control"+message.topic,payload=json.dumps(send),qos=2)
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