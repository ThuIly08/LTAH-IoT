# Docker Compose - Week 2 Lab 1

## Tổng quan

File `docker-compose.yml` khởi chạy toàn bộ hệ thống IoT gồm 5 container cùng lúc bằng một lệnh duy nhất `docker-compose up --build`. Các container giao tiếp với nhau qua mạng nội bộ Docker, dùng tên service thay cho `localhost`.

Luồng dữ liệu:
```
iot-sensor-simulator ──┐
                        ├──► mosquitto ──► processor ──► influxdb
system-monitor ─────────┘
```

---

## Chi tiết từng service

### mosquitto
- **Image:** `eclipse-mosquitto:2` (dùng sẵn, không cần build)
- **Vai trò:** MQTT broker — trung gian nhận và phân phối message giữa các service
- **Cổng:** `1883` mở ra ngoài để có thể test bằng MQTT client trên máy host
- **Config:** mount file `./mosquitto/config/mosquitto.conf` vào container, cho phép kết nối ẩn danh

### influxdb
- **Image:** `influxdb:2.7` (dùng sẵn, không cần build)
- **Vai trò:** Database lưu time-series data (dữ liệu cảm biến theo thời gian)
- **Cổng:** `8086` — có thể truy cập giao diện web tại `http://localhost:8086`
- **Khởi tạo tự động:** tạo sẵn org `iot-lab`, bucket `iot_data`, token `iot-token-123` qua biến môi trường
- **Volume:** `influxdb_data` giữ dữ liệu không bị mất khi container bị xóa

### iot-sensor-simulator
- **Build:** từ `./iot-sensor-simulator/Dockerfile`
- **Vai trò:** giả lập cảm biến IoT, định kỳ publish data lên MQTT broker
- **Phụ thuộc:** chờ `mosquitto` khởi động trước

### system-monitor
- **Build:** từ `./system_monitor/Dockerfile`
- **Vai trò:** đọc chỉ số CPU, RAM, disk của chính container rồi publish lên topic `system/info`
- **Biến môi trường đáng chú ý:** `PUBLISH_INTERVAL=5` — gửi dữ liệu mỗi 5 giây
- **Phụ thuộc:** chờ `mosquitto` khởi động trước

### processor
- **Build:** từ `./processor/Dockerfile`
- **Vai trò:** subscribe toàn bộ topic (`#`), nhận message từ hai simulator, xử lý và ghi vào InfluxDB
- **Phụ thuộc:** chờ cả `mosquitto` lẫn `influxdb` khởi động trước

---

## Ghi chú kỹ thuật

**Tên service thay cho localhost** — trong biến môi trường các container dùng `MQTT_BROKER=mosquitto` và `INFLUXDB_URL=http://influxdb:8086` vì Docker tự tạo DNS nội bộ, mỗi service được resolve theo đúng tên khai báo.

**`depends_on` không đảm bảo service đã sẵn sàng** — chỉ đảm bảo container đã *start*, không đảm bảo ứng dụng bên trong đã *ready*. Vì vậy các service đều có vòng lặp retry trong code Python.

**`docker-compose.yml` chỉ là file khai báo cấu hình** — nói cho Docker biết cần chạy container nào, dùng image gì, biến môi trường và thứ tự khởi động ra sao. Bản thân file không chạy gì cả, Docker đọc rồi tự lo phần còn lại.
