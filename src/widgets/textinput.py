import pygame

class TextInput:
    def __init__(self, pos, size, font, placeholder="", text_color=(255, 255, 255),
                 bg_color=(0, 0, 0), border_color=(200, 200, 200),
                 active_color=(100, 100, 255), password=False):
        self.rect = pygame.Rect(pos, size)
        self.font = font
        self.text = ""
        self.placeholder = placeholder
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.active_color = active_color
        self.active = False
        self.password = password  # 👈 nuevo parámetro

        self.text_surface = self.font.render(self.placeholder, True, (150, 150, 150))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode.isprintable():
                self.text += event.unicode

            # 🔒 Mostrar asteriscos si es password
            display_text = "*" * len(self.text) if self.password and self.text else self.text
            if not self.text:
                display_text = self.placeholder

            color = self.text_color if self.text else (150, 150, 150)
            self.text_surface = self.font.render(display_text, True, color)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        border_col = self.active_color if self.active else self.border_color
        pygame.draw.rect(surface, border_col, self.rect, 2)
        surface.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))

    def update_text(self, new_text):
        self.text = new_text
        display_text = "*" * len(self.text) if self.password else self.text
        self.text_surface = self.font.render(display_text, True, self.text_color)

    def get_value(self):
        return self.text

    def set_pos(self, pos):
        self.rect.topleft = pos

    def set_size(self, size):
        self.rect.size = size
