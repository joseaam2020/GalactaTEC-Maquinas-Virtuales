import pygame
from widgets.button import Button
from widgets.dropdown import Dropdown
from widgets.helpbutton import HelpButton

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

        # Boton de ayuda
        help_text = (
            "Edit Playthrough Help\n\n"
            "Use this screen to customize which enemy patterns appear in each level.\n\n"
            "Layout:\n\n"
            "- Each row corresponds to a game level (Level 1, Level 2, Level 3).\n"
            "- For each level, you can select an enemy pattern from the dropdown menu.\n\n"
            "Instructions:\n"
            "1. Click on the dropdown next to a level to view the available enemy patterns.\n"
            "2. Select the desired pattern for that level.\n"
            "3. Repeat for all levels you want to customize.\n\n"
            "Buttons:\n"
            "- Save: Save your changes.\n"
            "- Return: Go back to the options menu without saving.\n\n"
            "Tips:\n"
            "- You can adjust enemy patterns to make levels easier or harder.\n"
            "- All levels must have a pattern selected (default is 'Pattern 1').\n\n"
            "This setup allows you to create custom difficulty flows or experiment with different challenge combinations.\n\n"
        )
        self.help_button = HelpButton(font=pygame.font.Font(None,50), title="Edit Playthrough",text=help_text,pos=(0,0),screen_size=[])



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
        result = self.get_patterns_from_dropdowns()
        self.game.patterns[self.game.states["OPTIONS"].active_player] = result

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # pasar eventos a dropdowns y botones
            self.dropdowns[0].handle_event(event)
            if(self.dropdowns[0].is_open):
                continue
            self.dropdowns[1].handle_event(event)
            if(self.dropdowns[1].is_open):
                continue
            self.dropdowns[2].handle_event(event)

            for b in self.buttons:
                b.handle_event(event)

            # Pasar eventos a boton de ayuda
            self.help_button.handle_event(event)

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

        # Boton de ayuda
        margin = 20  # margen desde los bordes
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width,height]
        self.help_button.update_pos([final_x,final_y])

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

        # Dibujar boton de ayuda
        self.help_button.draw(screen)

    def update_dropdowns_from_patterns(self, patterns_dict):
        """
        patterns_dict: dict {nivel: patrón_num}, por ejemplo {1:1, 2:3, 3:2}
        Actualiza el valor seleccionado de los dropdowns según este diccionario.
        """
        for i, lvl in enumerate(self.levels):
            # Obtener patrón para este nivel (default 1)
            pattern_num = patterns_dict.get(lvl, 1)
            # Convertir a índice para dropdown (0-based)
            idx = pattern_num - 1
            # Validar índice
            if 0 <= idx < len(self.patterns):
                self.dropdowns[i].selected_index = idx
            else:
                self.dropdowns[i].selected_index = 0

    def get_patterns_from_dropdowns(self):
        """
        Recorre los dropdowns y devuelve un diccionario {nivel: patrón_num}
        basado en los valores seleccionados actualmente.
        """
        result = {}
        for i, lvl in enumerate(self.levels):
            # El índice seleccionado + 1 es el patrón (porque los patrones van de 1 a 5)
            selected_pattern_num = self.dropdowns[i].selected_index + 1
            result[lvl] = selected_pattern_num
        return result
