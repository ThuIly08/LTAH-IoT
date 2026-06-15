import requests
BASE = "https://thingsboard.cloud"
# 1) đăng nhập lấy token
r = requests.post(f"{BASE}/api/auth/login",
 json={"username": "hoangminhthu668@gmail.com",
 "password": "@Thu12345"})        
data = r.json()
if "token" not in data:              
 raise SystemExit(f"Đăng nhập thất bại ({r.status_code}): {data}")
jwt = data["token"]
h = {"X-Authorization": f"Bearer {jwt}"}
# 2) gửi lệnh RPC two-way (chờ thiết bị trả lời rồi nhận kết quả về)
dev = "436a7e10-658e-11f1-8152-99343c4bf5a3"
body = {"method": "setLight", "params": True}
resp = requests.post(f"{BASE}/api/rpc/twoway/{dev}",
 json=body, headers=h)
print("đã gửi lệnh, status:", resp.status_code)  # 200 = OK, 401 = sai token, 403 = sai quyền/device id, 504 = device chưa chạy (timeout)
if resp.status_code == 200:
 print("thiết bị trả lời:", resp.text)  # nội dung device publish về, vd: {"ok": true}
else:
 print("chi tiết lỗi:", resp.text)   # in lý do nếu thất bại