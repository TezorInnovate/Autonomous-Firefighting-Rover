# modules/flow_logger.py

import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "water_usage_log.txt")

# ------------------ INIT ------------------
def _ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

_ensure_log_dir()

# ------------------ LOGGER ------------------
def log_water_usage(flow_pulses: int):
    """
    Log water usage pulses with timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | FLOW_PULSES: {flow_pulses}\n"

    with open(LOG_FILE, "a") as f:
        f.write(entry)

    print(f"[FLOW LOGGER] Water usage logged: {flow_pulses} pulses")


def log_event(message: str):
    """
    Generic event logger (optional utility)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | EVENT: {message}\n"

    with open(LOG_FILE, "a") as f:
        f.write(entry)

    print(f"[FLOW LOGGER] Event logged: {message}")
