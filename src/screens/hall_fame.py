import pygame
from widgets import button
from widgets.button import Button
from widgets.userinfo import UserInfo
from register.bd import get_top_6_scores, add_score
from widgets.helpbutton import HelpButton

class HallOfFame:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.Font(None, 80)
        self.font_user = pygame.font.Font(None, 16)

        # Para mensajes pop-up de nuevos puntajes
        self.popup_messages = []  # lista de (mensaje, tiempo_expiracion_ms)
        self.popup_duration = 2500  # ms que dura cada pop-up

        # Fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Texto principal
        self.title_text = self.font_title.render("Hall of Fame", True, (255, 215, 0))
        self.title_rect = self.title_text.get_rect()

        self.scores = get_top_6_scores("./src/register/GalactaDB.db")

        # Widgets de usuarios (5 en total)
        self.users = []
        for player in self.scores:
            self.users.append(
                    UserInfo(
                        font=self.font_user,
                        pos=(0,0),
                        size=(120,120),
                        name=player,
                        photo=(self.scores[player]['img_path']),
                        score=self.scores[player]['score']
                        ))

        for _ in range(6 - len(self.scores)):
            self.users.append(UserInfo(self.font_user, (0, 0), (120, 120)))

        # Botón de salida
        self.exit_button = Button("Return", (0, 0), pygame.font.Font(None, 50), on_click=self.return_to_options)

        # Boton de ayuda
        help_text = (
            "Welcome to the Hall of Fame!\n\n"
            "This screen displays the top 6 players based on their highest scores.\n"
            "Players are arranged in a pyramid layout, with the highest scorer at the top.\n\n"
            "Each player panel shows their name, score, and chosen profile picture.\n"
            "If there are less than 6 players, the remaining spots will appear empty.\n\n"
            "Click the 'Return' button at the bottom right to go back to the Options menu.\n"
            "Press ESC to close this help window."
        )
        self.help_button = HelpButton(
                font=pygame.font.Font(None,50),
                title="Hall of Fame",
                text=help_text,
                pos=(0,0),
                screen_size=[]
        )
 
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Pasar enventos a boton de exit
            self.exit_button.handle_event(event)

            # Pasar eventos a boton de ayuda
            self.help_button.handle_event(event)

    def update_layout(self, screen):
        """Ajusta el layout dinámicamente según el tamaño de la pantalla."""
        width, height = screen.get_size()

        # Escalar fuentes proporcionalmente
        scale_factor = width / 800
        title_size = int(80 * scale_factor)
        user_font_size = int(30 * scale_factor)

        self.font_title = pygame.font.Font(None, title_size)
        self.font_user = pygame.font.Font(None, user_font_size)

        # Actualizar título centrado arriba
        self.title_text = self.font_title.render("Hall of fame", True, (255, 215, 0))
        self.title_rect = self.title_text.get_rect(center=(width // 2, height * 0.1))

        # Dimensiones de los widgets
        user_width = int(150 * scale_factor)
        user_height = int(150 * scale_factor)
        spacing_x = int(user_width * 0.3)
        spacing_y = int(user_height * 0.8)

        # Coordenadas base (centro)
        center_x = width // 2
        start_y = int(height * 0.35)

        # Distribución piramidal
        positions = [
            [(center_x, start_y)],  # Nivel 1 (1 usuario)
            [
                (center_x - (user_width + spacing_x) // 2, start_y + spacing_y),
                (center_x + (user_width + spacing_x) // 2, start_y + spacing_y),
            ],
            [
                (center_x - (user_width + spacing_x),
                 start_y + 2 * spacing_y),
                (center_x,
                 start_y + 2 * spacing_y),
                (center_x + (user_width + spacing_x),
                 start_y + 2 * spacing_y),
            ],
        ]

        # Asignar posiciones a los widgets (total 5 usuarios)
        idx = 0
        for level in positions:
            for (x, y) in level:
                if idx < len(self.users):
                    # Centrar los widgets respecto a su tamaño
                    pos = (x - user_width // 2, y - user_height // 2)
                    self.users[idx].size = [user_width, user_height]
                    self.users[idx].update_pos(pos)
                    self.users[idx].font = self.font_user
                    idx += 1

        # Posicionar botón de salida en esquina inferior derecha
        button_padding = 20
        self.exit_button.font = pygame.font.Font(None, int(50 * scale_factor))
        self.exit_button.update_text("Return")
        self.exit_button.update_pos((
            width - self.exit_button.width - button_padding,
            height - self.exit_button.height - button_padding
        ))

        # Boton de ayuda
        margin = 20  # margen desde los bordes
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width,height]
        self.help_button.update_pos([final_x,final_y])
         

    def update(self, dt):
        # Limpiar mensajes pop-up expirados
        ahora = pygame.time.get_ticks()
        self.popup_messages = [ (msg, t_exp) for (msg, t_exp) in self.popup_messages if t_exp > ahora ]

    def draw(self, screen):
        # Fondo escalado
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        # Actualizar layout antes de dibujar
        self.update_layout(screen)

        # Dibujar título
        screen.blit(self.title_text, self.title_rect)

        # Dibujar usuarios
        for user in self.users:
            user.draw(screen)

        # Dibujar botón de salida
        self.exit_button.draw(screen)

        # Dibujar boton de ayuda
        self.help_button.draw(screen)

        # Dibujar pop-ups de nuevos puntajes en la esquina superior izquierda
        if self.popup_messages:
            font_popup = pygame.font.Font(None, 24)
            x0, y0 = 20, 20  # margen desde la esquina
            for i, (msg, _) in enumerate(self.popup_messages):
                surf = font_popup.render(msg, True, (255,255,255))
                bg_rect = surf.get_rect(topleft=(x0, y0 + i*50))
                # Fondo semitransparente
                s = pygame.Surface((bg_rect.width+30, bg_rect.height+10), pygame.SRCALPHA)
                s.fill((30,30,30, 210))
                screen.blit(s, (bg_rect.x-15, bg_rect.y-5))
                screen.blit(surf, bg_rect)

    def return_to_options(self):
        """Reinicia Level1 y vuelve a OPTIONS."""
        try:
            self.game.restart_level()
        except Exception:
            pass
        self.game.change_state("OPTIONS")

    def set_new_scores(self,new_scores):
        for new_player in new_scores:
                try:
                    add_score(new_player,new_scores[new_player]["score"],"./src/register/GalactaDB.db")
                except Exception as e:
                    print(f"Error registrando puntajes nuevos: {e}")

    def update_scores(self):
        """Actualiza los puntajes y los widgets de usuario con los 6 mejores puntajes actuales. Si hay cambios, muestra pop-ups."""
        old_scores = self.scores.copy() if hasattr(self, 'scores') else {}
        new_scores = get_top_6_scores("./src/register/GalactaDB.db")
        mensajes = []
        # Comparar scores antiguos y nuevos
        for player in new_scores:
            nuevo = new_scores[player]['score']
            anterior = old_scores.get(player, {}).get('score', None)
            if anterior is None or nuevo != anterior:
                mensajes.append(f"¡Nuevo puntaje para {player}: {nuevo} pts!")
        # Guardar mensajes con tiempo de expiración
        ahora = pygame.time.get_ticks()
        for m in mensajes:
            self.popup_messages.append((m, ahora + self.popup_duration))
        # Actualizar scores y widgets
        self.scores = new_scores
        self.users = []
        for player in self.scores:
            self.users.append(
                UserInfo(
                    font=self.font_user,
                    pos=(0, 0),
                    size=(120, 120),
                    name=player,
                    photo=(self.scores[player]['img_path']),
                    score=self.scores[player]['score']
                )
            )
        for _ in range(6 - len(self.scores)):
            self.users.append(UserInfo(self.font_user, (0, 0), (120, 120)))


