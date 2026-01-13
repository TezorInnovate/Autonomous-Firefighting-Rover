import serial
import time

# ================================
# CHANGE THIS TO YOUR ESP32 PORT
# ================================
PORT = 'COM3'      # e.g. COM3, COM6, etc.
BAUD = 115200

# ================================
# OPEN SERIAL CONNECTION
# ================================
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)   # Allow ESP32 to reset

def send(cmd, delay_time=2):
    print(f"\n>>> Sending: {cmd}")
    ser.write((cmd + '\n').encode())
    time.sleep(0.2)

    # Read ESP32 response
    while ser.in_waiting:
        print("ESP32:", ser.readline().decode().strip())

    time.sleep(delay_time)

# ================================
# MOTOR TEST SEQUENCE
# ================================

print("Starting differential drive test...")

send("FORWARD", 3)
send("STOP", 1)

send("LEFT", 2)
send("STOP", 1)

send("RIGHT", 2)
send("STOP", 1)

send("BACKWARD", 3)
send("STOP", 2)

print("\nTest complete. Stopping motors.")
send("STOP", 1)

# ================================
# CLOSE SERIAL
# ================================
ser.close()
print("Serial connection closed.")