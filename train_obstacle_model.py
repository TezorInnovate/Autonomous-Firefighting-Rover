# train_obstacle_model.py

from ultralytics import YOLO
import torch

# --------------------------
# Main training function
# --------------------------
def main():
    # --------------------------
    # GPU check
    # --------------------------
    if torch.cuda.is_available():
        device = 0  # CUDA device index (recommended)
        print("GPU detected. Training on GPU.")
    else:
        device = "cpu"
        print("GPU not detected. Training on CPU.")

    # --------------------------
    # Load YOLOv8 model
    # --------------------------
    model = YOLO("yolov8n.pt")  # nano is enough for obstacles

    # --------------------------
    # Training config
    # --------------------------
    results = model.train(
        data="datasets/obstacle/data.yaml",
        epochs=40,            # smaller dataset → fewer epochs
        imgsz=640,
        batch=8,              # safe for small dataset + 4GB VRAM
        device=device,
        workers=8,            # safe due to __main__ guard
        project="runs/train",
        name="obstacle_model",
        verbose=True,
        save=True
    )

    print("Obstacle training complete!")
    print("Best weights saved at:", results.best)


# --------------------------
# Windows multiprocessing fix
# --------------------------
if __name__ == "__main__":
    torch.multiprocessing.freeze_support()
    main()
