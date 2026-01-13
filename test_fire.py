# test_fire_inference.py

from ultralytics import YOLO

# Load trained model
model = YOLO("runs/train/fire_model/weights/best.pt")

# Run inference on a single test image
results = model.predict("datasets/fire/test/images/sample.jpg", show=True, conf=0.25)
