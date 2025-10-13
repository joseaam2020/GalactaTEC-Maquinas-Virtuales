import pygame
from widgets.button import Button
#from options import Options

class main_window:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 60)
        self.small_font = pygame.font.Font(None, 36)

        # Cargar imagen de fondo
        self.background = pygame.image.load("./resources/imgs/options_background.jpg").convert()

        # Variables para campos de texto
        self.username = ""
        self.password = ""
        self.active_field = "username"  # "username" o "password"
        
        # Rectángulos para campos de entrada
        self.username_rect = pygame.Rect(0, 0, 0, 0)
        self.password_rect = pygame.Rect(0, 0, 0, 0)

        # Definimos los textos de los botones
        self.buttons_data = [
            "Sign in",  # Iniciar sesión
            "New player",  # Registrar nuevo jugador
            "Recover password",  # Recuperar contraseña

        ]

        # Creamos los botones
        self.buttons = [
            Button(text=txt, font=self.small_font, pos=(0, 0)) for txt in self.buttons_data
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Manejar entrada de texto
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Cambiar entre campos con TAB
                    self.active_field = "password" if self.active_field == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    # Presionar ENTER en el campo de contraseña intenta iniciar sesión
                    if self.active_field == "password":
                        self.attempt_login()
                elif event.key == pygame.K_BACKSPACE:
                    # Borrar caracteres
                    if self.active_field == "username":
                        self.username = self.username[:-1]
                    else:
                        self.password = self.password[:-1]
                else:
                    # Agregar caracteres (evitar teclas especiales)
                    if event.unicode.isprintable():
                        if self.active_field == "username":
                            self.username += event.unicode
                        else:
                            self.password += event.unicode
            
            # Manejar clics en campos de texto
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.username_rect.collidepoint(event.pos):
                    self.active_field = "username"
                elif self.password_rect.collidepoint(event.pos):
                    self.active_field = "password"

            # Pasar eventos a todos los botones
            for b in self.buttons:
                if b.handle_event(event):
                    print(f"Botón presionado: {b.text}")  # 👈 debug
                    if b.text == "Sign in":
                        print("Cambiando a ventana a Options")
                        self.game.change_state("OPTIONS")
                    elif b.text == "New player":
                        print("Cambiando a ventana a Registros")
                        self.game.change_state("new_player")
                    elif b.text == "Recover password":
                        print("Cambiando a ventana a cambiar contraseña")
                        self.game.change_state("RECOVER_PASSWORD")


    def attempt_login(self):
        # Intenta iniciar sesión con las credenciales proporcionadas
        if self.username and self.password:
            # Lógica de autenticación
            print(f"Intentando login: {self.username}")
            # Si las credenciales son correctas:
            self.game.change_state("LEVEL1")
        else:
            print("Por favor, complete ambos campos")

    def update_layout(self, screen):
        #Actualiza posiciones y tamaños según el tamaño de la pantalla
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
        title_y = height // 6
        field_width = width // 2
        field_height = height // 15
        field_spacing = height // 10
        
        # Posicionar campos de texto
        center_x = width // 2 - field_width // 2
        
        self.username_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 2,  # Bajado
            field_width, 
            field_height
        )
        
        self.password_rect = pygame.Rect(
            center_x, 
            title_y + field_spacing * 3.5,  # Bajado
            field_width, 
            field_height
        )
        
        # Posicionar botones
        button_width = field_width // 2
        button_height = field_height
        button_start_y = self.password_rect.bottom + field_spacing

        # Posición de lo botones
        self.buttons[0].update_pos((838, 430))  # Sign in
        self.buttons[1].update_pos((320, 560))  # New player
        self.buttons[2].update_pos((320, 492))  # Recover password

        # Asignar función al botón Sign in
        self.buttons[0].on_click = lambda: self.game.change_state("OPTIONS")

         # Funcionalidad del botón Add Players, que es registrar a un nuevo jugador
        self.buttons[1].on_click = lambda: self.game.change_state("REGISTER")

        #"Recover password": pos=(320, 560), size=(253, 45)
        #Botón "Back": pos=(660, 560), size=(97, 44)
        #Botón "Sign in": pos=(838, 430), size=(123, 46)
        #Botón "New player": pos=(660, 492), size=(168, 45)


    def draw(self, screen):
        # Dibujar fondo escalado
        background_scaled = pygame.transform.scale(self.background, screen.get_size())
        screen.blit(background_scaled, (0, 0))

        # Actualizar layout
        self.update_layout(screen)
        
        width, height = screen.get_size()
        
        # Dibujar título
        title_text = self.font.render("Sign In", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 6))
        screen.blit(title_text, title_rect)
        
        # Dibujar etiquetas de campos 
        username_label = self.small_font.render("Username:", True, (255, 255, 255))
        password_label = self.small_font.render("Password:", True, (255, 255, 255))
        
        screen.blit(username_label, (self.username_rect.left, self.username_rect.top - 50))
        screen.blit(password_label, (self.password_rect.left, self.password_rect.top - 50))
        
        # Dibujar campos de texto
        username_color = (100, 100, 255) if self.active_field == "username" else (200, 200, 200)
        password_color = (100, 100, 255) if self.active_field == "password" else (200, 200, 200)
        
        pygame.draw.rect(screen, username_color, self.username_rect, 2)
        pygame.draw.rect(screen, password_color, self.password_rect, 2)
        
        # Dibujar texto en campos (mostrar asteriscos para contraseña)
        username_surface = self.small_font.render(self.username, True, (255, 255, 255))
        password_surface = self.small_font.render("*" * len(self.password), True, (255, 255, 255))
        
        screen.blit(username_surface, (self.username_rect.x + 5, self.username_rect.y + 5))
        screen.blit(password_surface, (self.password_rect.x + 5, self.password_rect.y + 5))
        
        # Dibujar botones
        for button in self.buttons:
            button.draw(screen)

    def update(self, dt):
        pass