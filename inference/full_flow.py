import cv2
import time
import socket
import threading
from ultralytics import YOLO

# ================= CONFIG =================
ESP32_IP = "192.168.4.1"
ESP32_PORT = 3333

TARGET_DISTANCE_CM = 25
FIRE_CONF = 0.45
FRAME_SKIP = 3
OBSTACLE_CM = 30

# Distance model
def estimate_distance(h):
    return 4907.82 / h + 0.72

# ================= ESP32 =================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ESP32_IP, ESP32_PORT))
sock.settimeout(0.01)

def send(cmd):
    try:
        sock.sendall((cmd + "\n").encode())
    except:
        pass

# ================= SHARED =================
lock = threading.Lock()

state = "IDLE_SCAN"
manual_mode = False

fire_detected = False
fire_distance = None
ir_triggered = False
fire_missing_frames = 0

# ================= VISION THREAD =================
def vision_loop():
    global fire_detected, fire_distance

    model = YOLO("runs/detect/runs/train/fire_model3/weights/best.pt")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_id += 1
        if frame_id % FRAME_SKIP != 0:
            continue

        results = model(frame, conf=FIRE_CONF, verbose=False)
        found = False

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) != 0:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                h = y2 - y1
                with lock:
                    fire_detected = True
                    fire_distance = estimate_distance(h)
                found = True

                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                cv2.putText(frame, f"{fire_distance:.1f} cm",
                            (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0,255,0), 2)
                break

        if not found:
            with lock:
                fire_detected = False
                fire_distance = None

        cv2.imshow("Fire View", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('m'):
            toggle_manual(True)
        if key == ord('a'):
            toggle_manual(False)

    cap.release()
    cv2.destroyAllWindows()

# ================= MANUAL =================
def toggle_manual(enable):
    global manual_mode, state
    manual_mode = enable
    if enable:
        send("STOP")
        send("PUMP OFF")
    else:
        state = "IDLE_SCAN"

# ================= TELEMETRY =================
def telemetry_loop():
    global ir_triggered
    while True:
        try:
            msg = sock.recv(1024).decode()
            if "IR:1" in msg:
                ir_triggered = True
            else:
                ir_triggered = False
        except:
            pass
        time.sleep(0.05)

# ================= CONTROL THREAD =================
def control_loop():
    global state, fire_missing_frames

    while True:
        if manual_mode:
            time.sleep(0.1)
            continue

        with lock:
            fire = fire_detected
            dist = fire_distance
            ir = ir_triggered

        # ---------- STATE MACHINE ----------
        if state == "IDLE_SCAN":
            send("STOP")
            if fire:
                state = "APPROACH_FIRE"

        elif state == "APPROACH_FIRE":
            if not fire:
                state = "IDLE_SCAN"
            elif dist and dist > TARGET_DISTANCE_CM:
                send("MOVE FWD")
            else:
                send("STOP")
                state = "FIRE_CONFIRM"

        elif state == "FIRE_CONFIRM":
            send("STOP")
            if fire and dist <= TARGET_DISTANCE_CM:
                send("PUMP ON")
                fire_missing_frames = 0
                state = "EXTINGUISH"
            else:
                state = "APPROACH_FIRE"

        elif state == "EXTINGUISH":
            if fire:
                fire_missing_frames = 0
            else:
                fire_missing_frames += 1

            if fire_missing_frames > 10:
                send("PUMP OFF")
                print("🔥 Fire extinguished")
                state = "POST_EXTINGUISH_SCAN"

        elif state == "POST_EXTINGUISH_SCAN":
            if fire:
                state = "APPROACH_FIRE"

        time.sleep(0.05)

# ================= START =================
threads = [
    threading.Thread(target=vision_loop),
    threading.Thread(target=control_loop),
    threading.Thread(target=telemetry_loop)
]

for t in threads:
    t.start()

for t in threads:
    t.join()
