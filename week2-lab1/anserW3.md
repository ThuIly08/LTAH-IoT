# Trả lời câu hỏi - Week 2 Lab

**1. Docker Compose khác gì so với việc chạy nhiều lệnh `docker run` riêng lẻ?**

`docker run` phải gõ từng lệnh cho từng container, quản lý thủ công thứ tự khởi động, network và biến môi trường. Docker Compose khai báo tất cả trong một file `docker-compose.yml` và khởi chạy toàn bộ hệ thống bằng một lệnh `docker compose up`, tự động tạo network nội bộ giữa các container.

---

**2. Trong `docker-compose.yml`, vì sao service sensor dùng `MQTT_BROKER: mosquitto` thay vì `localhost`?**

Bên trong Docker, mỗi container là một máy riêng biệt. `localhost` sẽ trỏ về chính container đó, không phải container mosquitto. Docker Compose tự tạo DNS nội bộ, cho phép các container tìm thấy nhau qua tên service — vì vậy dùng `mosquitto` thay vì `localhost`.

---

**3. Vai trò của processor trong IoT stack là gì?**

Processor đóng vai trò **trung gian xử lý dữ liệu**: subscribe toàn bộ message từ MQTT broker, parse JSON, chuyển đổi thành định dạng InfluxDB Point rồi ghi vào database. Tách biệt việc thu thập dữ liệu (sensor) khỏi việc lưu trữ (InfluxDB).

---

**4. Vì sao dữ liệu sensor nên được lưu vào time-series database?**

Dữ liệu sensor gắn liền với thời gian và được ghi liên tục với tần suất cao. Time-series database như InfluxDB được tối ưu cho việc ghi/đọc theo mốc thời gian, nén dữ liệu hiệu quả, và truy vấn theo khoảng thời gian — khác với database quan hệ thông thường vốn không được thiết kế cho loại dữ liệu này.

---

**5. InfluxDB bucket là gì?**

Bucket là đơn vị lưu trữ trong InfluxDB 2.x, tương đương với "database" trong các hệ quản trị CSDL thông thường. Mỗi bucket chứa các measurement (bảng dữ liệu), có thể cấu hình thời gian giữ dữ liệu (retention policy), và được phân quyền truy cập độc lập.

---

**6. Trong Grafana, vì sao URL của InfluxDB phải là `http://influxdb:8086`?**

Grafana chạy trong container riêng, không thể dùng `localhost` để trỏ đến InfluxDB vì `localhost` là chính container Grafana. Docker Compose tạo DNS nội bộ nên các container tìm thấy nhau qua tên service — `influxdb` là tên service khai báo trong `docker-compose.yml`.

---

**7. Docker volume `influxdb-data` có vai trò gì?**

Lưu trữ dữ liệu của InfluxDB bên ngoài vòng đời container. Khi container bị xóa hoặc restart, dữ liệu vẫn còn nguyên trong volume. Không có volume, mọi dữ liệu sẽ mất khi container dừng.

---

**8. Nếu xóa container InfluxDB nhưng giữ volume, dữ liệu có mất không? Giải thích.**

**Không mất.** Volume tồn tại độc lập với container — xóa container chỉ xóa lớp runtime, không xóa volume. Khi tạo lại container InfluxDB và mount cùng volume đó, toàn bộ dữ liệu cũ sẽ được phục hồi.

---

**9. Nếu muốn thêm một sensor mới, em sẽ sửa hệ thống như thế nào?**

Tạo thư mục mới cho sensor (ví dụ `iot-electric-power/`), viết `app.py` publish data lên MQTT topic riêng, viết `Dockerfile`, rồi thêm service mới vào `docker-compose.yml` với `MQTT_BROKER=mosquitto`. Chạy lại `docker compose up -d --build` để khởi động service mới — Docker chỉ build thêm service mới, các service đang chạy không bị ảnh hưởng. Processor tự nhận vì đang subscribe topic `#` (tất cả), không cần sửa thêm gì.

---

**10. Trong hệ thống thật, vì sao không nên dùng token và password đơn giản như trong bài lab?**

Token `iot-token-123` và password `admin123` quá dễ đoán, dễ bị tấn công brute-force hoặc lộ qua log. Trong thực tế cần dùng token ngẫu nhiên độ dài cao, lưu trong secret manager (không hardcode trong file), phân quyền tối thiểu (mỗi service chỉ có quyền vừa đủ), và thay định kỳ.

---

Trong bài thực hành này, sinh viên đã triển khai một IoT stack đa dịch vụ bằng Docker Compose. Hệ thống bao gồm MQTT broker, các publisher giả lập dữ liệu, data processor, InfluxDB và Grafana. Đây là bước chuyển quan trọng từ việc chạy container đơn lẻ sang triển khai một hệ thống IoT gồm nhiều dịch vụ có khả năng giao tiếp, lưu trữ và trực quan hóa dữ liệu.
