#include<Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Wi-Fi credentials
const char* ssid = "POCO";
const char* password = "00000000";

// MQTT broker (use your laptop's IP on the hotspot)
const char* mqtt_server = "192.168.73.79";  // Replace this with broker IP

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(100);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi.");
  }
}

void reconnect() {
  // Loop until reconnected
  while (!client.connected()) {
    Serial.print("Connecting to MQTT... ");
    if (client.connect("ESP32Client")) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Booting...");
  setup_wifi();

  Serial.print("Setting MQTT server to ");
  Serial.println(mqtt_server);
  client.setServer(mqtt_server, 1883);
  randomSeed(analogRead(0));
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost. Reconnecting...");
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  float temp = random(200, 350) / 10.0;
  String payload = "{\"temperature\": " + String(temp, 1) + "}";

  Serial.print("Publishing: ");
  Serial.println(payload);

  boolean sent = client.publish("sensor/temperature", payload.c_str());

  if (sent) {
    Serial.println("Message published successfully.");
  } else {
    Serial.println("Failed to publish message.");
  }

  delay(5000);
}
