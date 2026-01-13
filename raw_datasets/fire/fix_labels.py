import os

LABEL_ROOT = "ai_fire_rover/raw_datasets/fire"

for split in ["train", "valid", "test"]:
    label_dir = os.path.join(LABEL_ROOT, split, "labels")

    for file in os.listdir(label_dir):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(label_dir, file)

        with open(path, "r") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                parts[0] = "0"  # remap class 1 -> 0
            new_lines.append(" ".join(parts) + "\n")

        with open(path, "w") as f:
            f.writelines(new_lines)

print("Label remapping complete.")
