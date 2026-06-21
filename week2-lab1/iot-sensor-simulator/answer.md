# 14. Câu hỏi báo cáo

## 1. MQTT broker có vai trò gì trong hệ thống IoT?

MQTT broker là **máy chủ trung gian** đứng giữa các thiết bị. Mọi thiết bị không gửi dữ liệu trực tiếp cho nhau mà gửi qua broker. Broker nhận message từ bên gửi (publisher) theo từng *topic*, rồi chuyển tiếp đến tất cả các bên đã đăng ký nhận (subscriber) của topic đó. Nhờ vậy thiết bị gửi và thiết bị nhận **không cần biết về nhau** (giảm phụ thuộc), dễ mở rộng số lượng thiết bị, và quản lý kết nối tập trung tại một chỗ.

## 2. Sự khác nhau giữa MQTT publisher và MQTT subscriber là gì?

- **Publisher (bên xuất bản):** gửi/đẩy dữ liệu *lên* broker theo một topic. Trong lab này, `app.py` đóng vai trò publisher — nó tạo dữ liệu cảm biến và `publish` lên topic `iot/sensors`.
- **Subscriber (bên đăng ký):** *đăng ký* một topic và *nhận* mọi message được publish lên topic đó.

Một thiết bị có thể vừa là publisher vừa là subscriber. Điểm khác nhau cốt lõi: publisher **gửi đi**, subscriber **nhận về**.

## 3. Vì sao cần dùng Docker container để đóng gói ứng dụng IoT?

- **Đồng nhất môi trường:** container đóng gói sẵn code + thư viện + cấu hình, nên chạy ở máy nào cũng giống nhau, tránh lỗi "máy tôi chạy được mà máy bạn không".
- **Cô lập:** mỗi service (broker, sensor) chạy trong container riêng, không xung đột thư viện/hệ điều hành.
- **Dễ triển khai & mở rộng:** chỉ cần một lệnh để bật/tắt/nhân bản nhiều sensor.
- **Gọn nhẹ & nhanh** hơn máy ảo vì chia sẻ chung nhân hệ điều hành.

## 4. Trong lệnh chạy broker, tham số `-p 1883:1883` có ý nghĩa gì?

`-p` là *port mapping* (ánh xạ cổng) giữa máy thật và container, theo dạng `-p <cổng máy thật>:<cổng trong container>`. `1883:1883` nghĩa là chuyển tiếp cổng **1883 của máy host** vào **cổng 1883 bên trong container** (1883 là cổng mặc định của MQTT). Nhờ đó ứng dụng bên ngoài container có thể kết nối tới broker qua `localhost:1883`.

## 5. Trong lệnh chạy sensor container, vì sao `MQTT_BROKER` được đặt là `mqtt-broker` thay vì `localhost`?

Vì khi chạy trong Docker, mỗi container có mạng riêng. Với một container, `localhost` chỉ về **chính nó**, không phải broker. Khi các container nằm chung một Docker network, Docker có DNS nội bộ cho phép gọi nhau bằng **tên service/tên container**. `mqtt-broker` chính là tên của container broker, nên sensor container phải dùng tên đó để Docker phân giải ra đúng địa chỉ của broker.

## 6. Docker network `iot-net` có vai trò gì?

Nó tạo một **mạng ảo riêng** để các container (broker và sensor) cùng tham gia. Trong mạng này, các container có thể:
- **Gọi nhau bằng tên** thay vì IP (nhờ DNS nội bộ của Docker).
- **Giao tiếp trực tiếp và cô lập** với các container/mạng khác (an toàn hơn).

## 7. Nếu không dùng Docker network riêng, sensor container có thể kết nối đến broker bằng tên `mqtt-broker` không? Giải thích.

**Không.** Việc phân giải tên container thành địa chỉ chỉ hoạt động khi các container ở chung một *user-defined network*. Mạng `bridge` mặc định của Docker **không có tính năng DNS tự động theo tên**. Nếu không tạo network riêng, sensor sẽ không hiểu `mqtt-broker` là gì và sẽ báo lỗi không phân giải được tên → kết nối thất bại.

## 8. Vì sao chương trình Python nên cấu hình từ biến môi trường thay vì hard-code trong source code?

- **Linh hoạt:** đổi địa chỉ broker, port, topic, chu kỳ gửi... mà **không phải sửa và build lại code**.
- **Tách cấu hình khỏi code:** cùng một image chạy được ở nhiều môi trường (dev/test/prod) chỉ bằng cách đổi biến môi trường.
- **An toàn:** thông tin nhạy cảm (mật khẩu, địa chỉ) không bị ghi cứng trong source.
- Đúng tinh thần của Docker/12-factor app. Trong `app.py`, ví dụ `os.getenv('MQTT_BROKER', 'localhost')` đọc cấu hình từ môi trường, có giá trị mặc định khi không được đặt.

## 9. Nếu muốn thay đổi chu kỳ gửi dữ liệu từ 2 giây sang 10 giây mà không sửa code, cần làm gì?

Đặt **biến môi trường** `PUBLISH_INTERVAL=10` khi chạy container (hoặc trong file docker-compose). Vì code đã đọc `PUBLISH_INTERVAL = float(os.getenv('PUBLISH_INTERVAL', '2'))`, nó sẽ tự lấy giá trị 10 mà không cần đụng đến source.

Ví dụ: `docker run -e PUBLISH_INTERVAL=10 ...` hoặc trong compose:
```yaml
environment:
  - PUBLISH_INTERVAL=10
```

## 10. Trong hệ thống IoT thật, vì sao không nên để `allow_anonymous true` cho MQTT broker?

`allow_anonymous true` cho phép **bất kỳ ai cũng kết nối được broker mà không cần đăng nhập**. Trong môi trường thật, điều này nguy hiểm:
- Kẻ xấu có thể **đọc trộm** dữ liệu cảm biến (subscribe topic).
- Có thể **gửi dữ liệu giả** lên topic, gây sai lệch/điều khiển sai thiết bị.
- Có thể làm **quá tải** broker (tấn công).

Hệ thống thật nên bật xác thực (username/password hoặc chứng chỉ TLS) và phân quyền theo topic. `allow_anonymous true` chỉ nên dùng khi **học/thử nghiệm** trong mạng nội bộ.

## 11. Ứng dụng IoT riêng của bạn publish dữ liệu lên topic nào? Vì sao bạn chọn topic đó?

Ứng dụng publish lên topic **`iot/sensors`** (cấu hình qua biến `MQTT_TOPIC`). Chọn topic này vì tên có **cấu trúc phân cấp rõ ràng** (`iot/sensors`): nhóm `iot` cho toàn hệ thống, nhánh `sensors` cho dữ liệu cảm biến. Cách đặt tên này giúp dễ mở rộng và lọc sau này (ví dụ `iot/sensors/temperature`, `iot/actuators/...`), đồng thời subscriber dễ đăng ký theo wildcard (`iot/#`).

## 12. Ứng dụng IoT riêng của bạn gửi những trường dữ liệu nào trong JSON message?

JSON message gồm 4 trường:

| Trường | Ý nghĩa |
|--------|---------|
| `device_id` | Mã định danh thiết bị gửi (vd `sensor-01`) — để biết dữ liệu từ thiết bị nào |
| `temperature` | Nhiệt độ mô phỏng (°C) |
| `humidity` | Độ ẩm mô phỏng (%) |
| `timestamp` | Thời điểm tạo dữ liệu, theo chuẩn ISO 8601 (UTC) |

## 13. Vai trò của thư viện `psutil` là gì trong ứng dụng gửi thông tin hệ thống?

`psutil` (Python System and Process Utilities) là thư viện dùng để **lấy thông tin tài nguyên hệ thống** như: phần trăm sử dụng CPU, dung lượng RAM, ổ đĩa, mạng, tiến trình đang chạy... Trong một ứng dụng gửi thông tin hệ thống, `psutil` đảm nhận việc **thu thập các chỉ số phần cứng/hệ điều hành**, sau đó dữ liệu này được đóng gói (JSON) và publish lên broker.

> Lưu ý: ứng dụng sensor trong lab này dùng `paho-mqtt` để giao tiếp MQTT và `random` để **mô phỏng** dữ liệu, chưa dùng `psutil`. `psutil` chỉ cần khi muốn gửi số liệu thật của máy.

## 14. Khi chạy ứng dụng IoT riêng trong container, vì sao vẫn cần đặt `MQTT_BROKER=mqtt-broker`?

Vì ứng dụng chạy trong container của nó, `localhost` (giá trị mặc định trong code) sẽ trỏ về chính container đó chứ không phải broker. Để kết nối được tới container broker, ta phải **trỏ đúng tới tên service/container của broker** trong cùng Docker network — đó là `mqtt-broker`. Vì vậy phải đặt `MQTT_BROKER=mqtt-broker` để ghi đè giá trị mặc định `localhost`, giúp Docker DNS phân giải đúng địa chỉ broker.
