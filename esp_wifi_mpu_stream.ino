// esp_wifi_mpu_stream.ino
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

#define SDA_PIN 8
#define SCL_PIN 9
#define MPU_ADDR 0x68

const char* ssid = "ADD YOUR WIFI NAME HERE";     
const char* password = "ADD YOUR WIFI PASSWORD HERE";    
const int laptop_port = 4210;          

IPAddress laptop_ip(ADD YOUR LAPTOP IP (IPV4) HERE); //Seprate the ip using comma (,)

WiFiUDP udp;

void setup() {
  Serial.begin(115200);
  delay(200);

  WiFi.begin(ssid, password);
  Serial.println("Connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("ESP IP: ");
  Serial.println(WiFi.localIP());

  udp.begin(4211);

  Wire.begin(SDA_PIN, SCL_PIN);
  delay(100);
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission();
  delay(50);

  Serial.println("Streaming started...");
}

unsigned long lastSend = 0;
const int interval = 20; // ~50Hz

void loop() {
  unsigned long now = millis();
  if (now - lastSend < interval) return;
  lastSend = now;

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return;
  Wire.requestFrom(MPU_ADDR, 14);

  if (Wire.available() < 14) return;

  int16_t ax = (Wire.read()<<8) | Wire.read();
  int16_t ay = (Wire.read()<<8) | Wire.read();
  int16_t az = (Wire.read()<<8) | Wire.read();
  Wire.read(); Wire.read();
  int16_t gx = (Wire.read()<<8) | Wire.read();
  int16_t gy = (Wire.read()<<8) | Wire.read();
  int16_t gz = (Wire.read()<<8) | Wire.read();

  float axg = ax / 16384.0;
  float ayg = ay / 16384.0;
  float azg = az / 16384.0;
  float gxd = gx / 131.0;
  float gyd = gy / 131.0;
  float gzd = gz / 131.0;

  char packet[200];
  snprintf(packet, sizeof(packet),
    "{\"t\":%lu,\"ax\":%.4f,\"ay\":%.4f,\"az\":%.4f,\"gx\":%.3f,\"gy\":%.3f,\"gz\":%.3f}",
    now, axg, ayg, azg, gxd, gyd, gzd);

  udp.beginPacket(laptop_ip, laptop_port);
  udp.print(packet);
  udp.endPacket();
}
