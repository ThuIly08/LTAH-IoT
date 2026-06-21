import json
import os
import time
from datetime import timezone, datetime

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
#processor - mqtt -> influxdb: nhân message từ mqtt rồi lưu vào db influxdb

#khai báo giá trị mặc định của biến môi trường
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
#topic # - lắng nghe toàn bộ message từ docker
MQTT_TOPIC = os.getenv('MQTT_TOPIC','#')

#khai báo biến liên quan influx fb
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'iot-token-123')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'iot-lab')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'iot_data')

#chuyển đổi chuỗi timestampt (2024-01-01T00:00:00Z)  thành object datetime
#trả về none nếu chuỗi rỗng hoặc lỗi
def parse_timestamp(timestamp_text):
    if not timestamp_text:
        return None
    try:
        normalized = timestamp_text.replate('Z', '+00:00')
        return datetime.fromisoformat(normalized)
    except Exception:
        return None

#ánh xạ tên mqtt topic sang tên bảng trong influxDB
def get_measurement_name(topic):
    if topic == 'iot/sensors':
        return 'sensor_data'
    if topic == 'system/info':
        return 'system_info'
    return 'mqtt_data'

#chuyển đổi 1 message json sang 1 influxDB Point (Định dạng để ghi vào db)
#gắn tag device_id và topic, duyệt qua từng field trong data để thêm vào point, trả về point nếu k có field hợp lệ
def create_point(topic, data):
    measurement = get_measurement_name(topic)
    device_id = str(data.get('device_id', 'unknown'))

    point = Point(measurement)
    point = point.tag('device_id', device_id)
    point = point.tag('topic', topic)

    timestamp = parse_timestamp(data.get('timestamp'))
    if timestamp is not None:
        point = point.time(timestamp, WritePrecision.NS)

    field_count = 0
    
    for key, value in data.items():
        if key in ['device_id', 'timestamp']:
            continue
        if isinstance(value, bool):
            point = point.field(key, value)
            field_count +=1
        elif isinstance(value, int):
            point = point.field(key, value)
            field_count +=1
        elif isinstance(value, float):
            point = point.field(key, value)
            field_count +=1
        elif isinstance(value, str):
            point = point.field(key, value)
            field_count +=1
    
    if field_count == 0:
        return None
    return point

#cổng kết nối đến influxdb - rety mỗi 5s
def connect_influxdb():
    while True: 
        try:
            client = InfluxDBClient(
                url = INFLUXDB_URL,
                token = INFLUXDB_TOKEN,
                org=INFLUXDB_ORG
            )
            health = client.health()
            print(f'InfluxDB health: {health.status}')
            write_api = client.write_api()
            return write_api
        except Exception as exc:
            print(f'Cannot connect to InfluxDB: {exc}')
            print('Retrying in 5 seconds ...')
            time.sleep(5)
#write_api để ghi dữ liệu            
write_api = connect_influxdb()

#callback được gọi mỗi khi mqtt kết nối thành công, subscribe vào topic đã cấu hình (#)
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT broker.')
        client.subscribe(MQTT_TOPIC)
        print(f'Subscribed to topic: {MQTT_TOPIC}')
    else:
        print(f'Failed to connect to MQTT broker. Return code: {rc}')

#callback được gọi mỗi khi nhận message mqtt
#giải mã json -> tạo influxDB point -> ghi vào db
def on_message(client, userdata, message):
    topic = message.topic

    try:
        payload_text = message.payload.decode('utf-8')
        data = json.loads(payload_text)
        point = create_point(topic, data)
        
        if point is None:
            print(f'Skipped message without valid fields: {payload_text}')
            return
        
        write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

        print(f'Written to InfluxDB: topic = {topic}, payload={payload_text}')

    except Exception as exc:
        print(f'Failed to process message from topic {topic}:{exc}')

def main():
    mqtt_client = mqtt.Client(client_id = 'iot-data-processor')
    mqtt_client.on_connect = on_connect #khai báo callback mỗi khi connect thành công
    mqtt_client.on_message = on_message #khai báo callback mỗi khi gửi mesage thành công

#khới tạo mqtt client, kết nối broker -> chạy loop_forever() để nhanaj mesage liên tục
    while True:
        try:
            print(f'Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} ...')
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive = 60)
            mqtt_client.loop_forever()
        except Exception as exc:
            print(f'MQTT connection error: {exc}')
            print('Retrying in 5 seconds')
            time.sleep(5)

if __name__ == '__main__':
    main()