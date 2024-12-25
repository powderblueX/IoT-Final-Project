import json
import os
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import threading
import paho.mqtt.client as mqtt
from flask_cors import CORS  # 导入CORS

# 定义 Flask 应用
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 启用跨域支持，允许所有 IP 访问

# 定义数据保存路径
save_paths = {
    "sensor/temperature": "DownloadData/temperature_data.json",
    "sensor/humidity": "DownloadData/humidity_data.json",
    "sensor/pressure": "DownloadData/pressure_data.json",
}

# 定义预测结果保存路径
prediction_save_paths = {
    "sensor/temperature": "DownloadData/temperature_predictions.json",
    "sensor/humidity": "DownloadData/humidity_predictions.json",
    "sensor/pressure": "DownloadData/pressure_predictions.json",
}

# MQTT 消息处理回调函数
def on_message(client, userdata, msg):
    try:
        print(f"Received raw message: {msg.payload.decode()} on topic {msg.topic}")
        data_list = json.loads(msg.payload.decode())  # 解析接收到的 JSON 数据列表
        # print(f"Parsed data: {data_list}")

        for data in data_list:  # 遍历每个数据项
            timestamp = data['timestamp']
            if "temperature" in data:
                process_sensor_data(data, "temperature", save_paths["sensor/temperature"], "sensor/temperature")
            if "humidity" in data:
                process_sensor_data(data, "humidity", save_paths["sensor/humidity"], "sensor/humidity")
            if "pressure" in data:
                process_sensor_data(data, "pressure", save_paths["sensor/pressure"], "sensor/pressure")

    except Exception as e:
        print(f"Error in on_message: {e}")

# 处理传感器数据
def process_sensor_data(data, sensor_type, file_path, topic):
    try:
        # 将新数据添加到历史数据文件
        if sensor_type in data:
            sensor_data = {
                "timestamp": data['timestamp'],
                "value": float(data[sensor_type])  # 将传感器值转换为浮动类型
            }
            save_to_local(sensor_data, file_path)

            # 重新加载更新后的历史数据，并进行预测
            run_prediction_with_history(file_path, topic)

    except Exception as e:
        print(f"Error processing {sensor_type} data: {e}")

# 保存数据到本地
def save_to_local(data, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)
        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=4)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

# 加载历史数据
def load_data_from_file(file_path):
    try:
        if not os.path.exists(file_path):
            return pd.DataFrame()

        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return pd.DataFrame()

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()

# 提取特征
def extract_features(df):
    try:
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['day'] = df['timestamp'].dt.day
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute

        X = df[['year', 'month', 'day', 'hour', 'minute']].values
        y = df['value'].values
        return X, y, df
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None, None, df

# 拟合多项式回归模型
def polynomial_regression(X, y, degree=3):
    try:
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        return model, poly
    except Exception as e:
        print(f"Error training model: {e}")
        return None, None

# 预测
def predict(model, poly, X):
    try:
        X_poly = poly.transform(X)
        return model.predict(X_poly)
    except Exception as e:
        print(f"Error making predictions: {e}")
        return []

def run_prediction_with_history(file_path, topic):
    try:
        df = load_data_from_file(file_path)
        if df.empty:
            return

        # 提取特征并训练多项式回归模型
        X, y, df = extract_features(df)
        if X is None or y is None:
            return

        model, poly = polynomial_regression(X, y, degree=3)
        if model is None or poly is None:
            return

        # 预测历史数据
        predictions = predict(model, poly, X)

        # 预测未来3小时的数据，只预测00分、20分、50分的时间点
        future_timestamps = []
        last_timestamp = df['timestamp'].iloc[-1]
         # 定义目标时间点
        target_minutes = [0, 20, 50]

        # 从最后一个时间戳开始，循环预测未来3小时内的时间点
        for i in range(1, 19):  # 预测未来3小时
            correct_timestamp = last_timestamp + timedelta(minutes=10*i)
    
             # 如果分钟数是0、20、50中的一个，加入预测时间戳
            if correct_timestamp.minute in target_minutes:
                future_timestamps.append(correct_timestamp)
                
        # 提取未来数据特征
        future_data = []
        for ts in future_timestamps:
            future_data.append([ts.year, ts.month, ts.day, ts.hour, ts.minute])

        # 使用已训练的模型预测未来数据
        future_predictions = predict(model, poly, future_data)

        # 合并历史和未来预测结果，检查时间戳冲突并更新预测数据
        save_predictions_to_local(df, predictions, topic, future_timestamps, future_predictions)
    except Exception as e:
        print(f"Error in prediction pipeline: {e}")


import numpy as np
import json
import os

def save_predictions_to_local(df, predictions, topic, future_timestamps=None, future_predictions=None):
    try:
        # 获取保存预测结果的文件路径
        file_path = prediction_save_paths.get(topic)
        if not file_path:
            return

        # 创建保存文件的目录（如果不存在的话）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 读取已有的预测数据
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # 获取历史数据中已存在的时间戳
        existing_timestamps = {item['timestamp'] for item in existing_data}

        # 删除已有数据中时间戳与新数据相同的项
        timestamps_to_remove = {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') for row in df.to_dict('records')}
        existing_data = [item for item in existing_data if item['timestamp'] not in timestamps_to_remove]

        # 保存历史数据的预测结果
        for row, pred in zip(df.to_dict('records'), predictions):
            if isinstance(pred, np.ndarray):
                pred_list = pred.tolist()  # 转换为 Python 列表
            else:
                pred_list = [pred]  # 包装成列表以统一处理

            for p in pred_list:
                existing_data.append({
                    "timestamp": row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    "actual_value": row['value'],
                    "predicted_value": float(p)
                })

        # 添加未来的预测数据（没有实际值，只有预测值）
        for ts, preds in zip(future_timestamps, future_predictions):
            timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')

            if timestamp_str in existing_timestamps:
                # 如果时间戳已存在且实际值为None，则删除该记录，保留实际值的数据
                existing_data = [item for item in existing_data if item['timestamp'] != timestamp_str or item['actual_value'] is not None]

            if timestamp_str not in existing_timestamps:  # 仅在时间戳不存在的情况下添加新的数据
                existing_data.append({
                    "timestamp": timestamp_str,
                    "actual_value": None,  # 没有实际值
                    "predicted_value": float(preds)
                })

        # 按时间戳对数据进行排序
        existing_data.sort(key=lambda x: x['timestamp'])  # 按照时间戳升序排序

        # 保存预测结果到文件
        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=4)

    except Exception as e:
        print(f"Error saving predictions: {e}")



# 定义 HTTP API 路由
@app.route('/api/get_predictions', methods=['GET'])
def get_predictions():
    topic = request.args.get('topic')
    file_path = prediction_save_paths.get(topic)
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "No predictions available for this topic"}), 404

    with open(file_path, "r") as file:
        predictions = json.load(file)
    return jsonify(predictions)

# 启动 MQTT 客户端线程
def start_mqtt_client():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("43.142.99.126", 1883, 60)
    client.subscribe("publish/1111")
    client.loop_forever()

if __name__ == "__main__":
    # 启动 MQTT 客户端线程
    mqtt_thread = threading.Thread(target=start_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=5000)
