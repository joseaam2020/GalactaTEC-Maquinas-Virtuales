import pygame
import random
from assets.sound_manager import SoundManager
from widgets.button import Button
from screens.main_window import main_window
from widgets.helpbutton import HelpButton
from screens.edit_user import EditUser

class Options:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Botones principales
        self.buttons_data = [
            "Edit User",
            "Hall of Fame",
            "Edit Playthrough",
            "Add Players",
            "Start Playthrough",
            "Exit Game",
        ]
        self.buttons = []
        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Hall of Fame":
                    on_click = self.game.change_state
                    args = "HALL_FAME"
                case "Edit Playthrough":
                    on_click = self.edit_game
                    args = "EDIT_PLAYTHROUGH"
                case "Add Players":
                    on_click = self.on_sign_in
                    args = "MAIN"
                case "Exit Game":
                    on_click = self.exit_game
                    args = None
                case "Start Playthrough":
                    on_click = self.start_game
                    args = "LEVEL_1"
                case "Edit User":
                    on_click = self.edit_user
                    args = "EDIT_USER"
            self.buttons.append(
                Button(
                    text=txt,
                    font=self.font,
                    pos=(0, 0),
                    on_click=on_click,
                    args=args
                )
            )

        # Botón de ayuda
        help_text = (
            "This is the game's options menu. From here, you can:\n\n"
            "- Edit User: Change your profile's information.\n\n"
            "- Hall of Fame: View the top scores and achievements.\n\n"
            "- Edit Playthrough: Change de enemy ship's behaviour.\n\n"
            "- Add Players: Register another persona to play together.\n\n"
            "- Start Playthrough: Begin a new playthrough session.\n\n"
            "- Exit Game: Close the game and return to the desktop.\n\n"
        )
        self.help_button = HelpButton(font=self.font, title="Options", text=help_text, pos=(0,0), screen_size=[])

        # ---------------- PESTAÑAS DE JUGADORES ----------------
        self.active_player = None  # jugador activo
        self.player_tabs = []      # botones de pestañas

    # ---------------- EVENTOS ----------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.change_state("LEVEL_1")

            # Botones principales
            for b in self.buttons:
                b.handle_event(event)

            # Pestañas de jugadores
            for tab in self.player_tabs:
                tab.handle_event(event)

            # Botón de ayuda
            self.help_button.handle_event(event)

    # ---------------- LAYOUT ----------------
    def update_layout(self, screen):
        width, height = screen.get_size()
        button_height = height // (len(self.buttons) + 2)
        y_offset = button_height

        # Actualizar botones principales
        for i, button in enumerate(self.buttons):
            scale_factor = width / 800
            font_size = int(40 * scale_factor)
            button.font = pygame.font.Font(None, font_size)
            button.update_text(button.text)
            x = (width - button.width) // 2
            y = y_offset + i * button_height
            button.update_pos((x, y))

        # Botón de ayuda
        margin = 20
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width,height]
        self.help_button.update_pos([final_x,final_y])

        # ---------------- PESTAÑAS DE JUGADORES ----------------
        tab_width = 150
        tab_height = 40
        tab_spacing = 20
        tab_y = 50
        self.player_tabs = []

        for i, username in enumerate(list(main_window.logged_users)):
            def make_on_click(u=username):
                return lambda: self.set_active_player(u)
            
            tab_button = Button(
                text=username,
                font=pygame.font.Font(None, 30),
                pos=(50, tab_y + i * (tab_height + tab_spacing)),
                on_click=make_on_click()
            )
            tab_button.width = tab_width
            tab_button.height = tab_height
            self.player_tabs.append(tab_button)

            # Establecer el primer jugador como activo si no hay ninguno
            if self.active_player is None:
                self.active_player = username

    # ---------------- DIBUJADO ----------------
    def draw(self, screen):
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        self.update_layout(screen)

        # Dibujar botones principales
        for button in self.buttons:
            button.draw(screen)

        # Verificar si el jugador activo sigue existiendo
        if self.active_player and self.active_player not in main_window.logged_users:
            # Si el jugador activo fue eliminado o renombrado, seleccionar otro
            if main_window.logged_users:
                self.active_player = list(main_window.logged_users)[0]
                self.game.current_player = self.active_player
            else:
                self.active_player = None
                self.game.current_player = None

        # Dibujar pestañas de jugadores
        for tab in self.player_tabs:
            # Resaltar jugador activo
            if tab.text == self.active_player:
                pygame.draw.rect(screen, (100, 200, 250), tab.rect)
            tab.draw(screen)

        # Dibujar botón de ayuda
        self.help_button.draw(screen)


    # ---------------- FUNCIONES ----------------
    def set_active_player(self, username):
        self.active_player = username
        self.game.current_player = username
        print(f"Jugador activo: {self.active_player}")
        # Aquí podrías cargar configuraciones específicas del jugador

    def on_sign_in(self, args):
        if not main_window.signed_in:
            main_window.signed_in = True
            self.game.current_state.needs_reset = True
        self.game.change_state(args)

    def exit_game(self):
        pygame.quit()
        exit()

    def update(self, dt):
        pass

    def start_game(self,args):
        self.game.start_playthrough()


    def edit_game(self,args):
        # Consigue patrones actuales
        patterns = self.game.patterns[self.active_player]
        # Actualiza los valores del edit_playthrough
        self.game.states[args].update_dropdowns_from_patterns(patterns)
        # Entra en edit playthrough
        self.game.change_state(args)

    def edit_user(self, args):

        # Entra en edit user
        self.game.change_state(args)

        # Actualiza los valores del edit_playthrough
        self.game.states[args].load_player_data(self.active_player)
        



