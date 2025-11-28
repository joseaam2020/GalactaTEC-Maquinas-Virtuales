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
        # Registrar mapping de usernames para que `Level` reconozca jugadores activos
        try:
            level.player_usernames = {1: first_player}
            if second_player:
                level.player_usernames[2] = second_player
            # Asegurar que Level sepa cuántos jugadores hay
            level.total_jugadores = 1 if not second_player else 2
            # Establecer current_player en el manager
            self.current_player = first_player
        except Exception:
            pass

        # Actualizar imagen y user info (mantener compatibilidad)
        try:
            level.jugador.cambiar_imagen(player_1_info.get("ship_image"))
        except Exception:
            pass
        try:
            level.user_1_info.update_info(first_player, player_1_info.get("photo_path"), 0)
        except Exception:
            pass
        if second_player:
            try:
                level.user_2_info.update_info(second_player, player_2_info.get("photo_path"), 0)
            except Exception:
                pass
        else:
            level.user_2_info = None

        # Intentar aplicar patrones y música según preferencias del usuario
        try:
            if first_player in self.patterns:
                level.tipo_patron = self.patterns.get(first_player, {}).get(1, level.tipo_patron)
        except Exception:
            pass
        try:
            SoundManager.cargar_musica("", player_1_info.get('music_pref'))
        except Exception:
            pass

        # Informar al Level que aplique mapping y actualice widgets/música
        try:
            if hasattr(level, 'apply_player_usernames'):
                level.apply_player_usernames()
        except Exception:
            try:
                level.update_userinfo_names()
            except Exception:
                pass

        # Cambiar estado a este nuevo nivel
        self.current_state = level

if __name__ == "__main__":
    game = StateManager()
    game.run()

