#include <Arduino.h>
#include <WiFi.h>

//////////////////////
// WIFI CONFIG (AP MODE)
//////////////////////
const char* ssid = "ESP32_ROVER";
const char* password = "rover123";

WiFiServer server(3333);
WiFiClient client;

//////////////////////
// PINS (UNCHANGED)
//////////////////////

// Ultrasonic (defined, used later)
#define TRIG_PIN 5
#define ECHO_PIN 18

// Servos
#define UC_SERVO_PIN 23      // Ultrasonic + Camera
#define W_SERVO_LR_PIN 19    // Water left-right

// Motor Driver
#define IN1 26
#define IN2 27
#define IN3 12
#define IN4 13
#define ENA 25
#define ENB 14

// Pump Relay
#define PUMP_RELAY 22

//////////////////////
// SERVO CONFIG
//////////////////////
#define SERVO_FREQ 50
#define PWM_RES 16

#define SERVO_LEFT    1900
#define SERVO_CENTER  1500
#define SERVO_RIGHT   1100

//////////////////////
// SERVO HELPERS
//////////////////////
uint32_t usToDuty(int us) {
  return map(us, 500, 2500, 1638, 8192);
}

void moveServoPin(int pin, int us) {
  ledcWrite(pin, usToDuty(us));
}

//////////////////////
// MOTOR CONTROL
//////////////////////
void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnLeft() {
  stopMotors();
  delay(200);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  stopMotors();
  delay(200);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

//////////////////////
// COMMAND HANDLER
//////////////////////
String handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  // ================= MOVEMENT =================
  if (cmd == "MOVE_FORWARD") {
    moveForward();
    return "OK MOVE_FORWARD";
  }

  if (cmd == "MOVE_FORWARD_SLOW") {
    moveForward(); // PWM control later
    return "OK MOVE_FORWARD_SLOW";
  }

  if (cmd == "TURN_LEFT") {
    turnLeft();
    return "OK TURN_LEFT";
  }

  if (cmd == "TURN_RIGHT") {
    turnRight();
    return "OK TURN_RIGHT";
  }

  if (cmd == "STOP") {
    stopMotors();
    return "OK STOP";
  }

  // ================= WATER AIM (LR ONLY) =================
  if (cmd == "AIM_LEFT") {
    moveServoPin(W_SERVO_LR_PIN, SERVO_LEFT);
    return "OK AIM_LEFT";
  }

  if (cmd == "AIM_RIGHT") {
    moveServoPin(W_SERVO_LR_PIN, SERVO_RIGHT);
    return "OK AIM_RIGHT";
  }

  if (cmd == "AIM_CENTER") {
    moveServoPin(W_SERVO_LR_PIN, SERVO_CENTER);
    return "OK AIM_CENTER";
  }

  // ================= PUMP =================
  if (cmd == "PUMP_ON") {
    digitalWrite(PUMP_RELAY, HIGH);
    return "OK PUMP_ON";
  }

  if (cmd == "PUMP_OFF") {
    digitalWrite(PUMP_RELAY, LOW);
    return "OK PUMP_OFF";
  }

  return "ERR UNKNOWN";
}

//////////////////////
// SETUP
//////////////////////
void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  pinMode(PUMP_RELAY, OUTPUT);
  digitalWrite(PUMP_RELAY, LOW);

  analogWrite(ENA, 200);
  analogWrite(ENB, 200);

  ledcAttach(UC_SERVO_PIN, SERVO_FREQ, PWM_RES);
  ledcAttach(W_SERVO_LR_PIN, SERVO_FREQ, PWM_RES);

  moveServoPin(UC_SERVO_PIN, SERVO_CENTER);
  moveServoPin(W_SERVO_LR_PIN, SERVO_CENTER);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  server.begin();

  Serial.println("ESP32 FIRE ROVER SERVER READY");
  Serial.println("IP: 192.168.4.1  PORT: 3333");
}

//////////////////////
// LOOP
//////////////////////
void loop() {
  if (!client || !client.connected()) {
    client = server.available();
    return;
  }

  if (client.available()) {
    String cmd = client.readStringUntil('\n');
    String response = handleCommand(cmd);
    client.println(response);
    Serial.println("CMD: " + cmd);
  }
}
