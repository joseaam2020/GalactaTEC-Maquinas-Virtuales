import pygame

class UserInfo:
    def __init__(self, font, pos, size, nombre="Available", foto="./resources/imgs/disponible.png", puntaje=0):
        self.font = font
        self.pos = pos  # (x, y)
        self.size:list = size  # (width, height)
        self.nombre = nombre
        self.puntaje = puntaje

        # Cargar imagen del usuario
        try:
            self.image = pygame.image.load(foto).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, size)
        except pygame.error:
            print(f"Error cargando imagen: {foto}")
            self.image = pygame.Surface(size)
            self.image.fill((100, 100, 100))  # Fallback gris

        # Crear rectángulo principal
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

        # Colores de texto
        self.color_nombre = (255, 255, 255)
        self.color_puntaje = (200, 200, 0)

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
        text_nombre = self.font.render(self.nombre, True, self.color_nombre)
        text_puntaje = self.font.render(f"Score: {self.puntaje}", True, self.color_puntaje)

        # Posicionar textos centrados bajo la imagen
        nombre_rect = text_nombre.get_rect(center=(x + width // 2, img_rect.bottom + 15))
        puntaje_rect = text_puntaje.get_rect(center=(x + width // 2, nombre_rect.bottom + 10))

        # Dibujar textos
        surface.blit(text_nombre, nombre_rect)
        surface.blit(text_puntaje, puntaje_rect)

    def update_info(self, nombre=None, foto=None, puntaje=None):
        """Permite actualizar la información del widget dinámicamente."""
        if nombre is not None:
            self.nombre = nombre
        if puntaje is not None:
            self.puntaje = puntaje
        if foto is not None:
            try:
                self.image = pygame.image.load(foto).convert_alpha()
                self.image = pygame.transform.smoothscale(self.image, self.size)
            except pygame.error:
                print(f"Error actualizando imagen: {foto}")

    def update_pos(self, pos):
        """Mueve el widget a una nueva posición."""
        self.pos = pos
        self.rect.topleft = pos

