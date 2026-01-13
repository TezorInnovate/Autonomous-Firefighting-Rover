# modules/ultrasonic.py
import time

class UltrasonicModule:
    """
    Uses ESP32 telemetry and servo to get distances for obstacle avoidance
    """
    def __init__(self, esp32_sock):
        self.sock = esp32_sock

    def send_cmd(self, cmd):
        """
        Send a command to ESP32 and return response
        """
        if not self.sock:
            return None
        try:
            self.sock.sendall((cmd + "\n").encode())
            resp = self.sock.recv(1024).decode().strip()
            return resp
        except Exception as e:
            print(f"ESP32 communication error: {e}")
            return None

    # ----------------- DISTANCE -----------------
    def get_distance_cm(self):
        """
        Get distance from telemetry (if DIST: is reported by ESP32)
        Currently ESP32 sends: "IR:0 FLOW:12"
        This can be expanded if ESP32 adds DIST:
        """
        resp = self.send_cmd("GET DIST")
        if resp and "DIST:" in resp:
            try:
                dist_cm = float(resp.split("DIST:")[1].strip())
                return dist_cm
            except:
                return None
        return None

    def scan_left_right(self):
        """
        Scan left and right using servo and return distances
        Returns (left_dist_cm, right_dist_cm)
        """
        left_dist = None
        right_dist = None

        self.send_cmd("SCAN LEFT")
        time.sleep(0.3)
        left_dist = self.get_distance_cm()

        self.send_cmd("SCAN RIGHT")
        time.sleep(0.3)
        right_dist = self.get_distance_cm()

        self.send_cmd("SCAN CENTER")
        time.sleep(0.3)

        return left_dist, right_dist


# ================= STANDALONE TEST =================
if __name__ == "__main__":
    import socket
    ip = "192.168.4.1"
    port = 3333
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        ultra = UltrasonicModule(sock)
        while True:
            left, right = ultra.scan_left_right()
            print(f"Left: {left} cm, Right: {right} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting ultrasonic test")
