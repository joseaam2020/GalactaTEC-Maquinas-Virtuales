import pygame

# Clase Botón
class Button:
    def __init__(self, text, pos, font, on_click=None,args=None):
        self.text = text
        self.font = font
        self.on_click = on_click
        self.selected = False
        self.args = args

        # Crear sonido
        try:
            self.click_sound = pygame.mixer.Sound("resources/audio/button.mp3")
        except pygame.error:
            print("Error creando sonido boton")
            self.click_sound = None  # En caso de que no haya sonido o mixer desactivado

        # Crear superficie del texto
        self.text_surf = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect()

        # Crear rectángulo con padding
        self.padding_x, self.padding_y = 20, 10
        width = self.text_rect.width + self.padding_x * 2
        height = self.text_rect.height + self.padding_y * 2
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

        # Guardar dimensiones como atributos accesibles
        self.width = width
        self.height = height

        # Colores
        self.color_default = (70, 70, 70)
        self.color_hover = (90, 90, 90)
        self.color_selected = (120, 120, 255)

    def draw(self, surface):
        # Determinar color según estado
        if self.selected:
            color = self.color_selected
        elif self.is_mouse_over():
            color = self.color_hover
        else:
            color = self.color_default

        # Dibujar fondo
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Dibujar texto centrado
        text_x = self.rect.x + (self.rect.width - self.text_rect.width) // 2
        text_y = self.rect.y + (self.rect.height - self.text_rect.height) // 2
        surface.blit(self.text_surf, (text_x, text_y))

    def is_mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        # Mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_mouse_over():
                self.click()

        # Teclado / control
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
        self.rect = pygame.Rect(pos[0], pos[1], self.width, self.height)


"""
# Ejemplo de uso
font = pygame.font.Font(None, 50)

def say_hello():
    print("¡Botón presionado!")

buttons = [
    Button("Jugar", (300, 200), font, say_hello),
    Button("Opciones", (300, 300), font),
    Button("Salir", (300, 400), font, lambda: exit())
]

selected_index = 0
buttons[selected_index].selected = True

running = True
while running:
    screen.fill((25, 25, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Manejo de botones
        for b in buttons:
            b.handle_event(event)

        # Navegación con teclado / control
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                buttons[selected_index].selected = False
                selected_index = (selected_index + 1) % len(buttons)
                buttons[selected_index].selected = True
            elif event.key == pygame.K_UP:
                buttons[selected_index].selected = False
                selected_index = (selected_index - 1) % len(buttons)
                buttons[selected_index].selected = True

    # Dibujar botones
    for b in buttons:
        b.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
"""
