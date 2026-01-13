import cv2
import numpy as np
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
CAMERA_INDEX = 0
BLACK_THRESHOLD = 60       # <--- darkness cutoff
MIN_AREA = 8000            # ignore noise
calibration_data = []      # (distance_cm, bbox_height_px)

cap = cv2.VideoCapture(CAMERA_INDEX)

print("\nBLACK BOX CALIBRATION MODE")
print("Use a solid BLACK rectangle")
print("Press 'c' to capture | 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --------- BLACK OBJECT MASK ---------
    _, mask = cv2.threshold(
        gray, BLACK_THRESHOLD, 255, cv2.THRESH_BINARY_INV
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    largest = None
    max_area = 0

    for c in contours:
        area = cv2.contourArea(c)
        if area > MIN_AREA and area > max_area:
            largest = c
            max_area = area

    bbox_height = None

    if largest is not None:
        x, y, w, h = cv2.boundingRect(largest)
        bbox_height = h

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"Height: {h}px",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    cv2.imshow("Calibration View", frame)
    cv2.imshow("Black Mask", mask)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c') and bbox_height is not None:
        dist = float(input("Enter distance from camera (cm): "))
        calibration_data.append((dist, bbox_height))
        print(f"Saved: {dist} cm → {bbox_height} px\n")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# ---------------- CURVE FIT ----------------
distances = np.array([d[0] for d in calibration_data])
bbox_heights = np.array([d[1] for d in calibration_data])

coeffs = np.polyfit(1 / bbox_heights, distances, 1)
a, b = coeffs

print("\n=== FINAL DISTANCE MODEL ===")
print(f"distance_cm = {a:.2f} / bbox_height_px + {b:.2f}")

# ---------------- PLOT ----------------
h_vals = np.linspace(min(bbox_heights), max(bbox_heights), 100)

plt.figure(figsize=(7,5))
plt.scatter(bbox_heights, distances, s=50, label="Measured")
plt.plot(h_vals, a / h_vals + b, 'r', label="Model")
plt.xlabel("Bounding Box Height (px)")
plt.ylabel("Distance (cm)")
plt.title("Camera Distance Calibration (Black Box)")
plt.legend()
plt.grid()
plt.show()
