import pygame
from widgets.button import Button

class HelpButton(Button):
    def __init__(self, pos, font, title, text, screen_size):
        super().__init__("?", pos, font, on_click=self.toggle_help)
        self.help_visible = False
        self.title = title
        self.text = text
        self.screen_size = screen_size
        self.help_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 36)

        # Colores
        self.bg_color = (40, 40, 40)
        self.text_color = (255, 255, 255)

        # Calculado dinámicamente
        self.help_rect = None

    def toggle_help(self):
        self.help_visible = not self.help_visible
        if self.click_sound:
            self.click_sound.play()

    def draw(self, surface):
        # Dibuja el botón "?"
        super().draw(surface)

        # Dibuja cuadro de ayuda si está activo
        if self.help_visible:
            self.draw_help_box(surface)

    def draw_help_box(self, surface):
        # Crear superficies de texto
        title_surf = self.title_font.render(self.title, True, self.text_color)
        text_lines = self.text.split("\n")
        text_surfs = [self.help_font.render(line, True, self.text_color) for line in text_lines]

        # Determinar dimensiones del cuadro
        padding = 20
        spacing = 10
        width = max(title_surf.get_width(), max((ts.get_width() for ts in text_surfs), default=0)) + padding * 2
        height = title_surf.get_height() + spacing + len(text_surfs) * self.help_font.get_height() + padding * 2

        screen_w, screen_h = self.screen_size
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.help_rect = pygame.Rect(x, y, width, height)

        # Dibujar fondo del cuadro
        pygame.draw.rect(surface, self.bg_color, self.help_rect, border_radius=12)

        # Dibujar título centrado
        title_x = x + (width - title_surf.get_width()) // 2
        title_y = y + padding
        surface.blit(title_surf, (title_x, title_y))

        # Dibujar texto línea por línea
        current_y = title_y + title_surf.get_height() + spacing
        for line_surf in text_surfs:
            line_x = x + (width - line_surf.get_width()) // 2
            surface.blit(line_surf, (line_x, current_y))
            current_y += self.help_font.get_height()

    def handle_event(self, event):
        # Lógica del botón
        super().handle_event(event)

        # Cerrar con ESC si está visible
        if event.type == pygame.KEYDOWN and self.help_visible:
            if event.key == pygame.K_ESCAPE:
                self.help_visible = False
