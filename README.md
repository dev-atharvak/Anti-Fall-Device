# Anti-Fall Device

An IoT-based fall detection system using an ESP32-C3, MPU6050 motion sensor, Wi-Fi communication, and a Random Forest Machine Learning model. The system continuously monitors body movement, detects falls in real time, and automatically sends Telegram alerts when a fall is detected.

---

## Features

- Real-time fall detection
- ESP32-C3 + MPU6050 integration
- Wi-Fi based sensor data streaming
- UDP communication
- Machine Learning powered classification
- Telegram alert notifications
- Data logging and analysis
- Model training and evaluation scripts included

---

## Hardware Requirements

- ESP32-C3 Development Board
- MPU6050 Gyroscopic Sensor
- USB Cable
- Wi-Fi Network
- Laptop/PC with Python installed

---

# Hardware Wiring

## ESP32-C3 ↔️ MPU6050 Connections

| MPU6050 Pin | ESP32-C3 Pin |
|------------|---------------|
| VCC        | 3.3V          |
| GND        | GND           |
| SDA        | GPIO 8        |
| SCL        | GPIO 9        |

## Pin Configuration

cpp
#define SDA_PIN 8
#define SCL_PIN 9
#define MPU_ADDR 0x68


## Wiring Diagram

text
MPU6050              ESP32-C3
--------             --------
VCC      ----------> 3.3V
GND      ----------> GND
SDA      ----------> GPIO 8
SCL      ----------> GPIO 9


---

# Network Configuration

Before uploading the ESP32 code, update the Wi-Fi credentials and laptop IP address inside:

cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

IPAddress laptop_ip(192,168,1,12);
const int laptop_port = 4210;


## Find Your Laptop IPv4 Address

Open Command Prompt:

bash
ipconfig


Example:

text
IPv4 Address . . . . . . . . . : 192.168.1.12


Update:

cpp
IPAddress laptop_ip(192,168,1,12);


with your laptop's IPv4 address.

Example:

text
IPv4 = 192.168.0.105


Change to:

cpp
IPAddress laptop_ip(192,168,0,105);


### Important Notes

- ESP32 and Laptop must be connected to the same Wi-Fi network.
- Firewall should allow Python to receive UDP packets.
- Incorrect IP address will prevent communication.

---

# Project Structure

```text
fall_project/

├── alerts_png/
├── alerts_raw/
├── data/
├── data_wifi/
├── esp_wifi_mpu_stream/
│   └── esp_wifi_mpu_stream.ino
├── logs/
├── model/
│   └── rf_model.pkl
├── extract_features.py
├── leave_one_out_eval.py
├── realtime_wifi_detect.py
├── train_rf.py
├── udp_logger.py
└── README.md
```


---

# File Descriptions

## esp_wifi_mpu_stream.ino

Runs on ESP32-C3.

Responsibilities:

- Reads MPU6050 sensor data
- Connects to Wi-Fi
- Sends accelerometer and gyroscope readings to the laptop using UDP

---

## udp_logger.py

Dataset collection tool.

Responsibilities:

- Receives UDP packets from ESP32
- Saves sensor data into CSV files
- Used when creating a dataset for training

Run:

bash
python udp_logger.py


---

## extract_features.py

Feature extraction script.

Responsibilities:

- Reads raw CSV files
- Extracts statistical features
- Creates processed training data

Run:

bash
python extract_features.py


---

## train_rf.py

Model training script.

Responsibilities:

- Trains Random Forest model
- Saves trained model as:

text
model/rf_model.pkl


Run:

bash
python train_rf.py


Note: Only required if you want to retrain the model using new data.

---

## leave_one_out_eval.py

Model evaluation script.

Responsibilities:

- Evaluates model accuracy
- Generates performance metrics
- Produces confusion matrix

Run:

bash
python leave_one_out_eval.py


---

## realtime_wifi_detect.py

Main application.

Responsibilities:

- Receives live sensor data
- Loads trained model
- Detects falls in real time
- Sends Telegram alerts
- Saves logs

Run:

bash
python realtime_wifi_detect.py


This is the MAIN program used during deployment.

---

## model/rf_model.pkl

Pre-trained Random Forest model used by realtime_wifi_detect.py.

No retraining required if this file already exists.

---

## alerts_raw/

Stores raw fall detection events.

---

## alerts_png/

Stores generated graphs and alert images.

---

## logs/

Stores real-time monitoring logs.

---

# How To Run The Project

## Step 1

Find your laptop IP address:

bash
ipconfig


## Step 2

Update:

cpp
IPAddress laptop_ip(...)


inside:

text
esp_wifi_mpu_stream.ino


## Step 3

Update Wi-Fi credentials:

cpp
ssid
password


inside:

text
esp_wifi_mpu_stream.ino


## Step 4

Upload:

text
esp_wifi_mpu_stream.ino


to ESP32-C3 using Arduino IDE.

## Step 5

Connect ESP32 and laptop to the same Wi-Fi network.

## Step 6

Run the main application:

bash
python realtime_wifi_detect.py


## Step 7

ESP32 begins streaming MPU6050 sensor data.

## Step 8

The trained Random Forest model analyzes incoming data.

## Step 9

If a fall is detected:

- Event is logged
- Alert image is generated
- Telegram notification is sent

---

# Training Your Own Model

### Collect Data

bash
python udp_logger.py


### Extract Features

bash
python extract_features.py


### Train Model

bash
python train_rf.py


### Evaluate Model

bash
python leave_one_out_eval.py


### There is no need to train model it is already trained 


---

# Python Dependencies

bash
pip install pandas numpy scipy scikit-learn matplotlib joblib requests


---

# Telegram Alerts

Configure:

python
TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"


inside the detection script.

Never upload your actual bot token or chat ID to a public repository.

---

# Future Improvements

- Mobile App Integration
- GPS Tracking
- Cloud Dashboard
- Caregiver Monitoring Portal
- Multiple User Support
- Battery Powered Wearable Version

---

# Author

## dev-atharvak (Atharva Kukade)
Full Stack Developer | AI & Embedded Systems Enthusiast | Github: dev-atharvak (https://github.com/dev-atharvak)

## FOUNDER: AkTechh Solution
### About AkTechh Solution

*AkTechh Solution* is a student-led technology initiative focused on developing innovative software, IoT, embedded systems, automation, and academic engineering projects. Our goal is to create practical, affordable, and real-world technology solutions while helping students learn, build, and showcase engineering projects with modern tools and technologies.

---

# License

MIT License
