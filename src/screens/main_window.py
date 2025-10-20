import pygame
from widgets.button import Button
from widgets.textinput import TextInput 
from register.bd import login_player
from widgets.helpbutton import HelpButton
#from options import Options

class main_window:

    signed_in = False
    needs_reset = False

    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)
        self.small_font = pygame.font.Font(None, 36)


        # Fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Campos de texto usando tu clase
        self.username_input = TextInput(
            pos=(0, 0),
            size=(0, 0),
            font=self.small_font,
            placeholder="Enter username"
        )
        self.password_input = TextInput(
            pos=(0, 0),
            size=(0, 0),
            font=self.small_font,
            placeholder="Enter password",
            password=True
        )


        # Definimos los botones
        self.buttons_data = [
            "Sign in",
            "New player",
            "Recover password",
            "Return",
        
        ]
        
        self.buttons = []
        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Sign in":
                    on_click = self.attempt_login
                    args = None
                case "New player":
                    on_click = self.game.change_state
                    args = "REGISTER"
                case "Recover password":
                    on_click = self.game.change_state
                    args = "RECOVER_PASSWORD"
                case "Return":
                    on_click = self.game.change_state
                    args = "OPTIONS"
            self.buttons.append(
                Button(
                    text=txt,
                    font=self.small_font,
                    pos=(0, 0),
                    on_click=on_click,
                    args=args
                )
            )

            

    
        # Boton de ayuda
        help_text = (
            "Welcome to the game!\n\n"
            "This is the sign-in screen where you can:\n\n"
            "- Enter your username and password to log in.\n\n"
            "- Click 'Sign in' to log in if your credentials are correct.\n\n"
            "- Click 'New player' to register a new account.\n\n"
            "- Click 'Recover password' if you've forgotten your password.\n\n"
            "Use the keyboard to type in your information.\n"
        )
        self.help_button = HelpButton(font=self.font, title="Sign in",text=help_text,pos=(0,0),screen_size=[])

   # ---------------- EVENTOS ----------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Pasar eventos a los inputs
            self.username_input.handle_event(event)
            self.password_input.handle_event(event)

            # Si se presiona Enter estando en el password → intentar login
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.password_input.active:
                    self.attempt_login()
            # Pasar eventos a boton de ayuda
            self.help_button.handle_event(event)

            # Pasar eventos a botones
            for b in self.buttons:
                if b.text == "Return" and main_window.signed_in:
                    b.handle_event(event)
                elif b.text != "Return":
                    b.handle_event(event)
                
                    

    # ---------------- LOGIN ----------------
    def attempt_login(self):
        # Obtengo los valores de los cuadros de texto
        username = self.username_input.get_value()
        password = self.password_input.get_value()

        print(username)
        print(password)

        if not username or not password:
            self.show_error("Por favor, complete ambos campos")
            return

        # Validar con la base de datos

        user = login_player(username, password, "./src/register/GalactaDB.db")
        if user:  # login correcto
            self.game.change_state("OPTIONS")
        else:  # login fallido
            self.show_error("Usuario o contraseña incorrectos")

    # ---------------- LAYOUT ----------------
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

        # Posiciones base
        title_y = height // 6
        field_width = width // 2
        field_height = height // 15
        field_spacing = height // 10
        center_x = width // 2 - field_width // 2

        # Configurar inputs
        self.username_input.set_pos((center_x, title_y + field_spacing * 2))
        self.username_input.set_size((field_width, field_height))

        self.password_input.set_pos((center_x, title_y + field_spacing * 3.5))
        self.password_input.set_size((field_width, field_height))

        # Actualizar botones
        button_width = field_width // 2
        button_height = field_height
        self.buttons[0].update_pos((838, 430))  # Sign in
        self.buttons[1].update_pos((320, 560))  # New player
        self.buttons[2].update_pos((320, 492))  # Recover password
        

        # Posicionar botón de salida en esquina inferior derecha
        button_padding = 20
        self.buttons[3].font = pygame.font.Font(None, int(50 * scale_factor))
        self.buttons[3].update_text("Return")
        self.buttons[3].update_pos((
            width - self.buttons[3].width - button_padding,
            height - self.buttons[3].height - button_padding
        ))
        
       
        # Boton de ayuda
        margin = 20  # margen desde los bordes
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width,height]
        self.help_button.update_pos([final_x,final_y])

    # ---------------- DIBUJADO ----------------
    def draw(self, screen):
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        self.update_layout(screen)
        width, height = screen.get_size()

        # Título
        title_text = self.font.render("Sign In", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 6))
        screen.blit(title_text, title_rect)

        # Etiquetas
        username_label = self.small_font.render("Username:", True, (255, 255, 255))
        password_label = self.small_font.render("Password:", True, (255, 255, 255))
        screen.blit(username_label, (self.username_input.rect.left, self.username_input.rect.top - 40))
        screen.blit(password_label, (self.password_input.rect.left, self.password_input.rect.top - 40))

        # Campos de texto
        self.username_input.draw(screen)
        self.password_input.draw(screen)

        # Enmascarar el campo de contraseña visualmente
        if self.password_input.text:
            masked = "*" * len(self.password_input.text)
            text_surface = self.password_input.font.render(masked, True, (255, 255, 255))
            screen.blit(text_surface, (self.password_input.rect.x + 5, self.password_input.rect.y + 5))

        

        # Botones
        for button in self.buttons:
            if button.text == "Return" and main_window.signed_in:
                button.draw(screen)
            elif button.text != "Return":
                button.draw(screen)


        # ------------------ DIBUJAR MENSAJE DE ERROR ------------------
        if hasattr(self, "error_message"):
            elapsed = pygame.time.get_ticks() - self.error_time
            if elapsed < self.error_duration:
                error_font = pygame.font.Font(None, 40)
                error_surf = error_font.render(self.error_message, True, (255, 50, 50))
                error_rect = error_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
                screen.blit(error_surf, error_rect)
            else:
                del self.error_message  # borrar mensaje tras tiempo

        # Dibujar boton de ayuda
        self.help_button.draw(screen) 

    def show_error(self, message, duration=2000):
        """
        Muestra un mensaje de error en el centro de la pantalla durante `duration` milisegundos.
        """
        self.error_message = message
        self.error_time = pygame.time.get_ticks()
        self.error_duration = duration
        
    def update(self, dt):
        pass
