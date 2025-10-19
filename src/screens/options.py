import pygame
from widgets.button import Button
from screens.main_window import main_window

class Options:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)

        # Cargar imagen de fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Definimos los textos de los botones
        self.buttons_data = [
            "Edit User",
            "Hall of Fame",
            "Edit Playthrough",
            "Add Players",
            "Start Playthrough",
            "Exit Game",
        ]

        # Creamos los botones
        self.buttons = []
        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Hall of Fame":
                    on_click = self.game.change_state
                    args = "HALL_FAME"
                case "Edit Playthrough":
                    on_click = self.game.change_state
                    args = "EDIT_PLAYTHROUGH"
                case "Add Players":
                    on_click = self.on_sign_in
                    args = "MAIN"
            self.buttons.append(
                Button(
                    text=txt,
                    font=self.font,
                    pos=(0, 0),
                    on_click=on_click,
                    args=args
                )
            )


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.change_state("LEVEL1")

            # Pasar eventos a todos los botones
            for b in self.buttons:
                b.handle_event(event)

    def update_layout(self, screen):
        """Actualiza posiciones y tamaños según el tamaño de la pantalla."""
        width, height = screen.get_size()
        button_height = height // (len(self.buttons) + 2)
        y_offset = button_height

        for i, button in enumerate(self.buttons):
            # Escalar el tamaño de fuente proporcionalmente
            scale_factor = width / 800  # suponiendo 800 como ancho base
            font_size = int(40 * scale_factor)
            button.font = pygame.font.Font(None, font_size)

            # Actualizar texto y tamaño
            button.update_text(button.text)  # corregido: era uptdate_text

            # Centrar horizontalmente
            x = (width - button.width) // 2
            y = y_offset + i * button_height
            button.update_pos((x, y))

    def update(self, dt):
        pass

    def draw(self, screen):
        # Dibujar fondo escalado
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        # Actualizar layout y dibujar botones
        self.update_layout(screen)
        for button in self.buttons:
            button.draw(screen)

    def on_sign_in(self, args):
        if not main_window.signed_in:
            main_window.signed_in = True 
        self.game.change_state(args)
