import pygame
from widgets.button import Button
from widgets.textinput import TextInput


class RegisterWindow:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)
        self.small_font = pygame.font.Font(None, 36)

        # Fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Campos de entrada (TextInput)
        self.username_field = TextInput((0, 0), (300, 40), self.small_font, placeholder="Enter username")
        self.fullname_field = TextInput((0, 0), (300, 40), self.small_font, placeholder="Enter full name")
        self.email_field = TextInput((0, 0), (300, 40), self.small_font, placeholder="Enter email")
        self.music_field = TextInput((0, 0), (300, 40), self.small_font, placeholder="Favorite music")

        # Campos de selección de archivos
        self.selected_profile_pic = "No seleccionada"
        self.selected_ship = "No seleccionada"

        # Botones
        self.buttons_data = ["Register", "Select Photo", "Select Ship", "Return"]
        # Creamos los botones
        self.buttons = []
        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Register":
                    on_click = self.game.change_state
                    args = "OPTIONS"
                case "Select Photo":
                    on_click = self.game.change_state
                    args = ""
                case "Select Ship":
                    on_click = self.game.change_state
                    args = ""
                case "Return":
                    on_click = self.game.change_state
                    args = "MAIN"
            self.buttons.append(
                Button(
                    text=txt,
                    font=self.small_font,
                    pos=(0, 0),
                    on_click=on_click,
                    args=args
                )
            )


    # =================== EVENTOS ===================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Pasar eventos a los campos de texto
            self.username_field.handle_event(event)
            self.fullname_field.handle_event(event)
            self.email_field.handle_event(event)
            self.music_field.handle_event(event)

            # Pasar eventos a los botones
            for b in self.buttons:
                b.handle_event(event)


    # =================== FUNCIONES DE ARCHIVO ===================
    def select_profile_picture(self):
        # Simula la selección de una fotografía
        self.selected_profile_pic = "avatar.png"
        print("Seleccionar fotografía del perfil")

    def select_ship_image(self):
        # Simula la selección de una nave
        self.selected_ship = "ship_red.png"
        print("Seleccionar imagen de nave")

    # =================== LÓGICA DE REGISTRO ===================
    def attempt_register(self):
        username = self.username_field.get_value()
        full_name = self.fullname_field.get_value()
        email = self.email_field.get_value()
        favorite_music = self.music_field.get_value()

        if username and full_name and email:
            print(f"Registrando jugador: {username}")
            print(f"Nombre completo: {full_name}")
            print(f"Email: {email}")
            print(f"Música preferida: {favorite_music}")
            print(f"Foto: {self.selected_profile_pic}")
            print(f"Nave: {self.selected_ship}")
            self.game.change_state("MAIN_MENU")
        else:
            print("Por favor, complete los campos obligatorios")

    # =================== LAYOUT ===================
    def update_layout(self, screen):
        width, height = screen.get_size()
        scale_factor = width / 800
        title_font_size = int(60 * scale_factor)
        field_font_size = int(36 * scale_factor)
        button_font_size = int(32 * scale_factor)

        self.font = pygame.font.Font(None, title_font_size)
        self.small_font = pygame.font.Font(None, field_font_size)

        # Actualizar fuentes de botones
        for button in self.buttons:
            button.font = pygame.font.Font(None, button_font_size)
            button.update_text(button.text)

        # Posiciones
        title_y = height // 8
        field_width = width // 2
        field_height = height // 20
        field_spacing = height // 25
        left_margin = width // 15

        # Reubicar campos de texto
        self.username_field.set_pos((left_margin, title_y + field_spacing * 3))
        self.username_field.set_size((field_width, field_height))

        self.fullname_field.set_pos((left_margin, title_y + field_spacing * 6))
        self.fullname_field.set_size((field_width, field_height))

        self.email_field.set_pos((left_margin, title_y + field_spacing * 9))
        self.email_field.set_size((field_width, field_height))

        self.music_field.set_pos((left_margin, title_y + field_spacing * 12))
        self.music_field.set_size((field_width, field_height))

        # Campos de selección de archivos
        self.profile_pic_rect = pygame.Rect(
            left_margin, title_y + field_spacing * 15, field_width, field_height
        )
        self.ship_rect = pygame.Rect(
            left_margin, title_y + field_spacing * 18, field_width, field_height
        )

        # Posicionar botones
        button_width = field_width // 2
        button_start_y = self.ship_rect.bottom + field_spacing

        # Botones de selección de archivo
        self.buttons[1].update_pos((self.profile_pic_rect.right + 20, self.profile_pic_rect.y - 5))  # Select Photo
        self.buttons[2].update_pos((self.ship_rect.right + 20, self.ship_rect.y - 5))  # Select Ship

        # Botones inferiores (Register y Back)
        register_button = self.buttons[0]
        back_button = self.buttons[3]
        margin_x, margin_y = -10, 30

        register_x = width - register_button.width - margin_x
        register_y = height - register_button.height - margin_y

        back_button.update_pos((register_x, register_y))
        spacing = 20
        register_left_x = register_x - register_button.width - spacing
        register_left_y = register_y
        register_button.update_pos((register_left_x, register_left_y))

        

    # =================== DIBUJO ===================
    def draw(self, screen):
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        self.update_layout(screen)

        width, height = screen.get_size()

        # Título
        title_text = self.font.render("New Player Registration", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 8))
        screen.blit(title_text, title_rect)

        # Etiquetas
        labels = [
            ("Username:", self.username_field.rect),
            ("Full Name:", self.fullname_field.rect),
            ("Email:", self.email_field.rect),
            ("Favorite Music:", self.music_field.rect),
            ("Profile Picture:", self.profile_pic_rect),
            ("Custom Ship:", self.ship_rect)
        ]

        for label_text, rect in labels:
            label = self.small_font.render(label_text, True, (255, 255, 255))
            screen.blit(label, (rect.left, rect.top - 35))

        # Dibujar campos de texto
        self.username_field.draw(screen)
        self.fullname_field.draw(screen)
        self.email_field.draw(screen)
        self.music_field.draw(screen)

        # Campos de selección de archivos
        file_fields = [
            (self.profile_pic_rect, self.selected_profile_pic),
            (self.ship_rect, self.selected_ship)
        ]
        for rect, text in file_fields:
            pygame.draw.rect(screen, (200, 200, 200), rect, 2)
            text_surface = self.small_font.render(text, True, (150, 150, 150))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # Dibujar botones
        for button in self.buttons:
            button.draw(screen)

    def update(self, dt):
        pass
