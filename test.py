import os

cache = "datasets/fire/train/labels.cache"
if os.path.exists(cache):
    os.remove(cache)
    print("Cache deleted")
else:
    print("Cache not found")
