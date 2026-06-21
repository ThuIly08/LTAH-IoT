import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost') #địa chỉ của mqtt_broker: mặc định là localhost
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC','iot/sensors')
DEVICE_ID = os.getenv('DEVICE_ID', 'sensor-01')
PUBLIST_INTERVAL = float(os.getenv('PUBLISH_INTERVAL', '2'))