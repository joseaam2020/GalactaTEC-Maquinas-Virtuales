import pygame
from widgets import button
from widgets.button import Button
from widgets.userinfo import UserInfo
from register.bd import get_top_6_scores

class HallOfFame:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.Font(None, 80)
        self.font_user = pygame.font.Font(None, 16)

        # Fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Texto principal
        self.title_text = self.font_title.render("Hall of Fame", True, (255, 215, 0))
        self.title_rect = self.title_text.get_rect()

        scores = get_top_6_scores("./src/register/GalactaDB.db")

        # Widgets de usuarios (5 en total)
        self.users = []
        for player in scores:
            self.users.append(
                    UserInfo(
                        font=self.font_user,
                        pos=(0,0),
                        size=(120,120),
                        name=player,
                        photo=("./" + scores[player]['img_path']),
                        score=scores[player]['score']
                        ))

        for _ in range(6 - len(scores)):
            self.users.append(UserInfo(self.font_user, (0, 0), (120, 120)))

        # Botón de salida
        self.exit_button = Button("Return", (0, 0), pygame.font.Font(None, 50), on_click=self.game.change_state, args="OPTIONS")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            self.exit_button.handle_event(event)

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

    def update(self, dt):
        pass

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

