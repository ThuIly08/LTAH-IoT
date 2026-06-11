"""
File này gửi dữ liệu telemetry (nhiệt độ giả lập) lên ThingsBoard Cloud qua MQTT.
Luồng: kết nối bằng token → sinh nhiệt độ ngẫu nhiên → gửi lên cloud → lặp lại mỗi 2 giây.
"""

# Thư viện MQTT, json để đóng gói dữ liệu, time để tạo delay, random để sinh số ngẫu nhiên
import paho.mqtt.client as mqtt
import json, time, random

# Access token của thiết bị trên ThingsBoard (lấy từ bước provisioning hoặc tạo thủ công)
TOKEN = "BwSjMFeqmy3wEePhjtTt"

# Topic chuẩn của ThingsBoard để nhận dữ liệu telemetry từ thiết bị
TOPIC = "v1/devices/me/telemetry"

# Khởi tạo MQTT client
c = mqtt.Client()

# Dùng token làm username để xác thực thiết bị (ThingsBoard không cần password)
c.username_pw_set(TOKEN)

# Kết nối tới ThingsBoard Cloud qua cổng 1883
c.connect("thingsboard.cloud", 1883)

# Chạy vòng lặp MQTT ở background để duy trì kết nối (không block luồng chính)
c.loop_start()

# Vòng lặp vô hạn: liên tục sinh và gửi dữ liệu
while True:
    # Sinh nhiệt độ ngẫu nhiên trong khoảng 24–30°C, làm tròn 1 chữ số thập phân
    data = {"temperature": round(random.uniform(24, 30), 1)}

    # Gửi dữ liệu lên ThingsBoard dưới dạng JSON
    c.publish(TOPIC, json.dumps(data))

    # In ra terminal để theo dõi
    print("sent", data)

    # Chờ 2 giây trước khi gửi lần tiếp theo
    time.sleep(2)
