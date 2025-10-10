import pygame

class Dropdown:
    def __init__(self, pos, font, options, default_index=0, on_select=None, width=None):
        """
        pos: (x, y) posición del dropdown
        font: fuente de texto
        options: lista de strings (las opciones del menú)
        default_index: índice de la opción seleccionada por defecto
        on_select: callback que se llama al seleccionar una opción (opcional)
        width: ancho fijo opcional (si None se ajusta al texto más largo)
        """
        self.pos = pos
        self.font = font
        self.options = options
        self.on_select = on_select
        self.selected_index = default_index
        self.is_open = False

        # Estilos visuales
        self.bg_color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.option_bg_color = (200, 200, 200)
        self.option_hover_color = (180, 180, 180)
        self.option_text_color = (0,0,0)
        self.border_radius = 6
        self.padding_x = 16
        self.padding_y = 10

        # Calcular ancho según el texto más largo
        if width is None:
            max_width = max(font.size(opt)[0] for opt in options)
            self.width = max_width + self.padding_x * 2
        else:
            self.width = width

        # Altura de una opción
        self.option_height = font.get_height() + self.padding_y * 2
        self.rect = pygame.Rect(pos[0], pos[1], self.width, self.option_height)

    def draw(self, surface):
        # --- DIBUJAR BOTÓN PRINCIPAL ---
        color = self.bg_color
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            color = self.hover_color

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        text = self.font.render(self.options[self.selected_index], True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


        # --- DIBUJAR OPCIONES DESPLEGADAS ---
        if self.is_open:
            for i, opt in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + (i + 1) * self.option_height,
                    self.width,
                    self.option_height,
                )

                # Cambiar color si el mouse está sobre la opción
                if option_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surface, self.option_hover_color, option_rect, border_radius=self.border_radius)
                else:
                    pygame.draw.rect(surface, self.option_bg_color, option_rect, border_radius=self.border_radius)

                # Dibujar texto de la opción
                text = self.font.render(opt, True, self.option_text_color)
                text_rect = text.get_rect(center=option_rect.center)
                surface.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            if self.rect.collidepoint(mouse_pos):
                # Clic sobre el botón principal → abrir/cerrar menú
                self.is_open = not self.is_open
            elif self.is_open:
                # Clic sobre alguna opción desplegada
                for i, opt in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + (i + 1) * self.option_height,
                        self.width,
                        self.option_height,
                    )
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.is_open = False
                        if self.on_select:
                            self.on_select(opt)
                        break
                else:
                    # Clic fuera del menú → cerrar
                    self.is_open = False

    def get_selected(self):
        """Devuelve el texto de la opción actualmente seleccionada."""
        return self.options[self.selected_index]

    def update_pos(self, pos):
        """Actualiza la posición del dropdown."""
        self.pos = pos
        self.rect.topleft = pos



""" Ejemplo de uso
dropdown = Dropdown(
    pos=(300, 200),
    font=font,
    options=["Fácil", "Normal", "Difícil"],
    default_index=1,
    on_select=on_select,
)

running = True
while running:
    screen.fill((25, 25, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        dropdown.handle_event(event)

    dropdown.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
"""
