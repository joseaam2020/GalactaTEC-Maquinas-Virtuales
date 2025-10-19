import pygame
from widgets.helpbutton import HelpButton
from widgets.button import Button

class RegisterWindow:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)
        self.small_font = pygame.font.Font(None, 36)

        # Cargar imagen de fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Variables para campos de texto
        self.username = ""
        self.full_name = ""
        self.email = ""
        self.profile_picture = None
        self.custom_ship = None
        self.favorite_music = ""
        
        # Variables para selección de archivos
        self.selected_profile_pic = "No seleccionada"
        self.selected_ship = "No seleccionada"
        
        # Campo activo
        self.active_field = "username"  # username, full_name, email, favorite_music
        
        # Rectángulos para campos de entrada
        self.username_rect = pygame.Rect(0, 0, 0, 0)
        self.full_name_rect = pygame.Rect(0, 0, 0, 0)
        self.email_rect = pygame.Rect(0, 0, 0, 0)
        self.favorite_music_rect = pygame.Rect(0, 0, 0, 0)
        self.profile_pic_rect = pygame.Rect(0, 0, 0, 0)
        self.ship_rect = pygame.Rect(0, 0, 0, 0)

        # Definimos los textos de los botones
        self.buttons_data = [
            "Register",  # Registrar jugador
            "Select Photo",  # Seleccionar fotografía
            "Select Ship",  # Seleccionar nave
            "Back"  # Volver atrás
        ]

        # Creamos los botones
        self.buttons = [
            Button(text=txt, font=self.small_font, pos=(0, 0)) for txt in self.buttons_data
        ]


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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Manejar entrada de texto
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Cambiar entre campos con TAB
                    fields = ["username", "full_name", "email", "favorite_music"]
                    current_index = fields.index(self.active_field)
                    next_index = (current_index + 1) % len(fields)
                    self.active_field = fields[next_index]
                    
                elif event.key == pygame.K_RETURN:
                    # Presionar ENTER intenta registrar
                    self.attempt_register()
                    
                elif event.key == pygame.K_BACKSPACE:
                    # Borrar caracteres
                    if self.active_field == "username":
                        self.username = self.username[:-1]
                    elif self.active_field == "full_name":
                        self.full_name = self.full_name[:-1]
                    elif self.active_field == "email":
                        self.email = self.email[:-1]
                    elif self.active_field == "favorite_music":
                        self.favorite_music = self.favorite_music[:-1]
                else:
                    # Agregar caracteres (evitar teclas especiales)
                    if event.unicode.isprintable():
                        if self.active_field == "username":
                            self.username += event.unicode
                        elif self.active_field == "full_name":
                            self.full_name += event.unicode
                        elif self.active_field == "email":
                            self.email += event.unicode
                        elif self.active_field == "favorite_music":
                            self.favorite_music += event.unicode
            
            # Manejar clics en campos de texto
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.username_rect.collidepoint(event.pos):
                    self.active_field = "username"
                elif self.full_name_rect.collidepoint(event.pos):
                    self.active_field = "full_name"
                elif self.email_rect.collidepoint(event.pos):
                    self.active_field = "email"
                elif self.favorite_music_rect.collidepoint(event.pos):
                    self.active_field = "favorite_music"
                elif self.profile_pic_rect.collidepoint(event.pos):
                    self.select_profile_picture()
                elif self.ship_rect.collidepoint(event.pos):
                    self.select_ship_image()

            # Pasar eventos a todos los botones
            for b in self.buttons:
                if b.handle_event(event):
                    if b.text == "Register":
                        self.attempt_register()
                    elif b.text == "Select Photo":
                        self.select_profile_picture()
                    elif b.text == "Select Ship":
                        self.select_ship_image()
                    elif b.text == "Back":
                        self.game.change_state("MAIN_MENU")

            # Pasar eventos a boton de ayuda
            self.help_button.handle_event(event)

    def select_profile_picture(self):
        #Simula la selección de una fotografía
        # En una aplicación real, aquí abrirías un diálogo de archivos
        self.selected_profile_pic = "avatar.png"  # Ejemplo
        print("Seleccionar fotografía del perfil")

    def select_ship_image(self):
        #Simula la selección de una imagen de nave
        # En una aplicación real, aquí abrirías un diálogo de archivos
        self.selected_ship = "ship_red.png"  # Ejemplo
        print("Seleccionar imagen de nave")

    def attempt_register(self):
        #Intenta registrar el nuevo jugador
        if self.username and self.full_name and self.email:
            # Aquí iría la lógica de registro en la base de datos
            print(f"Registrando jugador: {self.username}")
            print(f"Nombre completo: {self.full_name}")
            print(f"Email: {self.email}")
            print(f"Música preferida: {self.favorite_music}")
            print(f"Foto: {self.selected_profile_pic}")
            print(f"Nave: {self.selected_ship}")
            
            # Si el registro es exitoso:
            self.game.change_state("MAIN_MENU")
        else:
            print("Por favor, complete los campos obligatorios")

    def update_layout(self, screen):
        """Actualiza posiciones y tamaños según el tamaño de la pantalla."""
        width, height = screen.get_size()
        
        # Configurar fuentes proporcionales
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

        # Calcular posiciones
        title_y = height // 8  # Título más arriba para más espacio
        field_width = width // 2
        field_height = height // 20  # Campos más pequeños para más espacio
        field_spacing = height // 25  # Menos espacio entre campos
        
        # Posicionar campos de texto
        left_margin = width // 15  # margen desde el borde izquierdo
        center_x = left_margin
        
        # Campos de texto
        self.username_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 3,
            field_width, 
            field_height
        )
        
        self.full_name_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 6,
            field_width, 
            field_height
        )
        
        self.email_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 9,
            field_width, 
            field_height
        )
        
        self.favorite_music_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 12,
            field_width, 
            field_height
        )
        
        # Campos de selección de archivos (más anchos)
        file_field_width = field_width
        self.profile_pic_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 15,
            file_field_width, 
            field_height
        )
        
        self.ship_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 18,
            file_field_width, 
            field_height
        )
        
        # Posicionar botones
        button_width = field_width // 2
        button_start_y = self.ship_rect.bottom + field_spacing
        
       
        self.buttons[1].update_pos((self.profile_pic_rect.right + 20, self.profile_pic_rect.y - 5))  # Select Photo
        self.buttons[2].update_pos((self.ship_rect.right + 20, self.ship_rect.y - 5))  # Select Ship

       # Para posicionar los botones de Register y Back
        # Obtener tamaño de la pantalla
        width, height = screen.get_size()

        # Tamaño de los botones (ya definido por Button)
        register_button = self.buttons[0]
        back_button = self.buttons[3]

        # Margen desde el borde
        margin_x, margin_y = -10, 30

        # Posiciones: esquina inferior derecha
        register_x = width - register_button.width - margin_x
        register_y = height - register_button.height - margin_y

        # Ahora: poner el botón Back en la esquina inferior derecha
        self.buttons[3].update_pos((register_x, register_y))

        # Y el botón Register justo a la izquierda del Back
        spacing = 20
        register_left_x = register_x - register_button.width - spacing
        register_left_y = register_y
        self.buttons[0].update_pos((register_left_x, register_left_y))
 
        # Boton de ayuda
        margin = 20  # margen desde los bordes
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width,height]
        self.help_button.update_pos([final_x,final_y])

    def draw(self, screen):
        # Dibujar fondo escalado
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        # Actualizar layout
        self.update_layout(screen)
        
        width, height = screen.get_size()
        
        # Dibujar título
        title_text = self.font.render("New Player Registration", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 8))
        screen.blit(title_text, title_rect)
        
        # Dibujar etiquetas de campos
        labels = [
            ("Username:", self.username_rect),
            ("Full Name:", self.full_name_rect),
            ("Email:", self.email_rect),
            ("Favorite Music:", self.favorite_music_rect),
            ("Profile Picture:", self.profile_pic_rect),
            ("Custom Ship:", self.ship_rect)
        ]
        
        for label_text, rect in labels:
            label = self.small_font.render(label_text, True, (255, 255, 255))
            screen.blit(label, (rect.left, rect.top - 35))
        
        # Dibujar campos de texto
        fields = [
            (self.username_rect, self.username, "username"),
            (self.full_name_rect, self.full_name, "full_name"),
            (self.email_rect, self.email, "email"),
            (self.favorite_music_rect, self.favorite_music, "favorite_music")
        ]
        
        for rect, text, field_name in fields:
            color = (100, 100, 255) if self.active_field == field_name else (200, 200, 200)
            pygame.draw.rect(screen, color, rect, 2)
            text_surface = self.small_font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))
        
        # Dibujar campos de selección de archivos
        file_fields = [
            (self.profile_pic_rect, self.selected_profile_pic, "profile_pic"),
            (self.ship_rect, self.selected_ship, "ship")
        ]
        
        for rect, text, field_name in file_fields:
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
