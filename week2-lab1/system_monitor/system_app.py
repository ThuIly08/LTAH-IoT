import json
import os
import socket
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psutil

#khai báo giá trị mặc định cho các biến môi trường
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC','system/info')
DEVICE_ID = os.getenv('DEVICE_ID', 'system-monitor-01')
PUBLISH_INTERVAL = float(os.getenv('PUBLISH_INTERVAL', '5'))

#thu thập thông tin hệ thống hiện tiện bằng thư viện psutil, đóng gói thành 1 dick json
def create_system_info(): 
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk=psutil.disk_usage("/")

    return {
    "device_id": DEVICE_ID,
    "hostname": socket.gethostname(),
    "cpu_percent": cpu_percent,
    "memory_percent": memory.percent,
    "memory_used_mb": round(memory.used / (1024 * 1024), 2),
    "memory_total_mb": round(memory.total / (1024 * 1024), 2),
    "disk_percent": disk.percent,
    "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
    "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
    "timestamp": datetime.now(timezone.utc).isoformat()
}

#tạo mqtt_client và kết nối đến broker. Nếu kết nối thất bại thì tự động retry trong 5s cho đến khi thành công
#trả về client đã kết nối
def connect_mqtt_client():
    client = mqtt.Client(client_id = DEVICE_ID)

#giải thích while True: try except: 
#code trong try chạy bthg -> except bị bỏ qua, code trong try gặp lỗi -> nhảy xuống except để xử lý
    while True: 
        try:
            print(f'connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}...')
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive = 60)
            print('Connected to Mqtt Broker.')
            return client
        except Exception as exc:
            print(f'Connection failed: {exc}')
            print('retrying in 5 secconds...')
            time.sleep(5)

#vòng lặp chính của chương trình, kết nối mqtt broker. cứ mỗi publish_interval giây (mặc định 5s)
#gọi create_system_info()->serialize json (chuyển đổi dữ liệu (object/dict) thành chuỗi văn bản JSON) -> publish lên topic mqtt
#nếu xảy ra lỗi runtime, tự động recoonect
def main():
    client = connect_mqtt_client()
    print(f'Connecting to Mqtt broker at {MQTT_BROKER}:{MQTT_PORT}...')

    while True:
        try:
            data = create_system_info()
            payload = json.dumbs(data)
            result = client.publish(MQTT_TOPIC, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f'Published: {payload}')
            else: print(f'Failed to publish message. Error code: {result.rc}')
            time.sleep(PUBLISH_INTERVAL)
        except Exception as exc:
            print(f'Runtime error: {exc}')
            client = connect_mqtt_client()

#__name__ là 1 biến đặc biệt của python, python tự động gán giá trị cho __name__ dựa trên cách file được chạy:
#chạy trực tiếp file -> giá trị của __name__ là __main__; nếu được import từ file khác thì name là 'symtem_app' (tên file)
if __name__ == '__main__':
    main()
