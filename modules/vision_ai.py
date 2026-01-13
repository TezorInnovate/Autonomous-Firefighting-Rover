# modules/vision_ai.py
import cv2
from ultralytics import YOLO
import threading

# ================== CONFIG ==================
MODEL_PATH = "runs/detect/runs/train/fire_model3/weights/best.pt"
CAMERA_INDEX = 0
CONF_THRESHOLD = 0.5

ARRIVAL_PIXEL_THRESHOLD = 200   # 🔧 visual + logic threshold

# ============================================

class FireVision:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():
            raise RuntimeError("Camera not accessible")

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.center_x = self.frame_width // 2

        self.fire_detected = False
        self.fire_center = None
        self.fire_bbox = None

        self.lock = threading.Lock()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        results = self.model(frame, conf=CONF_THRESHOLD, verbose=False)
        fire_found = False

        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < CONF_THRESHOLD:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                with self.lock:
                    self.fire_detected = True
                    self.fire_center = (cx, cy)
                    self.fire_bbox = (x1, y1, x2, y2)

                # ---------------- DRAW FIRE BOX ----------------
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                # ---------------- ARRIVAL LINE ----------------
                vertical_distance = self.frame_height - cy

                # Line from fire center to bottom
                cv2.line(
                    frame,
                    (cx, cy),
                    (cx, self.frame_height),
                    (0, 255, 255),
                    2
                )

                # Threshold marker
                threshold_y = self.frame_height - ARRIVAL_PIXEL_THRESHOLD
                cv2.line(
                    frame,
                    (0, threshold_y),
                    (self.frame_width, threshold_y),
                    (0, 0, 255),
                    2
                )

                # Distance text
                cv2.putText(
                    frame,
                    f"Arrival distance: {vertical_distance}px",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                if vertical_distance <= ARRIVAL_PIXEL_THRESHOLD:
                    cv2.putText(
                        frame,
                        "ARRIVED",
                        (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 0, 255),
                        3
                    )

                fire_found = True
                break

        if not fire_found:
            with self.lock:
                self.fire_detected = False
                self.fire_center = None
                self.fire_bbox = None

        # Center reference line
        cv2.line(
            frame,
            (self.center_x, 0),
            (self.center_x, self.frame_height),
            (0, 255, 0),
            1
        )

        cv2.imshow("Fire Detection", frame)
        cv2.waitKey(1)

    # ============ PUBLIC API ============
    def detect_fire(self):
        with self.lock:
            return self.fire_detected

    def get_fire_center(self):
        with self.lock:
            return self.fire_center

    def get_fire_bbox(self):
        with self.lock:
            return self.fire_bbox

    def shutdown(self):
        self.cap.release()
        cv2.destroyAllWindows()


# ================== STANDALONE TEST ==================
if __name__ == "__main__":
    vision = FireVision()
    print("Fire vision running. Press CTRL+C to exit.")
    try:
        while True:
            vision.update_frame()
    except KeyboardInterrupt:
        vision.shutdown()
