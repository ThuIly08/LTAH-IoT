"""
File này thực hiện Device Provisioning: đăng ký thiết bị vào device profile
đã khai báo trên thingsboard.cloud và lấy về access token để dùng cho các lần kết nối sau.
"""

# Thư viện MQTT để giao tiếp với broker, json để xử lý dữ liệu
import paho.mqtt.client as mqtt, json

# Địa chỉ server ThingsBoard Cloud
HOST = "thingsboard.cloud"

# Thông tin đăng ký thiết bị: tên thiết bị, key và secret từ ThingsBoard
req = {
    "deviceName": "my-device-01",
    "provisionDeviceKey": "8d6dku3e647941ziyr1x",
    "provisionDeviceSecret": "ixdiqmwixffzrw0wplq9"
}

# Hàm callback được gọi khi nhận được tin nhắn từ broker
def on_msg(c, u, m):
    # Giải mã payload JSON từ server trả về
    res = json.loads(m.payload)
    # In toàn bộ response để debug, sau đó lấy token nếu thành công
    print("FULL RESPONSE =", res)
    if "credentialsValue" in res:
        print("TOKEN =", res["credentialsValue"])
    else:
        print("LỖI:", res.get("errorMsg") or res.get("status") or res)

# Khởi tạo MQTT client
c = mqtt.Client()

# Đặt username là "provision" (yêu cầu của ThingsBoard khi dùng provisioning)
c.username_pw_set("provision")

# Gán hàm xử lý tin nhắn nhận được
c.on_message = on_msg

# Kết nối tới broker ThingsBoard qua cổng 1883 (MQTT không mã hoá)
c.connect(HOST, 1883)

# Đăng ký nhận tin nhắn từ topic phản hồi của provisioning
c.subscribe("/provision/response")

# GỬI yêu cầu cấp phát lên topic request (publish ≠ subscribe: đây là GỬI, không phải lắng nghe)
c.publish("/provision/request", json.dumps(req))

# Giữ chương trình chạy liên tục để lắng nghe phản hồi từ server
c.loop_forever()
