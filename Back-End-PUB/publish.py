import os
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import Flask
from flask_socketio import SocketIO, emit
import threading

# MQTT 配置
broker = "43.142.99.126"
port = 1883
topic = "publish/1111"

# Flask 配置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 文件路径
file_path = "D:/LoT/Publisher/sorted_data.json"

# 全局变量存储最新数据
latest_data = None

# MQTT 连接回调
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code:", rc)

# MQTT 消息回调
def on_message(client, userdata, msg):
    global latest_data
    try:
        payload = json.loads(msg.payload.decode())
        latest_data = {
            "topic": msg.topic,
            "message": payload,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        print(f"New message received: {latest_data}")

        # 推送给所有前端客户端
        socketio.emit('new_message', latest_data)
    except json.JSONDecodeError as e:
        print(f"Failed to decode message: {e}")

# 启动 MQTT 客户端
def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.subscribe(topic)
    client.loop_forever()

# Flask 路由
@app.route("/")
def index():
    return "MQTT Publisher Backend Running"

# WebSocket 事件
@socketio.on('connect')
def handle_connect():
    print("Frontend connected")
    if latest_data:
        emit('new_message', latest_data)  # 推送最新数据

# 定时发布数据
def publish_data():
    global latest_data
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.loads(file.read())
                now = datetime.now().strftime('%Y-%m-%dT%H:%M:00')
                for item in data:
                    if item["timestamp"] == now:
                        # 发布 MQTT 消息
                        client = mqtt.Client()
                        client.connect(broker, port, 60)
                        client.publish(topic, json.dumps(item))
                        latest_data = {
                            "topic": topic,
                            "message": item,
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        print(f"Published data: {latest_data}")
                        break
            except json.JSONDecodeError as e:
                print(f"Error reading JSON: {e}")

def schedule_publish():
    while True:
        now = datetime.now()
        if now.minute in [0, 20, 50]:
            publish_data()
            time.sleep(60)
        else:
            time.sleep(30)

# 启动 Flask 和 MQTT
if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.start()

    publish_thread = threading.Thread(target=schedule_publish)
    publish_thread.start()

    socketio.run(app, host="0.0.0.0", port=5000)
