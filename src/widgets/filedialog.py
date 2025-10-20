import os
import pygame
from widgets.button import Button
from widgets.textinput import TextInput

class FileDialog(Button):
    def __init__(self, text, pos, font, on_select=None, screen_size=[800,600]):
            super().__init__(text, pos, font, self.open_dialog)
            self.font = font
            self.on_select = on_select
            self.screen_size = screen_size  # Tamaño de la pantalla o ventana

            self.modal_visible = False
            self.current_path = os.getcwd()
            self.files = []
            self.file_buttons = []
            self.selected_file = None

            self.text_input = TextInput((0, 0), (0, 0), font)
            self.select_button = None
            self.cancel_button = None

            self.small_font = pygame.font.Font(None,30)
            self.modal_rect = pygame.Rect(0, 0, 900, 600)  # Tamaño fijo del modal
            self.setup_modal()

            # Paginacion
            self.current_page = 0
            self.items_per_page = 9

    def setup_modal(self):
        # Se reposiciona en open_dialog()
        self.update_file_list()

    def update_screen_size(self, new_screen_size):
        self.screen_size = new_screen_size

    def rebuild_modal_contents(self):
        x = (self.screen_size[0] - self.modal_rect.width) // 2
        y = (self.screen_size[1] - self.modal_rect.height) // 2
        self.modal_rect.topleft = (x, y)

        self.text_input.set_pos((x + 10, y + self.modal_rect.height - 60))
        self.text_input.set_size((self.modal_rect.width - 20, 40))

        self.select_button = Button("Seleccionar", (x + 10, y + self.modal_rect.height - 110), self.small_font, self.select_file)
        self.cancel_button = Button("Cancelar", (x + 200, y + self.modal_rect.height - 110), self.small_font, self.cancel)

        self.file_buttons = []
        y_offset = y + 10

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        visible_files = self.files[start:end]

        for item in visible_files:
            path = os.path.join(self.current_path, item)
            button = Button(
                item + ('/' if os.path.isdir(path) else ''),
                (x + 10, y_offset),
                self.small_font,
                self.on_item_click,
                args=item
            )
            y_offset += button.height + 10
            self.file_buttons.append(button)

        # Botones de navegación (paginación)
        if end < len(self.files):
            next_button = Button(">", (x + self.modal_rect.width - 70, y + self.modal_rect.height - 110), self.small_font, self.next_page)
            self.file_buttons.append(next_button)

        if self.current_page > 0:
            prev_button = Button("<", (x + self.modal_rect.width - 140, y + self.modal_rect.height - 110), self.small_font, self.prev_page)
            self.file_buttons.append(prev_button)
    
    def next_page(self):
        if (self.current_page + 1) * self.items_per_page < len(self.files):
            self.current_page += 1
            self.rebuild_modal_contents()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.rebuild_modal_contents()

    def open_dialog(self):
        self.modal_visible = True
        self.current_page = 0
        self.update_file_list()
        self.rebuild_modal_contents()

    def update_file_list(self):
        try:
            items = os.listdir(self.current_path)
            items.sort()
        except PermissionError:
            items = []
        self.files = [".."] + items 

    def on_item_click(self, item):
        if item == "..":
            parent = os.path.dirname(self.current_path)
            if os.path.isdir(parent) and parent != self.current_path:
                self.current_path = parent
                self.update_file_list()
                self.rebuild_modal_contents()
        else:
            full_path = os.path.join(self.current_path, item)
            if os.path.isdir(full_path):
                self.current_path = full_path
                self.current_page = 0 
                self.update_file_list()
                self.rebuild_modal_contents()
            else:
                self.selected_file = full_path
                self.text_input.update_text(item)

    def select_file(self):
        if self.selected_file:
            # Actualizar texto del botón con el nombre del archivo
            if self.on_select:
                self.on_select(self.selected_file)
            self.modal_visible = False

    def cancel(self):
        self.modal_visible = False

    def handle_event(self, event):
        if self.modal_visible:
            for b in self.file_buttons:
                b.handle_event(event)
            self.text_input.handle_event(event)
            if(self.select_button and self.cancel_button):
                self.select_button.handle_event(event)
                self.cancel_button.handle_event(event)
        else:
            super().handle_event(event)

    def draw(self, surface):
        super().draw(surface)
        if self.modal_visible:
            # Dibujar fondo modal
            pygame.draw.rect(surface, (30, 30, 30), self.modal_rect)
            pygame.draw.rect(surface, (200, 200, 200), self.modal_rect, 2)

            # Ruta actual
            path_surface = self.small_font.render(self.current_path, True, (255, 255, 0))
            surface.blit(path_surface, (self.modal_rect.x + 10, self.modal_rect.y - 30))

            for b in self.file_buttons:
                b.draw(surface)

            self.text_input.draw(surface)
            if(self.select_button and self.cancel_button):
                self.select_button.draw(surface)
                self.cancel_button.draw(surface)

    def update_pos(self, new_pos):
        super().update_pos(new_pos)
        # Modal se reposiciona la próxima vez que se abra
   
