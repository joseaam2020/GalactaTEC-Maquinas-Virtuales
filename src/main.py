# Example file showing a basic pygame "game loop"
import pygame
from screens.options import Options
from screens.main_window import main_window
from screens.new_player import RegisterWindow
from screens.hall_fame import HallOfFame
from screens.edit_playthrough import EditPlaythrough
from screens.recover_password import RecoverPassword
from widgets.textinput import TextInput
from screens.start_playthrough import Level1

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

class StateManager:
    def __init__(self):
        self.screen = screen
        self.states = {
            "MAIN": main_window(self),
            "OPTIONS": Options(self),
            "REGISTER": RegisterWindow(self),
            "HALL_FAME": HallOfFame(self),
            "EDIT_PLAYTHROUGH" : EditPlaythrough(self),
            "RECOVER_PASSWORD" : RecoverPassword(self),
            "LEVEL_1" : Level1(self)
        }
        self.current_state = self.states["MAIN"]  # arranca en login

    def change_state(self, new_state):
        if new_state in self.states:
            self.current_state = self.states[new_state]

            # Limpiar todos los TextInput cuando la ventana los tenga
            for attr_name in dir(self.current_state):
                attr = getattr(self.current_state, attr_name)
                if isinstance(attr, TextInput):
                    attr.clear()
        else:
            print(f"Estado '{new_state}' no existe")

    def run(self):
        while True:
            dt = clock.tick(60) / 1000
            self.current_state.handle_events()
            self.current_state.update(dt)
            self.current_state.draw(screen)
            pygame.display.flip()

if __name__ == "__main__":
    game = StateManager()
    game.run()

