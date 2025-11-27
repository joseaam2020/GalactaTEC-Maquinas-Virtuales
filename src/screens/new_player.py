import pygame
import os
import shutil
from widgets.filedialog import FileDialog
from widgets.helpbutton import HelpButton
from widgets.button import Button
from widgets.textinput import TextInput
from register.bd import email_exists, username_exists
from widgets.emailservice import send_verification_code
from register.bd import validate_password
from register.bd import register_player

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
        self.password_field = TextInput((0, 0), (300, 40), self.small_font, placeholder="Enter password",password=True)

        # Campos de selección de archivos
        self.selected_profile_pic = "No seleccionada"
        self.selected_music = "No seleccionada"
        self.selected_ship  = ""

        # Botones
        self.buttons_data = ["Register", "Return"]
        # Creamos los botones
        self.buttons = []
        for txt in self.buttons_data:
            on_click = None
            args = None
            match txt:
                case "Register":
                    on_click = self.register
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

        # Boton imagen
        self.buttons.append(
                FileDialog(
                    text="Select Photo",
                    font=self.small_font,
                    pos=(0,0),
                    on_select=self.select_profile_picture
                )
        )

        # Boton musica
        self.buttons.append(
                FileDialog(
                    text="Select Music",
                    font=self.small_font,
                    pos=(0,0),
                    on_select=self.select_music
                )
        )

        # Botones naves
        for i in range(1,4):
            self.buttons.append(
                Button(
                    text="",
                    font=self.small_font,
                    pos=(0, 0),
                    on_click=self.select_ship_image,
                    args=i,
                    image_path=f"./resources/imgs/player_ship_{i}.png",
                    size=(70,70)
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

            modal_visible_1: bool = self.buttons[2].modal_visible
            modal_visible_2: bool = self.buttons[3].modal_visible
            if(modal_visible_1):
                self.buttons[2].handle_event(event)
                continue
            if(modal_visible_2):
                self.buttons[3].handle_event(event)
                continue

            if getattr(self, "popup_active", False):
                self.handle_popup_events(event)
                continue  # bloquea interacción con la ventana principal

            # Pasar eventos a los campos de texto
            self.username_field.handle_event(event)
            self.fullname_field.handle_event(event)
            self.email_field.handle_event(event)
            self.password_field.handle_event(event)

            # Pasar eventos a los botones
            for b in self.buttons:
                b.handle_event(event)

            # Pasar eventos a boton de ayuda
            self.help_button.handle_event(event)
        
    # =================== FUNCIONES DE ARCHIVO ===================
    def select_profile_picture(self,img_path):
        # Simula la selección de una fotografía
        self.selected_profile_pic = img_path
        print("Seleccionar fotografía del perfil")

    def select_music(self,music_path): 
        self.selected_music = music_path
        print("Seleccionar musica")

    def select_ship_image(self, number):
        self.selected_ship = f"./resources/imgs/player_ship_{number}.png"
        print(f"Seleccionar imagen de nave {number}")

        # Limpiar el highlight de todos los botones de nave
        for i in range(4, 7):
            self.buttons[i].highlighted = False

        # Resaltar el botón seleccionado
        self.buttons[3 + number].highlighted = True

    # =================== LÓGICA DE REGISTRO ===================
    def attempt_register(self):
        username = self.username_field.get_value()
        full_name = self.fullname_field.get_value()
        email = self.email_field.get_value()
        
        if username and full_name and email:
            print(f"Registrando jugador: {username}")
            print(f"Nombre completo: {full_name}")
            print(f"Email: {email}")
            print(f"Música preferida: {self.selected_music}")
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
        self.username_field.set_pos((left_margin, title_y + field_spacing * 2))
        self.username_field.set_size((field_width, field_height))

        self.fullname_field.set_pos((left_margin, title_y + field_spacing * 5))
        self.fullname_field.set_size((field_width, field_height))

        self.email_field.set_pos((left_margin, title_y + field_spacing * 8))
        self.email_field.set_size((field_width, field_height))

        self.password_field.set_pos((left_margin, title_y + field_spacing * 11))
        self.password_field.set_size((field_width, field_height))

        # Campos de selección de archivos
        self.profile_pic_rect = pygame.Rect(
            left_margin, title_y + field_spacing * 14, field_width, field_height
        )

        # Campos de music
        self.music_rect = pygame.Rect(
            left_margin, title_y + field_spacing * 17, field_width, field_height
        )


        # Campos de music
        self.ship_rect = pygame.Rect(
            left_margin, title_y + field_spacing * 20, field_width, 60
        )

        # Posicionar botones
        button_width = field_width // 2
        button_start_y = self.music_rect.bottom + field_spacing

        # Botones de selección de archivo
        self.buttons[2].update_pos((self.profile_pic_rect.right + 20, self.profile_pic_rect.y - 5))  # Select Photo
        self.buttons[2].update_screen_size(screen.get_size())  # Select Photo
        self.buttons[3].update_pos((self.music_rect.right + 20, self.music_rect.y - 5))  # Select Music
        self.buttons[3].update_screen_size(screen.get_size())  # Select Photo

        # Botones inferiores (Register y Back)
        register_button = self.buttons[0]
        back_button = self.buttons[1]
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

        # Botones naves
        button_size = 70  # ancho y alto de cada botón
        spacing = 20      # espacio horizontal entre botones

        # Calcular ancho total ocupado por los 3 botones + espacios
        total_width = button_size * 3 + spacing * 2

        # Coordenada X inicial para centrar dentro del rectángulo
        start_x = self.ship_rect.x + (self.ship_rect.width - total_width) // 2
        y_center = self.ship_rect.centery - button_size // 2

        # Actualizar posiciones de los tres botones
        self.buttons[4].update_pos((start_x, y_center))
        self.buttons[5].update_pos((start_x + button_size + spacing, y_center))
        self.buttons[6].update_pos((start_x + (button_size + spacing) * 2, y_center))
        
        if getattr(self, "popup_active", False):
            width, height = screen.get_size()
            popup_width, popup_height = 400, 250

            # Centrar popup
            self.popup_rect = pygame.Rect(
                (width - popup_width) // 2,
                (height - popup_height) // 2,
                popup_width,
                popup_height
            )

            # Reposicionar campo de texto
            self.code_field.set_pos((
                self.popup_rect.centerx - self.code_field.rect.width // 2,
                self.popup_rect.centery - self.code_field.rect.height // 2
            ))

            # Reposicionar botones
            spacing = 10
            verify_button = self.popup_buttons[0]
            cancel_button = self.popup_buttons[1]

            verify_button.update_pos((
                self.popup_rect.centerx - verify_button.width - spacing,
                self.popup_rect.bottom - verify_button.height - 20
            ))

            cancel_button.update_pos((
                self.popup_rect.centerx + spacing,
                self.popup_rect.bottom - cancel_button.height - 20
            ))

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
            ("Favorite Music:", self.music_rect),
            ("Profile Picture:", self.profile_pic_rect),
            ("Password:", self.password_field.rect),
            ("Custom Ship:", self.ship_rect)
        ]

        for label_text, rect in labels:
            label = self.small_font.render(label_text, True, (255, 255, 255))
            screen.blit(label, (rect.left, rect.top - 35))

        # Dibujar campos de texto
        self.username_field.draw(screen)
        self.fullname_field.draw(screen)
        self.email_field.draw(screen)
        self.password_field.draw(screen)

        # Campos de selección de archivos

        # Dibujar seleccion de imagen
        rect = self.profile_pic_rect
        if ("/" in self.selected_profile_pic):
            text = self.selected_profile_pic.split('/')[-1]
        elif("\\" in self.selected_profile_pic):
            text = self.selected_profile_pic.split('\\')[-1]
        else:
            text = self.selected_profile_pic
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        text_surface = self.small_font.render(text, True, (150, 150, 150))
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))
        

        # Dibujar seleccion de nave
        rect = self.music_rect
        if ("/" in self.selected_music):
            text = self.selected_music.split('/')[-1]
        elif("\\" in self.selected_music):
            text = self.selected_music.split('\\')[-1]
        else:
            text = self.selected_music
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        text_surface = self.small_font.render(text, True, (150, 150, 150))
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # Dibujar botones
        for button in self.buttons:
            button.draw(screen)

        self.buttons[0].draw(screen)
        self.buttons[1].draw(screen)
        self.buttons[2].draw(screen)
        if(not self.buttons[2].modal_visible):
            self.buttons[3].draw(screen)

        # Dibujar boton de ayuda
        self.help_button.draw(screen)

        # ------------------ DIBUJAR MENSAJE DE ERROR ------------------
        if hasattr(self, "error_message"):
            elapsed = pygame.time.get_ticks() - self.error_time
            if elapsed < self.error_duration:
                error_font = pygame.font.Font(None, 40)
                error_surf = error_font.render(self.error_message, True, (255, 50, 50))
                error_rect = error_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 18))
                screen.blit(error_surf, error_rect)
            else:
                del self.error_message  # borrar mensaje tras tiempo

        # Si el popup está activo, dibujarlo encima
        if getattr(self, "popup_active", False):
            self.draw_popup(screen)

    def update(self, dt):
        pass

    def show_error(self, message, duration=2000):
        """
        Muestra un mensaje de error en el centro de la pantalla durante `duration` milisegundos.
        """
        self.error_message = message
        self.error_time = pygame.time.get_ticks()
        self.error_duration = duration

    def register(self):
        username = self.username_field.text
        fullname = self.fullname_field.text
        email    = self.email_field.text
        password = self.password_field.text
        music    = self.selected_music
        ship     = self.selected_ship
        photo    = self.selected_profile_pic

        # Validar que los paths existan
        if not os.path.isfile(music):
            self.show_error("Archivo de música no encontrado")
            return
        if not music.lower().endswith('.mp3'):
            self.show_error("El archivo de música no es .mp3")
            return
        
        if not os.path.isfile(ship):
            self.show_error("Archivo de nave no encontrado:")
            return
        if not ship.lower().endswith(('.jpg', '.png')):
            self.show_error("El archivo de nave no es .jpg o .png")
            return
        
        if not os.path.isfile(photo):
            self.show_error("Archivo de foto no encontrado")
            return
        if not photo.lower().endswith(('.jpg', '.png')):
            self.show_error("El archivo de foto no es .jpg o .png:")
            return

        valid_password, pwd_msg = validate_password(password=password) 

        # Validando informacion
        if(username and fullname and email and music and password and ship and photo):
            if username_exists(username=username, db_path="./src/register/GalactaDB.db"):
                self.show_error("El usuario ya existe, por favor ingrese otro.")
                return
            elif(not valid_password):
                self.show_error("Contraseña: " + pwd_msg);
                return
            elif email_exists(email=email,db_path="./src/register/GalactaDB.db"):
                self.show_error("El correo ya existe, por favor ingrese otro.")
                return
            else:
                code = send_verification_code(email)
                if code:
                    self.show_verification_popup(code)
                else:
                    self.show_error("Error enviando el correo de verificación")
                    return
        else:
            self.show_error("Error: Debe llenar todos los espacios")
            return



    # =================== POPUP DE VERIFICACIÓN ===================

    def show_verification_popup(self, sent_code: int):
        """
        Muestra un cuadro emergente (popup) para ingresar el código de verificación.
        """
        self.popup_active = True
        self.sent_code = sent_code
        self.popup_font = pygame.font.Font(None, 40)

        width, height = 800,600
        popup_width, popup_height = 400, 250
        self.popup_rect = pygame.Rect(
            (width - popup_width) // 2,
            (height - popup_height) // 2,
            popup_width,
            popup_height
        )

        # Campo de texto para el código
        self.code_field = TextInput(
            (self.popup_rect.centerx - 100, self.popup_rect.centery - 20),
            (200, 40),
            self.popup_font,
            placeholder="Enter code"
        )

        # Botones
        self.popup_buttons = [
            Button(
                text="Verify",
                font=self.popup_font,
                pos=(self.popup_rect.centerx - 90, self.popup_rect.bottom - 70),
                on_click=self.verify_code
            ),
            Button(
                text="Cancel",
                font=self.popup_font,
                pos=(self.popup_rect.centerx + 20, self.popup_rect.bottom - 70),
                on_click=self.close_popup
            )
        ]

    def close_popup(self):
        """
        Cierra el popup sin validar.
        """
        self.popup_active = False

    def verify_code(self):
        """
        Valida el código ingresado por el usuario.
        """
        entered = self.code_field.get_value().strip()

        if entered.isdigit() and int(entered) == self.sent_code:
            print("✅ Código correcto. Registro completado.")
            self.popup_active = False
            self.show_error("Correo verificado con éxito", duration=2000)
            # Aquí puedes continuar con la creación del jugador y guardarlo en la BD.
            username = self.username_field.text
            fullname = self.fullname_field.text
            email    = self.email_field.text
            password = self.password_field.text
            music    = self.selected_music
            ship     = self.selected_ship
            photo    = self.selected_profile_pic

            # Rutas de destino
            audio_dest_dir = "./resources/audio/"
            img_dest_dir = "./resources/imgs/"

            # Asegurarse de que las carpetas existen
            os.makedirs(audio_dest_dir, exist_ok=True)
            os.makedirs(img_dest_dir, exist_ok=True)

            # Obtener solo el nombre del archivo
            music_filename = os.path.basename(self.selected_music)
            photo_filename = os.path.basename(self.selected_profile_pic)

            # Rutas completas de destino
            music_dest = os.path.join(audio_dest_dir, music_filename)
            photo_dest = os.path.join(img_dest_dir, photo_filename)

            # Copiar archivos (sobrescribe si ya existe)
            try:
                src_music = os.path.abspath(self.selected_music)
                dst_music = os.path.abspath(music_dest)
                if src_music != dst_music:
                    shutil.copy2(src_music, dst_music)
                else:
                    # Ya es el mismo archivo: no copiar
                    print(f"Music file already in destination: {dst_music}")
            except Exception as e:
                print(f"Error copying music file: {e}")

            try:
                src_photo = os.path.abspath(self.selected_profile_pic)
                dst_photo = os.path.abspath(photo_dest)
                if src_photo != dst_photo:
                    shutil.copy2(src_photo, dst_photo)
                else:
                    print(f"Photo file already in destination: {dst_photo}")
            except Exception as e:
                print(f"Error copying photo file: {e}")

            # Actualizar variables con las nuevas rutas
            music = music_dest
            photo = photo_dest

            # Registrar el usuario en la base de datos
            register_player(
                    username=username,
                    full_name=fullname,
                    email=email,
                    password=password,
                    photo_path=photo,
                    music_pref=music,
                    ship_image=ship,
                    db_path="./src/register/GalactaDB.db",
            )
            
            # Crear diccionario para el jugador
            info =  {
                    "email"  : email,
                    "music" : music,
                    "ship" : ship,
                    "photo" : photo
                    }

            self.game.players[username] = info
            patterns = {1:1,2:1,3:1}
            self.game.patterns[username] = patterns
            print(self.game.players)
            self.game.change_state("MAIN")

        else:
            print("❌ Código incorrecto.")
            self.show_error("Código incorrecto, inténtalo de nuevo")

    def handle_popup_events(self, event):
        """
        Maneja los eventos del popup mientras está activo.
        """
        self.code_field.handle_event(event)
        for b in self.popup_buttons:
            b.handle_event(event)

    def draw_popup(self, screen):
        """
        Dibuja el cuadro de verificación del código.
        """
        # Fondo semi-transparente para efecto modal
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Cuadro del popup
        pygame.draw.rect(screen, (30, 30, 30), self.popup_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.popup_rect, 3, border_radius=10)

        # Texto del popup
        title = self.popup_font.render("Enter verification code", True, (255, 255, 255))
        screen.blit(title, (self.popup_rect.centerx - title.get_width() // 2, self.popup_rect.y + 30))

        # Campo de texto y botones
        self.code_field.draw(screen)
        for b in self.popup_buttons:
            b.draw(screen)
