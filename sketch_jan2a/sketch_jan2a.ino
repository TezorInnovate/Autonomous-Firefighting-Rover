#include <Arduino.h>
#include <WiFi.h>

// ================= WIFI CONFIG =================
const char* ssid = "ESP32_ROVER";
const char* password = "rover123";

WiFiServer server(3333);
WiFiClient client;

// ================= PINS =================

// Ultrasonic (defined, not used here)
#define TRIG_PIN 5
#define ECHO_PIN 18

// Servos
#define UC_SERVO_PIN 23      // Ultrasonic + Camera
#define W_SERVO_LR_PIN 19    // Water left-right
#define W_SERVO_UD_PIN 21    // Water up-down

// Motor Driver
#define IN1 26
#define IN2 27
#define IN3 12
#define IN4 13
#define ENA 25
#define ENB 14

// Pump Relay
#define PUMP_RELAY 22

// ================= MOTOR SPEED (TEST MODE) =================
#define MOTOR_TEST_SPEED 150   // VERY slow (0–255)

// ================= SERVO CONFIG =================
#define SERVO_FREQ 50
#define PWM_RES 16

#define SERVO_LEFT    1900
#define SERVO_CENTER  1500
#define SERVO_RIGHT   1100

// ================= SERVO HELPERS =================
uint32_t usToDuty(int us) {
  return map(us, 500, 2500, 1638, 8192);
}

void moveServoPin(int pin, int us) {
  ledcWrite(pin, usToDuty(us));
}

// ================= MOTOR HELPERS =================
void setMotorSpeed(uint8_t speed) {
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
}

void stopMotors() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

// ================= MOTOR CONTROL =================
void moveForward() {
  stopMotors();
  delay(100);
  setMotorSpeed(MOTOR_TEST_SPEED);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  stopMotors();
  delay(100);
  setMotorSpeed(MOTOR_TEST_SPEED);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  stopMotors();
  delay(100);
  setMotorSpeed(MOTOR_TEST_SPEED - 15);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  stopMotors();
  delay(100);
  setMotorSpeed(MOTOR_TEST_SPEED - 15);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

// ================= COMMAND HANDLER =================
String handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  // Movement
  if (cmd == "MOVE FWD") {
    moveForward();
    return "OK MOVE FWD";
  }
  if (cmd == "MOVE REV") {
    moveBackward();
    return "OK MOVE REV";
  }
  if (cmd == "TURN LEFT") {
    turnLeft();
    return "OK TURN LEFT";
  }
  if (cmd == "TURN RIGHT") {
    turnRight();
    return "OK TURN RIGHT";
  }
  if (cmd == "STOP") {
    stopMotors();
    return "OK STOP";
  }

  // Ultrasonic + Camera Servo
  if (cmd == "SCAN LEFT") {
    moveServoPin(UC_SERVO_PIN, SERVO_LEFT);
    return "OK SCAN LEFT";
  }
  if (cmd == "SCAN RIGHT") {
    moveServoPin(UC_SERVO_PIN, SERVO_RIGHT);
    return "OK SCAN RIGHT";
  }
  if (cmd == "SCAN CENTER") {
    moveServoPin(UC_SERVO_PIN, SERVO_CENTER);
    return "OK SCAN CENTER";
  }

  // Water Servos
  if (cmd == "WATER LEFT") {
    moveServoPin(W_SERVO_LR_PIN, SERVO_LEFT);
    return "OK WATER LEFT";
  }
  if (cmd == "WATER RIGHT") {
    moveServoPin(W_SERVO_LR_PIN, SERVO_RIGHT);
    return "OK WATER RIGHT";
  }
  if (cmd == "WATER CENTER") {
    moveServoPin(W_SERVO_LR_PIN, SERVO_CENTER);
    return "OK WATER CENTER";
  }
  if (cmd == "WATER UP") {
    moveServoPin(W_SERVO_UD_PIN, SERVO_LEFT);
    return "OK WATER UP";
  }
  if (cmd == "WATER DOWN") {
    moveServoPin(W_SERVO_UD_PIN, SERVO_RIGHT);
    return "OK WATER DOWN";
  }

  // Pump
  if (cmd == "PUMP ON") {
    digitalWrite(PUMP_RELAY, HIGH);
    return "OK PUMP ON";
  }
  if (cmd == "PUMP OFF") {
    digitalWrite(PUMP_RELAY, LOW);
    return "OK PUMP OFF";
  }

  return "ERR UNKNOWN COMMAND";
}

// ================= SETUP =================
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

  // Attach servos using LEDC
  ledcAttach(UC_SERVO_PIN, SERVO_FREQ, PWM_RES);
  ledcAttach(W_SERVO_LR_PIN, SERVO_FREQ, PWM_RES);
  ledcAttach(W_SERVO_UD_PIN, SERVO_FREQ, PWM_RES);

  moveServoPin(UC_SERVO_PIN, SERVO_CENTER);
  moveServoPin(W_SERVO_LR_PIN, SERVO_CENTER);
  moveServoPin(W_SERVO_UD_PIN, SERVO_CENTER);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  server.begin();

  Serial.println("ESP32 WiFi Command Server READY (SLOW TEST MODE)");
  Serial.println("IP: 192.168.4.1  PORT: 3333");
}

// ================= LOOP =================
void loop() {
  if (!client || !client.connected()) {
    client = server.available();
    return;
  }

  if (client.available()) {
    String cmd = client.readStringUntil('\n');
    String response = handleCommand(cmd);
    client.println(response);
  }
}
