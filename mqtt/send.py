import paho.mqtt.client as mqtt

client = mqtt.Client()
# 参数有 Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
client.connect("度武器IP地址", 1883, 60)  # 连接服务器,端口为1883,维持心跳为60秒
client.publish('test', 'test string',1)