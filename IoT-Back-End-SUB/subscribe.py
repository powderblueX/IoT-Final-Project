import paho.mqtt.client as mqtt
import json
import os
from flask import Flask, jsonify
from threading import Thread
import signal
import sys
from flask_cors import CORS

# MQTT配置
BROKER = "43.142.99.126"
PORT = 1883  # MQTT代理端口
TOPIC = "publish/1111"

# Flask 应用
app = Flask(__name__)

# 启用 CORS，只允许特定来源
CORS(app)

# 文件存储路径
FILE_PATH = "mqtt_data.json"

# MQTT 客户端实例
mqtt_client = mqtt.Client()

# 回调函数 - 连接
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe(TOPIC)  # 订阅主题
    else:
        print(f"Failed to connect, return code {rc}")

# 回调函数 - 收到消息
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        print(f"Received message: {data}")

        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, 'w') as file:
                json.dump([], file)

        with open(FILE_PATH, 'r+') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file, indent=4)

        print("Data saved successfully!")
    except Exception as e:
        print(f"Error processing message: {e}")

# 提取最后9条数据
def get_last_n_data(n=9):
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, 'r') as file:
            file_data = json.load(file)
            return file_data[-n:] if len(file_data) >= n else file_data
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# 定义API路由
@app.route('/get-latest-data', methods=['GET'])
def get_latest_data():
    data = get_last_n_data(9)  # 获取最后9条数据
    return jsonify(data)

# MQTT客户端运行
def run_mqtt_client():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_forever()

# 信号处理函数
def signal_handler(sig, frame):
    print("Gracefully shutting down...")
    mqtt_client.disconnect()  # 断开MQTT连接
    mqtt_client.loop_stop()   # 停止MQTT循环
    sys.exit(0)

if __name__ == '__main__':
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动MQTT客户端线程
    mqtt_thread = Thread(target=run_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # 启动Flask应用
    app.run(host='0.0.0.0', port=5001)
