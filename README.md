# 🔥 Autonomous Firefighting Rover  
**AI Vision–Driven Mobile Fire Detection & Suppression System**

---

## 📌 Overview

The **Autonomous Firefighting Rover** is a fully self-designed and implemented robotic system capable of **detecting fire using AI-based computer vision**, **navigating towards it autonomously**, and **extinguishing it using an onboard water pump**.

This project was developed **from scratch**, covering:

- Mechanical and electronic hardware integration  
- ESP32 embedded firmware and Wi-Fi communication  
- AI fire detection using a custom-trained YOLO model  
- Vision-based navigation and arrival logic  
- Autonomous and manual control modes  
- Water usage telemetry and logging  

The system is intended for **robotics research, autonomous systems education, and real-world fire response experimentation**.

---

## 🎯 Project Objectives

- Detect fire in real time using a camera and AI vision
- Autonomously navigate while keeping fire centred in view
- Reliably determine arrival at fire **without relying on IR sensors**
- Activate water pump only when the rover reaches the fire
- Log water usage for analysis
- Provide manual override for safety and testing

---

## 🤖 System Architecture

Camera → AI Vision (YOLO)
↓
Decision Logic (Python)
↓
Wi-Fi Commands (TCP Socket)
↓
ESP32
┌────────┼─────────┐
Motors Pump Relay Servos


---

## 🧠 AI & Vision System

### Fire Detection
- Custom **YOLO object detection model**
- Trained specifically for **fire / flame detection**
- Real-time inference using OpenCV

### Vision-Based Arrival Logic (Key Innovation)
Instead of unreliable distance estimation using bounding box size:

- A **vertical line** is drawn from:
  - **Fire centre**
  - To **bottom-centre of the camera frame**
- As the rover approaches the fire, this line shortens
- When the line length falls below a configurable threshold:
  - Rover stops
  - Pump is activated

This method is:
- Independent of flame size variation
- Stable against detection noise
- Camera-only (no extra sensors required)

---

## 🛠 Hardware Components

- **ESP32** (Wi-Fi enabled microcontroller)
- DC motors with motor driver
- Water pump with relay module
- Servo motors (camera / hose mounting)
- USB / CSI camera
- Rover chassis and power system

---

## 🔌 Embedded Firmware (ESP32)

- Developed using **Arduino IDE**
- TCP socket server over Wi-Fi
- Handles:
  - Motor movement commands
  - Pump ON / OFF control
  - Servo positioning
  - Flow sensor telemetry
- Designed to operate using **a single shared socket**

---

## 🧩 Software Modules

### `vision_ai.py`
- YOLO fire detection
- Visual overlays (bounding box, centre line, arrival line)
- Thread-safe detection state
- Fire centre tracking

### `rover_movement.py`
- High-level movement control
- Forward / stop / left / right commands
- TCP socket communication with ESP32

### `pump_control.py`
- Pump relay control
- Socket-safe communication
- Reliable activation logic

### `flow_logger.py`
- Timestamped water usage logging
- Event logging support
- Automatic log directory creation

### `commander.py`
- Central autonomous controller
- Vision-only arrival logic
- Manual override support
- Pump activation and shutdown control

---

## ⚙️ Operating Modes

### Autonomous Mode
- Starts by default
- Detects fire and navigates towards it
- Stops using vision-based arrival logic
- Activates pump
- Turns pump off once fire is no longer detected

### Manual Override Mode
- Keyboard control (`W / A / S / D`)
- Emergency stop
- Intended for testing and safety

---

## 📁 Project Structure

Autonomous-Firefighting-Rover/
│
├── modules/
│ ├── vision_ai.py
│ ├── rover_movement.py
│ ├── pump_control.py
│ ├── flow_logger.py
│ └── commander.py
│
├── esp32_firmware/
│ └── esp32_rover.ino
│
├── logs/
│ └── water_usage_log.txt
│
├── runs/
│ └── detect/
│ └── fire_model3/
│
└── README.md

## 👨‍💻 Author

Faizan Ahmed
B.Tech Computer Science & Engineering
Focus areas: Robotics, AI, Autonomous Systems, Embedded Intelligence

This project was entirely self-designed and implemented, covering hardware, firmware, AI model training, and autonomous control.

## 📜 License

Released for educational and research purposes.
Contact the author for commercial usage or extensions.
