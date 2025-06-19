from app.handlers import device, sensor

ROUTES = {
    "device/register": device.register_device,
    "sensor/temperature": sensor.handle_temperature,
    "test/topic": sensor.handle_test,  # Add this line

}

def handle_message(topic, payload):
    handler = ROUTES.get(topic)
    if handler:
        handler(payload.decode())
    else:
        print(f"No handler for topic: {topic}")

