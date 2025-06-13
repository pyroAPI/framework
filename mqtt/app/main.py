import paho.mqtt.client as mqtt
from app.router import handle_message
from config.settings import MQTT_BROKER, MQTT_PORT

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe("#")  # Subscribe to all topics (or specific ones)

def on_message(client, userdata, msg):
    handle_message(msg.topic, msg.payload)

def run_mqtt_server():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
