import msvcrt
from rover_movement import RoverMovement

def main():
    rover = RoverMovement(
        esp32_ip="192.168.4.1",
        port=3333,
        speed=200,
        turn_duration=0.35
    )

    print("\n--- WASD Rover Control (Windows) ---")
    print("W: Forward")
    print("S: Backward")
    print("A: Turn Left")
    print("D: Turn Right")
    print("X: Stop")
    print("+ / - : Speed up / down")
    print("Q: Quit\n")

    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8").lower()

                if key == "w":
                    rover.forward()

                elif key == "s":
                    rover.backward()

                elif key == "a":
                    rover.turn_left(45)

                elif key == "d":
                    rover.turn_right(45)

                elif key == "x":
                    rover.stop()

                elif key == "+":
                    rover.set_speed(rover.speed + 20)

                elif key == "-":
                    rover.set_speed(rover.speed - 20)

                elif key == "q":
                    break

    finally:
        rover.close()

if __name__ == "__main__":
    main()
