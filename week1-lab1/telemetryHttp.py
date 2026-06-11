"""
File này gửi dữ liệu telemetry (nhiệt độ giả lập) lên ThingsBoard Cloud qua HTTP REST API.
Luồng: tạo URL từ token → sinh nhiệt độ ngẫu nhiên → POST lên cloud → lặp lại mỗi 2 giây.

Khác với telemetryMqtt.py (dùng giao thức MQTT), file này dùng HTTP — mỗi lần gửi là 1 request độc lập, không duy trì kết nối liên tục.
"""

# requests để gửi HTTP, time để tạo delay, random để sinh số ngẫu nhiên
import requests, time, random

# Access token của thiết bị trên ThingsBoard
TOKEN = "BwSjMFeqmy3wEePhjtTt"

# URL endpoint REST API của ThingsBoard để nhận telemetry — token nằm thẳng trong URL
URL = ("https://thingsboard.cloud"
       f"/api/v1/{TOKEN}/telemetry")

# Vòng lặp vô hạn: liên tục sinh và gửi dữ liệu
while True:
    # Sinh nhiệt độ ngẫu nhiên trong khoảng 24–30°C, làm tròn 1 chữ số thập phân
    data = {"temperature": round(random.uniform(24, 30), 1)}

    # Gửi HTTP POST kèm data dạng JSON lên ThingsBoard
    r = requests.post(URL, json=data)

    # In HTTP status code (200 = thành công) và data vừa gửi để theo dõi
    print(r.status_code, data)

    # Chờ 2 giây trước khi gửi lần tiếp theo
    time.sleep(2)
