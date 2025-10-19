import pygame
from widgets.filedialog import FileDialog
from widgets.helpbutton import HelpButton
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
        self.buttons_data = ["Register", "Select Ship", "Return"]
        # Creamos los botones
        self.buttons = []
        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Register":
                    on_click = self.game.change_state
                    args = "OPTIONS"
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

        self.buttons.append(
                FileDialog(
                    text="Select Photo",
                    font=self.small_font,
                    pos=(0,0),
                    on_select=self.select_profile_picture
                )
        )


        # Boton de ayuda
        help_text = (
            "New Player Registration\n\n"
            "Use this form to create your player profile.\n\n"
            "Fields:\n"
            "- Username: Choose a unique name you'll use to sign in.\n"
            "- Full Name: Enter your real or display name.\n"
            "- Email: Provide a valid email for recovery purposes.\n"
            "You can also select:\n"
            "- Profile Picture: Click the field or the 'Select Photo' button to choose an avatar.\n"
            "- Custom Ship: Click the field or the 'Select Ship' button to choose your spaceship image.\n\n"
            "Buttons:\n"
            "- Register: Submit the form and create your player account.\n"
            "- Back: Return to the main menu without saving.\n\n"
            "Make sure all required fields are filled in.\n"
        )

        self.help_button = HelpButton(font=self.font, title="Registration",text=help_text,pos=(0,0),screen_size=[])

   # =================== EVENTOS ===================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            modal_visible: bool = self.buttons[3].modal_visible
            if(not modal_visible):
                # Pasar eventos a los campos de texto
                self.username_field.handle_event(event)
                self.fullname_field.handle_event(event)
                self.email_field.handle_event(event)
                self.music_field.handle_event(event)

                # Pasar eventos a los botones
                for b in self.buttons:
                    b.handle_event(event)
        
                # Pasar eventos a boton de ayuda
                self.help_button.handle_event(event)
            else:
                self.buttons[3].handle_event(event)
        
# =================== FUNCIONES DE ARCHIVO ===================
    def select_profile_picture(self,img_path):
        # Simula la selección de una fotografía
        self.selected_profile_pic = img_path
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
        field_font_size = int(28 * scale_factor)
        button_font_size = int(26 * scale_factor)

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
        self.buttons[3].update_pos((self.profile_pic_rect.right + 20, self.profile_pic_rect.y - 5))  # Select Photo
        self.buttons[3].update_screen_size(screen.get_size())  # Select Photo
        self.buttons[1].update_pos((self.ship_rect.right + 20, self.ship_rect.y - 5))  # Select Ship

        # Botones inferiores (Register y Back)
        register_button = self.buttons[0]
        back_button = self.buttons[2]
        margin_x, margin_y = -10, 30

        register_x = width - register_button.width - margin_x
        register_y = height - register_button.height - margin_y

        back_button.update_pos((register_x, register_y))
        spacing = 20
        register_left_x = register_x - register_button.width - spacing
        register_left_y = register_y
        register_button.update_pos((register_left_x, register_left_y))
 
        # Boton de ayuda
        margin = 20  # margen desde los bordes
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width,height]
        self.help_button.update_pos([final_x,final_y])

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

        # Dibujar seleccion de imagen
        rect = self.profile_pic_rect
        if ("/" in self.selected_profile_pic):
            text = self.selected_profile_pic.split('/')[-1]
        else:
            text = self.selected_profile_pic
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        text_surface = self.small_font.render(text, True, (150, 150, 150))
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))
        

        # Dibujar seleccion de nave
        rect = self.ship_rect
        text = self.selected_ship
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        text_surface = self.small_font.render(text, True, (150, 150, 150))
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # Dibujar botones
        for button in self.buttons:
            button.draw(screen)

        # Dibujar boton de ayuda
        self.help_button.draw(screen)

    def update(self, dt):
        pass
