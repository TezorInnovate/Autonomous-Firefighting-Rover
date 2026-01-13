# modules/pump_control.py
import socket
import time

# ================= CONFIG =================
ESP32_IP = "192.168.4.1"
ESP32_PORT = 3333

# Servo PWM positions
SERVO_LEFT_US = 1200
SERVO_CENTER_US = 1500
SERVO_RIGHT_US = 1800

# ================= PUMP MODULE =================
class PumpControl:
    """
    Controls pump relay and water servo via ESP32
    """
    def __init__(self, ip=ESP32_IP, port=ESP32_PORT):
        self.ip = ip
        self.port = port
        self.sock = None
        self.connect()

    def connect(self):
        """Connect to ESP32 over Wi-Fi"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)
            self.sock.connect((self.ip, self.port))
            print(f"Connected to ESP32 pump at {self.ip}:{self.port}")
        except Exception as e:
            print("ESP32 pump connection failed:", e)
            self.sock = None

    def send_command(self, cmd):
        """Send a command and wait for response"""
        if not self.sock:
            self.connect()
            if not self.sock:
                return None
        try:
            self.sock.sendall((cmd + "\n").encode())
            resp = self.sock.recv(1024).decode().strip()
            return resp
        except Exception as e:
            print("Command send failed:", e)
            self.sock = None
            return None

    # ================= PUBLIC API =================
    def pump_on(self):
        return self.send_command("PUMP ON")

    def pump_off(self):
        return self.send_command("PUMP OFF")

    def turn_to_fire(self, fire_direction):
        """
        Aim water servo based on fire horizontal position
        fire_direction: 'LEFT', 'CENTER', 'RIGHT'
        """
        if fire_direction == "LEFT":
            pwm = SERVO_LEFT_US
        elif fire_direction == "RIGHT":
            pwm = SERVO_RIGHT_US
        else:
            pwm = SERVO_CENTER_US

        return self.send_command(f"WATER ANGLE {pwm}")


# ================= STANDALONE TEST =================
if __name__ == "__main__":
    pump = PumpControl()
    print("Pump control module test. Press Ctrl+C to exit.")
    try:
        while True:
            cmd = input("Enter command (on/off/left/center/right): ").strip().lower()
            if cmd == "on":
                print(pump.pump_on())
            elif cmd == "off":
                print(pump.pump_off())
            elif cmd in ["left", "center", "right"]:
                print(pump.turn_to_fire(cmd.upper()))
    except KeyboardInterrupt:
        print("Exiting pump control test")
