FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY system_app.py .

#khai báo các biến môi trường
ENV MQTT_BROKER=localhost \
    MQTT_PORT=1883 \
    MQTT_TOPIC=system/info \
    DEVICE_ID=system-monitor-01 \
    PUBLISH_INTERVAL=5

CMD ["python", "system_app.py"]
