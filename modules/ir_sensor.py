# modules/ir_sensor.py

class IRSensor:
    """
    Decodes IR / flame sensor telemetry from ESP32

    Bitmask definition:
        bit 0 -> LEFT
        bit 1 -> CENTER
        bit 2 -> RIGHT
    """

    LEFT = 0b001
    CENTER = 0b010
    RIGHT = 0b100

    def __init__(self):
        self.last_state = {
            "left": False,
            "center": False,
            "right": False
        }

    # ------------------ CORE DECODER ------------------
    def decode_bitmask(self, ir_value: int) -> dict:
        """
        Convert bitmask into readable state dictionary
        """
        state = {
            "left": bool(ir_value & self.LEFT),
            "center": bool(ir_value & self.CENTER),
            "right": bool(ir_value & self.RIGHT)
        }

        self.last_state = state
        return state

    # ------------------ COMMANDER HELPERS ------------------
    def any_fire_detected(self, ir_value: int) -> bool:
        """
        Returns True if any IR sensor is triggered
        """
        return ir_value != 0

    def is_center_fire(self, ir_value: int) -> bool:
        """
        Returns True if center sensor detects flame
        """
        return bool(ir_value & self.CENTER)

    def flame_direction(self, ir_value: int) -> str:
        """
        Returns dominant flame direction
        """
        state = self.decode_bitmask(ir_value)

        if state["center"]:
            return "CENTER"
        if state["left"] and not state["right"]:
            return "LEFT"
        if state["right"] and not state["left"]:
            return "RIGHT"
        if state["left"] and state["right"]:
            return "WIDE"

        return "NONE"

    # ------------------ DEBUG ------------------
    def __str__(self):
        return f"IR State -> {self.last_state}"
