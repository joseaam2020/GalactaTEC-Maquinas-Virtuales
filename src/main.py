# Example file showing a basic pygame "game loop"
import pygame
from screens.options import Options
from screens.hall_fame import HallOfFame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

class StateManager:
    def __init__(self):
        self.states = {
            "OPTIONS": Options(self),
            "HALL_FAME": HallOfFame(self), 
        }
        self.current_state = self.states["OPTIONS"]

    def change_state(self, new_state):
        if new_state in self.states:
            self.current_state = self.states[new_state]
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

