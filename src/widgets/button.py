import pygame

class Button:
    def __init__(self, text, pos, font, on_click=None, args=None, image_path=None, size=None):
        self.text = text
        self.font = font
        self.on_click = on_click
        self.args = args
        self.selected = False
        self.image_path = image_path
        self.custom_size = size  # Guardamos el size ingresado
        self.highlighted = False 

        # Intentar cargar sonido
        try:
            self.click_sound = pygame.mixer.Sound("resources/audio/button.mp3")
        except pygame.error:
            print("Error creando sonido botón")
            self.click_sound = None

        # Crear superficie de texto
        self.text_surf = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect()

        # Calcular tamaño base
        self.padding_x, self.padding_y = 20, 10
        width = self.text_rect.width + self.padding_x * 2
        height = self.text_rect.height + self.padding_y * 2

        # Si se definió un tamaño custom, usarlo
        if self.custom_size:
            width, height = self.custom_size

        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.width, self.height = width, height

        # Cargar imagen si se pasó un path válido
        self.image = None
        if self.image_path:
            try:
                self.image = pygame.image.load(self.image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except Exception as e:
                print(f"Error cargando imagen del botón '{self.image_path}':", e)
                self.image = None

        # Colores
        self.color_default = (70, 70, 70)
        self.color_hover = (90, 90, 90)
        self.color_selected = (120, 120, 255)

    def draw(self, surface):
        # Determinar color
        if self.selected:
            color = self.color_selected
        elif self.is_mouse_over():
            color = self.color_hover
        else:
            color = self.color_default

        # Fondo del botón
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Dibujar imagen si existe
        if self.image:
            surface.blit(self.image, self.rect.topleft)

        # Dibujar texto centrado
        text_x = self.rect.x + (self.rect.width - self.text_rect.width) // 2
        text_y = self.rect.y + (self.rect.height - self.text_rect.height) // 2
        surface.blit(self.text_surf, (text_x, text_y))

        # Dibujar borde rojo si el botón está resaltado
        if self.highlighted:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 4, border_radius=8)

    def is_mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_mouse_over():
                self.click()
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.click()

    def click(self):
        if self.click_sound:
            self.click_sound.play()
        if self.on_click:
            if self.args:
                self.on_click(self.args)
            else:
                self.on_click()

    def update_text(self, text):
        self.text = text

    def update_pos(self, pos):
        self.rect.topleft = pos

    def update_image(self, image_path=None, size=None):
        """
        Permite cambiar la imagen del botón en tiempo de ejecución.
        """
        if image_path:
            self.image_path = image_path
            try:
                img = pygame.image.load(image_path).convert_alpha()
                if size:
                    img = pygame.transform.scale(img, size)
                    self.rect.size = size
                    self.width, self.height = size
                else:
                    img = pygame.transform.scale(img, (self.width, self.height))
                self.image = img
            except Exception as e:
                print("Error cargando imagen:", e)
                self.image = None
