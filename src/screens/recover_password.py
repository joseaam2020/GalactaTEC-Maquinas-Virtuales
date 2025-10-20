import pygame
from widgets.button import Button
from widgets.textinput import TextInput
from widgets.helpbutton import HelpButton
from register.bd import check_email

class RecoverPassword:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)
        self.small_font = pygame.font.Font(None, 36)

        # Fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Campo de texto (correo)
        self.email_input = TextInput(
            pos=(0, 0),
            size=(0, 0),
            font=self.small_font,
            placeholder="Enter your email"
        )

        # Botones
        self.buttons_data = ["Send", "Return"]
        self.buttons = []

        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Send":
                    on_click = self.send_request
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

        # Botón de ayuda
        help_text = (
            "Forgot your password?\n\n"
            "Enter your registered email and click 'Send'.\n"
            "You’ll receive instructions to reset your password.\n"
            "Click 'Return' to go back to the login screen."
        )
        self.help_button = HelpButton(font=self.font, title="Recover Password", text=help_text, pos=(0, 0), screen_size=[])

    # ---------------- EVENTOS ----------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Pasar eventos al input
            self.email_input.handle_event(event)

            # Presionar Enter envía la solicitud
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.email_input.active:
                    self.send_request()

            # Pasar eventos a los botones
            for b in self.buttons:
                b.handle_event(event)

            # Botón de ayuda
            self.help_button.handle_event(event)

    # ---------------- ENVÍO ----------------
    def send_request(self):
        email = self.email_input.get_value()
        if not email:
            self.show_error("Please enter your email")
            return

        print(f"Recover password for: {email}")
        checked = check_email(email, "./src/register/GalactaDB.db")
        if checked: 
            # Lógica para enviar el correo
            print("Correo enviado")

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
        center_x = width // 2 - field_width // 2

        # Campo de email
        self.email_input.set_pos((center_x, title_y + height // 3))
        self.email_input.set_size((field_width, field_height))

        # Botón "Send"
        self.buttons[0].update_pos((width // 2 - self.buttons[0].width // 2, title_y + height // 2))

        # Botón "Return" en esquina inferior derecha
        button_padding = 20
        self.buttons[1].font = pygame.font.Font(None, int(50 * scale_factor))
        self.buttons[1].update_text("Return")
        self.buttons[1].update_pos((
            width - self.buttons[1].width - button_padding,
            height - self.buttons[1].height - button_padding
        ))

        # Botón de ayuda
        margin = 20
        final_x = margin
        final_y = height - self.help_button.height - margin
        self.help_button.screen_size = [width, height]
        self.help_button.update_pos([final_x, final_y])

    # ---------------- DIBUJADO ----------------
    def draw(self, screen):
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        self.update_layout(screen)
        width, height = screen.get_size()

        # Título
        title_text = self.font.render("Recover Password", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 6))
        screen.blit(title_text, title_rect)

        # Etiqueta de correo
        email_label = self.small_font.render("Email:", True, (255, 255, 255))
        screen.blit(email_label, (self.email_input.rect.left, self.email_input.rect.top - 40))

        # Campo de texto
        self.email_input.draw(screen)

        # Botones
        for button in self.buttons:
            button.draw(screen)

        # Mostrar errores o mensajes
        if hasattr(self, "error_message"):
            elapsed = pygame.time.get_ticks() - self.error_time
            if elapsed < self.error_duration:
                error_font = pygame.font.Font(None, 40)
                error_surf = error_font.render(self.error_message, True, (255, 50, 50))
                error_rect = error_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
                screen.blit(error_surf, error_rect)
            else:
                del self.error_message

        # Botón de ayuda
        self.help_button.draw(screen)

    def show_error(self, message, duration=2000):
        self.error_message = message
        self.error_time = pygame.time.get_ticks()
        self.error_duration = duration

    def update(self, dt):
        pass
