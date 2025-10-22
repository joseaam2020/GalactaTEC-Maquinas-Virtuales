import pygame
from widgets.button import Button
from widgets.textinput import TextInput
from widgets.helpbutton import HelpButton
from register.bd import update_password, validate_password

class ChangePassword:
    def __init__(self, game):
        self.game = game
        #self.email = email  # Email verificado
        self.font = pygame.font.Font(None, 60)
        self.small_font = pygame.font.Font(None, 36)

        # Fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Campos de texto para la nueva contraseña
        self.password_input = TextInput(
            pos=(0, 0),
            size=(0, 0),
            font=self.small_font,
            placeholder="New password",
            password=True  # Si tu TextInput soporta modo password
        )
        
        self.confirm_password_input = TextInput(
            pos=(0, 0),
            size=(0, 0),
            font=self.small_font,
            placeholder="Confirm password",
            password=True
        )

        # Botones
        self.buttons = [
            Button(
                text="Change Password",
                font=self.small_font,
                pos=(0, 0),
                on_click=self.change_password
            ),
            Button(
                text="Cancel",
                font=self.small_font,
                pos=(0, 0),
                on_click=self.game.change_state,
                args="MAIN"
            )
        ]

        # Botón de ayuda
        help_text = (
            "Reset Your Password\n\n"
            "Enter your new password twice to confirm.\n"
            "Password must be at least 6 characters long.\n"
            "Click 'Change Password' to save.\n"
            "Click 'Cancel' to return to login."
        )
        self.help_button = HelpButton(
            font=self.font, 
            title="Change Password", 
            text=help_text, 
            pos=(0, 0), 
            screen_size=[]
        )

    # ---------------- EVENTOS ----------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            self.password_input.handle_event(event)
            self.confirm_password_input.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.password_input.active or self.confirm_password_input.active:
                    self.change_password()

            for b in self.buttons:
                b.handle_event(event)

            self.help_button.handle_event(event)

    # ---------------- CAMBIAR CONTRASEÑA ----------------

    def change_password(self):
        password = self.password_input.get_value()
        confirm = self.confirm_password_input.get_value()

        if not password or not confirm:
            self.show_error("Por favor completa todos los campos.")
            return

        if password != confirm:
            self.show_error("Las contraseñas no coinciden.")
            return

        # Validar requisitos de seguridad
        is_valid, reason = validate_password(password)
        if not is_valid:
            self.show_error(reason)
            return

        email = self.game.current_email

        success = update_password(email, password, "./src/register/GalactaDB.db")
        if success:
            self.show_error("Contraseña actualizada correctamente.", duration=2000)
            # Programar cambio de pantalla (sin bloquear)
            self.success_time = pygame.time.get_ticks()
            self.pending_change = True
        else:
            self.show_error("Error al actualizar la contraseña.")

    # ---------------- LAYOUT ----------------
    def update_layout(self, screen):
        width, height = screen.get_size()
        scale_factor = width / 800
        title_font_size = int(60 * scale_factor)
        field_font_size = int(36 * scale_factor)
        button_font_size = int(32 * scale_factor)

        self.font = pygame.font.Font(None, title_font_size)
        self.small_font = pygame.font.Font(None, field_font_size)

        for button in self.buttons:
            button.font = pygame.font.Font(None, button_font_size)
            button.update_text(button.text)

        title_y = height // 6
        field_width = width // 2
        field_height = height // 15
        center_x = width // 2 - field_width // 2

        # Campos de contraseña
        self.password_input.set_pos((center_x, title_y + height // 4))
        self.password_input.set_size((field_width, field_height))

        self.confirm_password_input.set_pos((center_x, title_y + height // 3 + 50))
        self.confirm_password_input.set_size((field_width, field_height))

        # Botón "Change Password" centrado
        self.buttons[0].update_pos((
            width // 2 - self.buttons[0].width // 2, 
            title_y + height // 2 + 50
        ))

        # Botón "Cancel" en esquina inferior derecha
        button_padding = 20
        self.buttons[1].update_pos((
            width - self.buttons[1].width - button_padding,
            height - self.buttons[1].height - button_padding
        ))

        # Botón de ayuda
        margin = 20
        self.help_button.screen_size = [width, height]
        self.help_button.update_pos([margin, height - self.help_button.height - margin])

    # ---------------- DIBUJADO ----------------
    def draw(self, screen):
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        self.update_layout(screen)
        width, height = screen.get_size()

        # Título
        title_text = self.font.render("Change Password", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 6))
        screen.blit(title_text, title_rect)

        # Etiquetas
        password_label = self.small_font.render("New Password:", True, (255, 255, 255))
        screen.blit(password_label, (
            self.password_input.rect.left, 
            self.password_input.rect.top - 40
        ))

        confirm_label = self.small_font.render("Confirm Password:", True, (255, 255, 255))
        screen.blit(confirm_label, (
            self.confirm_password_input.rect.left, 
            self.confirm_password_input.rect.top - 40
        ))

        # Campos de texto
        self.password_input.draw(screen)
        self.confirm_password_input.draw(screen)

        # Botones
        for button in self.buttons:
            button.draw(screen)

        # Mostrar errores
        if hasattr(self, "error_message"):
            elapsed = pygame.time.get_ticks() - self.error_time
            if elapsed < self.error_duration:
                error_font = pygame.font.Font(None, 40)
                color = (50, 255, 50) if "successfully" in self.error_message else (255, 50, 50)
                error_surf = error_font.render(self.error_message, True, color)
                error_rect = error_surf.get_rect(center=(width // 2, height // 4))
                screen.blit(error_surf, error_rect)
            else:
                del self.error_message

        self.help_button.draw(screen)

    def show_error(self, message, duration=2000):
        self.error_message = message
        self.error_time = pygame.time.get_ticks()
        self.error_duration = duration

    def update(self, dt):
        # Si hay un cambio pendiente tras mostrar el mensaje
        if getattr(self, "pending_change", False):
            if pygame.time.get_ticks() - self.success_time > 2000:
                self.pending_change = False
                self.game.change_state("MAIN")