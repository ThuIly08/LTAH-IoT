import json
import os
import random
import time
from datetime import datetime, timezone
#datetime, timezone nằm trong module datetime của python

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost') #địa chỉ của mqtt_broker: mặc định là localhost
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883')) #os.getenv trả về string, dùng int(...) để ép về kiểu số nguyên
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'iot/power') #topic riêng cho dữ liệu công suất điện
DEVICE_ID = os.getenv('DEVICE_ID', 'power-meter-01') #mã định danh cho đồng hồ đo điện
PUBLISH_INTERVAL = float(os.getenv('PUBLISH_INTERVAL', '2'))

#điện áp danh định (V): lưới điện dân dụng Việt Nam là 220V
NOMINAL_VOLTAGE = float(os.getenv('NOMINAL_VOLTAGE', '220'))

#Trong python, sau khi khai báo hàm với dấu : ở cuối,
#tất cả các dòng thuộc thân hàm phải được thụt vào trong (thường là 4 dấu cách)
def create_power_data():
    #tạo giá trị mô phỏng cho đồng hồ đo công suất điện
    voltage = round(random.uniform(215.0, 225.0), 2)   #điện áp (V), dao động quanh mức danh định 220V
    current = round(random.uniform(0.5, 10.0), 2)      #dòng điện (A)
    power_factor = round(random.uniform(0.85, 1.0), 2) #hệ số công suất (cos phi), nằm trong khoảng 0..1

    #công suất tiêu thụ thực tế P = U * I * cos(phi), đơn vị watt (W)
    #làm tròn 2 chữ số cho gọn
    power = round(voltage * current * power_factor, 2)

    frequency = round(random.uniform(49.9, 50.1), 2)   #tần số lưới điện (Hz), chuẩn VN là 50Hz

    #trong dictionary (từ điển) phải dùng dấu , chứ không phải dấu ;
    #dictionary là 1 kiểu dữ liệu trong Python để lưu trữ dữ liệu theo dạng cặp key: value
    data = {
        'device_id': DEVICE_ID,
        'voltage': voltage,           #điện áp (V)
        'current': current,           #dòng điện (A)
        'power': power,               #công suất tiêu thụ (W)
        'power_factor': power_factor, #hệ số công suất
        'frequency': frequency,       #tần số (Hz)
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    return data

def main(): #định nghĩa hàm main, là hàm điều chỉnh toàn bộ luồng chạy của chương trình (kết nối -> tạo dữ liệu -> gửi đi)
    #tạo 1 mqtt client
    client = mqtt.Client(client_id=DEVICE_ID)
    #in thông báo ra màn hình nhờ f-string - cho phép chèn giá trị biến vào trong {...}
    print(f'Connecting to mqtt broker at {MQTT_BROKER}:{MQTT_PORT}...')
    #thực hiện kết nối tới broker, mở kết nối 60s, nếu trong 60s không có dữ liệu trao đổi, client sẽ ping để báo 'tôi vẫn sống',
    #nếu broker không nhận được -> coi như client mất kết nối
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    #khởi động network loop chạy nền: hoàn tất bắt tay kết nối và giữ kết nối sống
    #(xử lý ping/keepalive, gửi/nhận gói tin). Thiếu dòng này, publish sẽ báo lỗi rc=4 (NO_CONN)
    client.loop_start()

    print(f"Publishing data to topic: {MQTT_TOPIC}")

    while True:
        data = create_power_data()
        payload = json.dumps(data)

        result = client.publish(MQTT_TOPIC, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f'Published: {payload}')
        else:
            print(f'Failed to publish message. Error code: {result.rc}')

        time.sleep(PUBLISH_INTERVAL)

if __name__ == '__main__':
    main()
