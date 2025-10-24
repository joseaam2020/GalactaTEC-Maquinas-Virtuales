import pygame

class UserInfo:
    def __init__(self, font, pos, size, name="Available", photo="./resources/imgs/disponible.png", score=0):
        self.font = font
        self.pos = pos  # (x, y)
        self.size:list = size  # (width, height)
        self.name = name
        self.score = score

        # Cargar imagen del usuario
        try:
            self.image = pygame.image.load(photo).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, size)
        except pygame.error:
            print(f"Error cargando imagen: {photo}")
            self.image = pygame.Surface(size)
            self.image.fill((100, 100, 100))  # Fallback gris

        # Crear rectángulo principal
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

        # Colores de texto
        self.color_name = (255, 255, 255)
        self.color_score = (200, 200, 0)

        # Fondo opcional (puedes personalizarlo)
        self.bg_color = (40, 40, 40)
        self.border_radius = 10

    def draw(self, surface):
        # Dibujar fondo del widget
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        # Coordenadas base
        x, y = self.rect.topleft
        width, height = self.rect.size

        # Dibujar imagen centrada en la parte superior
        img_rect = self.image.get_rect(center=(x + width // 2, y + height // 3))
        surface.blit(self.image, img_rect)

        # Renderizar textos
        text_name = self.font.render(self.name, True, self.color_name)
        text_score = self.font.render(f"Score: {self.score}", True, self.color_score)

        # Posicionar textos centrados bajo la imagen
        name_rect = text_name.get_rect(center=(x + width // 2, img_rect.bottom + 25))
        score_rect = text_score.get_rect(center=(x + width // 2, name_rect.bottom + 10))

        # Dibujar textos
        surface.blit(text_name, name_rect)
        surface.blit(text_score, score_rect)

    def update_info(self, name=None, photo=None, score=None):
        """Permite actualizar la información del widget dinámicamente."""
        if name is not None:
            self.name = name
        if score is not None:
            self.score = score
        if photo is not None:
            try:
                self.image = pygame.image.load(photo).convert_alpha()
                self.image = pygame.transform.smoothscale(self.image, self.size)
            except pygame.error:
                print(f"Error actualizando imagen: {photo}")

    def update_pos(self, pos):
        """Mueve el widget a una nueva posición."""
        self.pos = pos
        self.rect.topleft = pos

