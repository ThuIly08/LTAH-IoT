import paho.mqtt.client as mqtt, json   # paho: thư viện MQTT đa năng (không riêng cho ThingsBoard); json: mã hóa/giải mã dữ liệu
TOKEN = "BwSjMFeqmy3wEePhjtTt" #access token của thiết bị trên thingsboard (vừa là mật khẩu, vừa là danh tính thiết bị)
REQ = "v1/devices/me/rpc/request/+"  # topic nhận lệnh RPC; "me" = chính thiết bị này (ThingsBoard tự biết nhờ token); "+" = khớp mọi request_id
light = False   # trạng thái đèn hiện tại (False=tắt, True=bật); dashboard sẽ đọc/ghi giá trị này
def on_msg(c, u, m): #callback mỗi khi có lệnh gọi tới (paho TỰ gọi & tự truyền c=client, u=userdata, m=message)
 global light
 rid = m.topic.split('/')[-1] #request_id tách từ topic — phần tử cuối sau split('/')
 cmd = json.loads(m.payload)
 method = cmd["method"]
 print(f"topic request/{rid} - lệnh: ", method, cmd.get("params"))
 # thực thi hành động theo loại lệnh:
 if method == "setLight":        # nút Power gạt -> ĐẶT trạng thái đèn (params = true/false)
  light = cmd["params"]
 elif method == "getLight":      # LED indicator hỏi -> chỉ ĐỌC, không đổi gì
  pass                          # không làm gì thêm, chỉ trả light hiện tại ở dưới
 resp = f"v1/devices/me/rpc/response/{rid}"
 c.publish(resp, json.dumps(light))     # trả trạng thái đèn (true/false) về cho server/LED qua RPC response
 c.publish("v1/devices/me/telemetry", json.dumps({"light": light}))


c = mqtt.Client() #mở 1 mqtt client
c.username_pw_set(TOKEN)  # đăng nhập vào broker VỚI TƯ CÁCH là thiết bị này: username=token, password để trống. ThingsBoard quy định dùng token làm username
c.on_message = on_msg  # GÁN hàm (không có dấu ()), tức trao hàm cho paho giữ; paho gọi lại khi có tin nhắn (cơ chế callback)
c.connect("thingsboard.cloud", 1883)  # kết nối broker MQTT của ThingsBoard, cổng 1883 (phải gọi SAU username_pw_set)
c.subscribe(REQ)  # đăng ký lắng nghe topic nhận lệnh
c.loop_forever() #giữ chương trình chạy chờ lệnh