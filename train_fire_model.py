# train_fire_model.py

from ultralytics import YOLO
import torch

# --------------------------
# Main training function
# --------------------------
def main():
    # --------------------------
    # Check GPU availability
    # --------------------------
    if torch.cuda.is_available():
        device = 0  # CUDA device index (recommended for Ultralytics)
        print("GPU detected. Training on GPU.")
    else:
        device = "cpu"
        print("GPU not detected. Training on CPU (slower).")

    # --------------------------
    # Load YOLOv8 pretrained model
    # --------------------------
    model = YOLO("yolov8n.pt")

    # --------------------------
    # Training parameters
    # --------------------------
    data_path = "datasets/fire/data.yaml"
    epochs = 50
    img_size = 640
    batch_size = 16
    project_name = "runs/train"
    run_name = "fire_model"

    # --------------------------
    # Start training
    # --------------------------
    results = model.train(
        data=data_path,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        workers=8,        # Windows-safe now due to __main__ guard
        name=run_name,
        project=project_name,
        verbose=True,
        save=True
    )

    print("Training complete!")
    print("Best weights saved at:", results.best)


# --------------------------
# Windows multiprocessing fix
# --------------------------
if __name__ == "__main__":
    torch.multiprocessing.freeze_support()
    main()
    