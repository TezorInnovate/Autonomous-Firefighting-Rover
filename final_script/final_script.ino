#include <Arduino.h>
#include <WiFi.h>

// ================= WIFI CONFIG =================
const char* ssid = "ESP32_ROVER";
const char* password = "rover123";

WiFiServer server(3333);
WiFiClient client;

// ================= PINS =================

// Ultrasonic / Camera servo
#define UC_SERVO_PIN 23

// Water left-right servo
#define W_SERVO_LR_PIN 19

// Motor Driver
#define IN1 26   // Left motor
#define IN2 27
#define IN3 12   // Right motor
#define IN4 13
#define ENA 25   // Left PWM
#define ENB 14   // Right PWM

// Pump Relay
#define PUMP_RELAY 22

// IR Sensors
#define IR1 32
#define IR2 33
#define IR3 34

// Flow sensor
#define FLOW_SENSOR_PIN 35
volatile unsigned int pulse_count = 0;

// Ultrasonic sensor (HC-SR04)
#define TRIG_PIN 4
#define ECHO_PIN 5

// ================= SPEED CONFIG =================
int speed_straight   = 150;   // normal cruising
int speed_turn_fast  = 200;   // outer wheel
int speed_turn_slow  = 80;    // inner wheel

// ================= SERVO CONFIG =================
#define SERVO_FREQ 50
#define PWM_RES 16

#define SERVO_CENTER 1500
#define SERVO_MIN 1200
#define SERVO_MAX 1800

// ================= FLOW SENSOR =================
void IRAM_ATTR pulse_counter() {
  pulse_count++;
}

// ================= SERVO HELPERS =================
uint32_t usToDuty(int us) {
  return map(us, 500, 2500, 1638, 8192);
}

void moveServoPin(int pin, int us) {
  us = constrain(us, SERVO_MIN, SERVO_MAX);
  ledcWrite(pin, usToDuty(us));
}

// ================= MOTOR SPEED =================
void setSpeedLR(int left_pwm, int right_pwm) {
  left_pwm  = constrain(left_pwm, 0, 255);
  right_pwm = constrain(right_pwm, 0, 255);
  analogWrite(ENA, left_pwm);
  analogWrite(ENB, right_pwm);
}

// ================= MOTOR CONTROL =================
void stopMotors() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void moveForward() {
  setSpeedLR(speed_straight, speed_straight);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  setSpeedLR(speed_straight, speed_straight);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

// ---- ARC TURNS (FORWARD + STEERING) ----
void turnLeft() {
  setSpeedLR(speed_turn_slow, speed_turn_fast);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  setSpeedLR(speed_turn_fast, speed_turn_slow);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

// ================= ULTRASONIC =================
float readUltrasonicDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout 30ms
  float distance_cm = duration * 0.0343 / 2.0;
  if (distance_cm == 0) distance_cm = -1; // invalid reading
  return distance_cm;
}

// ================= COMMAND HANDLER =================
String handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  // ---- Movement ----
  if (cmd == "MOVE FWD")   { moveForward();  return "OK MOVE FWD"; }
  if (cmd == "MOVE REV")   { moveBackward(); return "OK MOVE REV"; }
  if (cmd == "TURN LEFT")  { turnLeft();     return "OK TURN LEFT"; }
  if (cmd == "TURN RIGHT") { turnRight();    return "OK TURN RIGHT"; }
  if (cmd == "STOP")       { stopMotors();   return "OK STOP"; }

  // ---- Camera / Ultrasonic Servo ----
  if (cmd == "SCAN LEFT")   { moveServoPin(UC_SERVO_PIN, SERVO_MIN);    return "OK SCAN LEFT"; }
  if (cmd == "SCAN RIGHT")  { moveServoPin(UC_SERVO_PIN, SERVO_MAX);    return "OK SCAN RIGHT"; }
  if (cmd == "SCAN CENTER") { moveServoPin(UC_SERVO_PIN, SERVO_CENTER); return "OK SCAN CENTER"; }

  // ---- Water Servo (precise aiming) ----
  if (cmd.startsWith("WATER ANGLE")) {
    int us = cmd.substring(11).toInt();
    moveServoPin(W_SERVO_LR_PIN, us);
    return "OK WATER ANGLE";
  }

  // ---- Pump ----
  if (cmd == "PUMP ON")  { digitalWrite(PUMP_RELAY, HIGH); return "OK PUMP ON"; }
  if (cmd == "PUMP OFF") { digitalWrite(PUMP_RELAY, LOW);  return "OK PUMP OFF"; }

  // ---- GET DISTANCE ----
  if (cmd == "GET DIST") {
    float dist = readUltrasonicDistance();
    return "DIST:" + String(dist, 1);
  }

  return "ERR UNKNOWN COMMAND";
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);

  // Motor pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  stopMotors();

  // Pump
  pinMode(PUMP_RELAY, OUTPUT);
  digitalWrite(PUMP_RELAY, LOW);

  // IR Sensors
  pinMode(IR1, INPUT);
  pinMode(IR2, INPUT);
  pinMode(IR3, INPUT);

  // Flow sensor
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulse_counter, RISING);

  // Servos
  ledcAttach(UC_SERVO_PIN, SERVO_FREQ, PWM_RES);
  ledcAttach(W_SERVO_LR_PIN, SERVO_FREQ, PWM_RES);
  moveServoPin(UC_SERVO_PIN, SERVO_CENTER);
  moveServoPin(W_SERVO_LR_PIN, SERVO_CENTER);

  // Ultrasonic
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Wi-Fi AP
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  server.begin();

  Serial.println("ESP32 FIRE ROVER READY (ARC TURN MODE)");
  Serial.println("IP: 192.168.4.1  PORT: 3333");
}

// ================= LOOP =================
unsigned long last_report = 0;
const unsigned long REPORT_INTERVAL = 1000;

void loop() {
  // Accept client
  if (!client || !client.connected()) {
    client = server.available();
    return;
  }

  // Handle commands
  if (client.available()) {
    String cmd = client.readStringUntil('\n');
    String response = handleCommand(cmd);
    client.println(response);
  }

  // Telemetry
  if (millis() - last_report > REPORT_INTERVAL) {
    last_report = millis();

    int ir_status =
      (digitalRead(IR1)) |
      (digitalRead(IR2) << 1) |
      (digitalRead(IR3) << 2);

    float dist = readUltrasonicDistance();

    String telemetry =
      "IR:" + String(ir_status) +
      " FLOW:" + String(pulse_count) +
      " DIST:" + String(dist, 1);

    client.println(telemetry);
    pulse_count = 0;
  }
}
