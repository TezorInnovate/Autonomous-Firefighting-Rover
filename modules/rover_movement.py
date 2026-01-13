# modules/rover_movement.py
import socket
import time

class RoverMovement:
    """
    Interface to ESP32 rover for movement and servo control
    """
    def __init__(self, esp32_sock, forward_speed=0.55, turn_speed_diff=0.35):
        """
        esp32_sock: connected socket to ESP32
        forward_speed: scaling factor for forward movement (currently not applied)
        turn_speed_diff: difference for turning (currently not applied)
        """
        self.sock = esp32_sock
        self.forward_speed = forward_speed
        self.turn_speed_diff = turn_speed_diff

    def send_cmd(self, cmd):
        """
        Send a command to the ESP32 and return response
        """
        if not self.sock:
            return None
        try:
            self.sock.sendall((cmd + "\n").encode())
            self.sock.settimeout(1.0)
            resp = self.sock.recv(1024).decode().strip()
            return resp
        except (socket.timeout, OSError) as e:
            print(f"ESP32 communication error: {e}")
            return None

    # -------- MOVEMENT COMMANDS --------
    def move_forward(self):
        return self.send_cmd("MOVE FWD")

    def move_backward(self):
        return self.send_cmd("MOVE REV")

    def stop(self):
        return self.send_cmd("STOP")

    def turn_left(self, forward=True):
        # forward/backward differentiation can be added if needed
        return self.send_cmd("TURN LEFT")

    def turn_right(self, forward=True):
        return self.send_cmd("TURN RIGHT")

    # -------- CAMERA / ULTRASONIC SERVO --------
    def scan_left(self):
        return self.send_cmd("SCAN LEFT")

    def scan_right(self):
        return self.send_cmd("SCAN RIGHT")

    def scan_center(self):
        return self.send_cmd("SCAN CENTER")


# ================= STANDALONE TEST =================
if __name__ == "__main__":
    # Example: test movement
    import sys
    ip = "192.168.4.1"
    port = 3333
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        rover = RoverMovement(sock)
        print(rover.move_forward())
        time.sleep(1)
        print(rover.turn_left())
        time.sleep(1)
        print(rover.stop())
    except KeyboardInterrupt:
        print("Test interrupted")
