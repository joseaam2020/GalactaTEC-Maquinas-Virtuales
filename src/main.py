# Example file showing a basic pygame "game loop"
import random
import pygame
from screens.options import Options
from screens.main_window import main_window
from screens.new_player import RegisterWindow
from screens.hall_fame import HallOfFame
from screens.edit_playthrough import EditPlaythrough
from screens.recover_password import RecoverPassword
from widgets.textinput import TextInput
from screens.start_playthrough import Level1
from assets.sound_manager import SoundManager
from screens.change_password import ChangePassword
from screens.edit_user import EditUser
from screens.end_game import EndGameScreen


# pygame setup
pygame.init()
SoundManager.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

class StateManager:
    def __init__(self):
        self.screen = screen
        self.current_player = None # Para indicar el jugador activo
        self.states = {
            "MAIN": main_window(self),
            "OPTIONS": Options(self),
            "REGISTER": RegisterWindow(self),
            "HALL_FAME": HallOfFame(self),
            "EDIT_PLAYTHROUGH" : EditPlaythrough(self),
            "RECOVER_PASSWORD" : RecoverPassword(self),
            "LEVEL_1" : Level1(self),
            "CHANGE_PASSWORD": ChangePassword(self),
            "EDIT_USER": EditUser(self),
            "END_GAME": EndGameScreen(self),
        }
        self.current_state = self.states["MAIN"]  # arranca en login
        self.current_email = None
        self.players = {}
        self.patterns = {}

    
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

    def start_playthrough(self):
        logged_users = list(main_window.logged_users)

        # Jugador principal
        first_player = logged_users[0]
        player_1_info = self.players[first_player]

        # Segundo jugador (opcional)
        if len(logged_users) > 1:
            random.shuffle(logged_users)
            second_player = logged_users[1]
            player_2_info = self.players[second_player]
        else:
            second_player = None
            player_2_info = None

        #Crear un nuevo Level1 SIEMPRE
        from screens.start_playthrough import Level1
        level = Level1(self)

        # Cambiar imagen de la nave
        level.jugador.cambiar_imagen(player_1_info["ship_image"])

        # User Info
        level.user_1_info.update_info(first_player, player_1_info["photo_path"], 0)

        if second_player:
            level.user_2_info.update_info(second_player, player_2_info["photo_path"], 0)
        else:
            level.user_2_info = None

        # Patrón enemigo
        level.tipo_patron = self.patterns[first_player][1]

        # Música
        SoundManager.cargar_musica("", player_1_info['music_pref'])

        #Cambiar estado a este nuevo nivel
        self.current_state = level

if __name__ == "__main__":
    game = StateManager()
    game.run()

