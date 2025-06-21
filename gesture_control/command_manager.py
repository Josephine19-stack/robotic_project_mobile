import time
from utils.utils_tello import send_tello_command

class CommandManager:
    def __init__(self, tello):
        self.tello = tello
        self.is_flying = False
        self.last_command_time = 0
        self.command_delay = 1.0  # secondes
        self.allowed_first_gesture = "OPEN_PALM"
    
    def try_send_command(self, gesture):
        current_time = time.time()

        # Trop tôt pour envoyer une nouvelle commande
        if (current_time - self.last_command_time) < self.command_delay:
            return  # silencieux

        # Si drone est au sol, seule commande possible est "OPEN_PALM"
        if not self.is_flying:
            if gesture != self.allowed_first_gesture:
                print(f"[Refusé] Geste '{gesture}' ignoré : le drone est au sol.")
                return
        else:
            # Si le drone est déjà en vol, interdire un décollage
            if gesture == self.allowed_first_gesture:
                print(f"[Refusé] Geste '{gesture}' ignoré : le drone est déjà en vol.")
                return

        # Envoi de la commande
        result = send_tello_command(self.tello, gesture)
        if result is not None:
            self.is_flying = result
        self.last_command_time = current_time
