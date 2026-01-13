import os
import cv2
import socket
import time
from ultralytics import YOLO

# =============================
# OFFLINE FLAGS (prevent GitHub downloads)
# =============================
os.environ["ULTRALYTICS_NO_NETWORK"] = "True"  # disable network access
os.environ["ULTRALYTICS_HUB"] = "False"       # disable hub
os.environ["YOLO_VERBOSE"] = "False"          # minimal logging

# =============================
# CONFIG
# =============================
MODEL_PATH = "runs/detect/runs/train/fire_model3/weights/best.pt"
CAMERA_INDEX = 0

ESP32_IP = "192.168.4.1"     # ESP32 AP IP
ESP32_PORT = 3333

CONF_THRESHOLD = 0.25
IMG_SIZE = 640               # smaller for faster inference

# Fire proximity thresholds (relative to bounding box area / frame area)
FAR_THRESH = 0.02
APPROACH_THRESH = 0.08

# =============================
# SOCKET SETUP
# =============================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)

try:
    sock.connect((ESP32_IP, ESP32_PORT))
    print("[INFO] Connected to ESP32 via Wi-Fi")
except Exception as e:
    raise RuntimeError(f"ESP32 connection failed: {e}")

def send_cmd(cmd):
    try:
        sock.sendall((cmd + "\n").encode())
        print("[CMD]", cmd)
    except Exception as e:
        print("[ERROR] Command send failed:", e)

# =============================
# LOAD YOLO MODEL (offline)
# =============================
model = YOLO(MODEL_PATH, task="detect")  # task="detect" prevents auto-download

# =============================
# CAMERA SETUP
# =============================
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise RuntimeError("Camera not accessible")

last_cmd = None

# =============================
# MAIN LOOP
# =============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    frame_area = h * w

    # Run YOLO inference
    results = model(
        frame,
        imgsz=IMG_SIZE,
        conf=CONF_THRESHOLD,
        verbose=False
    )

    fire_detected = False
    fire_state = "NONE"

    # Parse detection results
    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            if cls != 0:   # Fire class index
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_area = (x2 - x1) * (y2 - y1)

            # Ignore tiny noise
            if box_area < 0.001 * frame_area:
                continue

            fire_detected = True
            ratio = box_area / frame_area

            if ratio < FAR_THRESH:
                fire_state = "FAR"
            elif ratio < APPROACH_THRESH:
                fire_state = "APPROACHING"
            else:
                fire_state = "AT_FIRE"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Fire {fire_state}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
            break  # only process the first fire detection

    # =============================
    # COMMAND LOGIC
    # =============================
    cmd = "STOP"

    if fire_detected:
        if fire_state == "FAR":
            cmd = "MOVE_FORWARD"
        elif fire_state == "APPROACHING":
            cmd = "MOVE_FORWARD_SLOW"
        elif fire_state == "AT_FIRE":
            cmd = "STOP"

    if cmd != last_cmd:
        send_cmd(cmd)
        last_cmd = cmd

    # =============================
    # DEBUG OVERLAY
    # =============================
    cv2.putText(
        frame,
        f"STATE: {fire_state}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )

    cv2.imshow("Fire Navigation (Wi-Fi)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# =============================
# CLEANUP
# =============================
cap.release()
cv2.destroyAllWindows()
sock.close()
