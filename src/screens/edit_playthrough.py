import pygame
from widgets.button import Button
from widgets.dropdown import Dropdown

class EditPlaythrough:
    def __init__(self, game):
        self.game = game

        # fuentes iniciales (se reasignan en update_layout)
        self.font_title = pygame.font.Font(None, 80)
        self.font_label = pygame.font.Font(None, 50)

        # fondo 
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # datos
        self.levels = [1, 2, 3]
        self.patterns = [f"Patrón {i}" for i in range(1, 6)]

        # widgets (creados con posición temporal (0,0); se posicionan en update_layout)
        self.dropdowns = []
        for i, lvl in enumerate(self.levels):
            dd = Dropdown(
                pos=(0, 0),
                font=self.font_label,
                options=self.patterns,
                default_index=0,
                on_select=(lambda opt, idx=i: self._on_select_pattern(idx, opt))
            )
            self.dropdowns.append(dd)

        # botones inferiores
        self.buttons = [
            Button(text="Save", pos=(0, 0), font=self.font_label, on_click=self.save_settings),
            Button(text="Return", pos=(0, 0), font=self.font_label, on_click=self.game.change_state, args="OPTIONS"),
        ]

        # texto de título (se vuelve a renderizar en update_layout)
        self.title_surface = self.font_title.render("Edit Playthrough", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect()

        # almacenamiento temporal de labels renderizados (se actualizan cada layout)
        self.header_surfaces = []
        self.row_label_surfaces = []

    def _on_select_pattern(self, idx, option_text):
        # callback opcional cuando se selecciona un patrón en nivel idx
        # por ahora solo imprimimos; sirve para debug o lógica adicional
        print(f"[Dropdown] Level {idx+1} seleccionó: {option_text}")

    def save_settings(self):
        # lee las opciones actuales de los dropdowns
        for i, dd in enumerate(self.dropdowns):
            selected = dd.get_selected()
            print(f"Level {i+1} -> {selected}")
        print("Settings saved (por ahora solo consola).")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # pasar eventos a dropdowns y botones
            for dd in self.dropdowns:
                dd.handle_event(event)
            for b in self.buttons:
                b.handle_event(event)

    def update_layout(self, screen):
        width, height = screen.get_size()
        scale = width / 800  # base 800 ancho

        # ===========================
        # Fuentes escaladas
        # ===========================
        title_size = max(28, int(72 * scale))
        label_size = max(16, int(36 * scale))
        button_size = max(18, int(36 * scale))

        self.font_title = pygame.font.Font(None, title_size)
        self.font_label = pygame.font.Font(None, label_size)

        # Título centrado arriba
        self.title_surface = self.font_title.render("Edit Playthrough", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(width // 2, int(height * 0.08)))

        # ===========================
        # Tabla: definiciones (2 columnas x 4 filas)
        # ===========================
        # filas: 0 = headers, 1..3 = levels 1..3
        row_height = max(int(self.font_label.get_height() * 1.8), int(height * 0.09))
        table_top = int(height * 0.18)

        col1_x = int(width * 0.30)
        col2_x = int(width * 0.70)

        # Headers
        header1 = self.font_label.render("Level", True, (255, 255, 255))
        header2 = self.font_label.render("Enemy pattern", True, (255, 255, 255))
        self.header_surfaces = [
            (header1, header1.get_rect(center=(col1_x, table_top))),
            (header2, header2.get_rect(center=(col2_x, table_top))),
        ]

        # Rows (levels)
        self.row_label_surfaces = []
        for i, lvl in enumerate(self.levels):
            y = table_top + (i + 1) * row_height
            lbl = self.font_label.render(f"{lvl}", True, (255, 255, 255))
            lbl_rect = lbl.get_rect(center=(col1_x, y))
            self.row_label_surfaces.append((lbl, lbl_rect))

            # actualizar dropdown visual (fuente, ancho y alto)
            dd = self.dropdowns[i]
            dd.font = self.font_label
            # recalcular ancho en base al texto más largo
            max_w = max(dd.font.size(opt)[0] for opt in dd.options)
            dd.width = max_w + dd.padding_x * 2
            dd.option_height = dd.font.get_height() + dd.padding_y * 2
            # actualizar rects internos
            dd.rect.width = dd.width
            dd.rect.height = dd.option_height
            # posicionar centrado en la segunda columna
            dd_x = int(col2_x - dd.width // 2)
            dd_y = int(y - dd.option_height // 2)
            dd.update_pos((dd_x, dd_y))

        # ===========================
        # Botones inferiores (recalcular tamaños y posiciones)
        # ===========================
        # actualizar fuente y recalcular tamaños en cada botón (Button no recalcula solo)
        for b in self.buttons:
            b.font = pygame.font.Font(None, button_size)
            # re-render del texto y recalculo de medidas (usamos atributos públicos del Button)
            b.text_surf = b.font.render(b.text, True, (255, 255, 255))
            b.text_rect = b.text_surf.get_rect()
            # recalcular tamaño total con padding
            try:
                px = b.padding_x
                py = b.padding_y
            except AttributeError:
                # en caso raro; valores por defecto
                px, py = 20, 10
            b.width = b.text_rect.width + px * 2
            b.height = b.text_rect.height + py * 2

        # posicionar: Save a la izquierda del centro, Return a la derecha
        button_y = int(height - max(80, 60 * scale))
        gap = int(20 * scale)
        total_w = self.buttons[0].width + gap + self.buttons[1].width
        start_x = width // 2 - total_w // 2

        self.buttons[0].update_pos((start_x, button_y))
        self.buttons[1].update_pos((start_x + self.buttons[0].width + gap, button_y))

    def update(self, dt):
        pass

    def draw(self, screen):
        # fondo escalado
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        # layout y render (aseguramos que cada frame el layout esté correcto)
        self.update_layout(screen)

        # dibujar título
        screen.blit(self.title_surface, self.title_rect)

        # dibujar headers
        for surf, rect in self.header_surfaces:
            screen.blit(surf, rect)

        # dibujar filas (labels) y dropdowns
        for lbl_surf, lbl_rect in self.row_label_surfaces:
            screen.blit(lbl_surf, lbl_rect)

        # primero dibujar todo normalmente
        for dd in self.dropdowns:
            if not dd.is_open:
                dd.draw(screen)

        # luego dibujar el que está abierto, para que quede arriba
        for dd in self.dropdowns:
            if dd.is_open:
                dd.draw(screen)

        # dibujar botones
        for b in self.buttons:
            b.draw(screen)
