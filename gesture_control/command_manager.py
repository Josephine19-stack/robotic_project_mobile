import time

from gesture_control.utils.utils_tello import send_tello_command

class CommandManager:
    """
    This class manages gesture-based commands sent to the Tello drone.  
    It enforces cooldowns between commands and controls whether takeoff or landing is allowed based on flight status.
    """
    def __init__(self, tello):
        self.tello = tello
        self.is_flying = False
        self.last_command_time = 0
        self.command_delay = 5.0  # secondes
        self.allowed_first_gesture = "OPEN_PALM"
    
    def try_send_command(self, gesture):
        current_time = time.time()

        # Too early to send a new command
        if (current_time - self.last_command_time) < self.command_delay:
            return  # silent

        # If the drone is on the ground, the only allowed command is "OPEN_PALM"
        if not self.is_flying:
            if gesture != self.allowed_first_gesture:
                print(f"[Refusé] Geste '{gesture}' ignoré : le drone est au sol.")
                return
        else:
            # If the drone is already flying, takeoff is not allowed
            if gesture == self.allowed_first_gesture:
                print(f"[Refusé] Geste '{gesture}' ignoré : le drone est déjà en vol.")
                return

        # Sending command
        result = send_tello_command(self.tello, gesture)
        if result is not None:
            self.is_flying = result
            
        self.last_command_time = current_time
