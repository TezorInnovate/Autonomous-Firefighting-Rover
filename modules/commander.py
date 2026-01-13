# modules/commander.py
import time
import socket
import threading

import vision_ai
import rover_movement
import pump_control
import flow_logger

# ================== CONFIG ==================
ESP32_IP = "192.168.4.1"
ESP32_PORT = 3333

ARRIVAL_PIXEL_THRESHOLD = 200     # must match vision_ai
ALIGN_TOLERANCE_PX = 20

# ================== SOCKET ==================
esp32_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
esp32_sock.settimeout(2)
esp32_sock.connect((ESP32_IP, ESP32_PORT))
print("[COMMANDER] Connected to ESP32")

# ================== MODULES ==================
vision = vision_ai.FireVision()
movement = rover_movement.RoverMovement(esp32_sock)
pump = pump_control.PumpControl(esp32_sock)

# ================== FLAGS ==================
stop_flag = False
manual_override = False
fire_engaged = False   # 🔒 prevents repeat pumping

flow_logger.log_event("Autonomous mode started (Vision-only arrival logic)")

# ================== AUTONOMOUS LOOP ==================
def autonomous_loop():
    global fire_engaged

    while not stop_flag:
        if manual_override:
            time.sleep(0.1)
            continue

        vision.update_frame()

        if not vision.detect_fire():
            fire_engaged = False
            movement.stop()
            time.sleep(0.05)
            continue

        fire_center = vision.get_fire_center()
        if not fire_center:
            movement.stop()
            continue

        cx, cy = fire_center
        frame_h = vision.frame_height
        frame_cx = vision.center_x

        vertical_distance = frame_h - cy

        # ---------------- ALIGNMENT ----------------
        if cx < frame_cx - ALIGN_TOLERANCE_PX:
            movement.turn_left(forward=True)
            continue
        elif cx > frame_cx + ALIGN_TOLERANCE_PX:
            movement.turn_right(forward=True)
            continue

        # ---------------- ARRIVAL CHECK ----------------
        if vertical_distance <= ARRIVAL_PIXEL_THRESHOLD:
            if not fire_engaged:
                fire_engaged = True
                movement.stop()

                flow_logger.log_event(
                    f"Fire reached — activating pump (px={vertical_distance})"
                )

                pump.pump_on()

                # wait until fire disappears
                while vision.detect_fire():
                    vision.update_frame()
                    time.sleep(0.1)

                pump.pump_off()

                flow_logger.log_water_usage(0)
                flow_logger.log_event("Fire extinguished successfully")

            continue

        # ---------------- MOVE FORWARD ----------------
        movement.move_forward()
        time.sleep(0.05)

# ================== MANUAL MODE ==================
def manual_control():
    global manual_override
    print("Manual mode: W/A/S/D, X stop, Q quit")

    while manual_override:
        cmd = input("> ").strip().upper()

        if cmd == "W":
            movement.move_forward()
        elif cmd == "S":
            movement.move_backward()
        elif cmd == "A":
            movement.turn_left()
        elif cmd == "D":
            movement.turn_right()
        elif cmd == "X":
            movement.stop()
        elif cmd == "Q":
            manual_override = False
            movement.stop()
            print("Exiting manual mode")
            break

# ================== START ==================
try:
    auto_thread = threading.Thread(target=autonomous_loop, daemon=True)
    auto_thread.start()

    while True:
        cmd = input("[M] Manual | CTRL+C Quit : ").strip().upper()
        if cmd == "M":
            manual_override = True
            threading.Thread(target=manual_control).start()

except KeyboardInterrupt:
    print("\n[COMMANDER] Shutting down...")
    stop_flag = True
    movement.stop()
    pump.pump_off()
    vision.shutdown()
    esp32_sock.close()
