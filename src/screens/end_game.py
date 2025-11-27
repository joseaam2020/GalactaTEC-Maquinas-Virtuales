import pygame
from widgets.button import Button

class EndGameScreen:
    def __init__(self, manager):
        self.manager = manager
        self.screen = manager.screen

        # Fuentes
        self.font_title = pygame.font.Font(None, 90)
        self.font_text  = pygame.font.Font(None, 50)
        self.font_button = pygame.font.Font(None, 40)  # Fuente para botones

        # Aquí se guardará la lista de jugadores
        self.players = []  # [{"name":..., "photo":..., "score":...}, ...]

        # Botones (firma correcta)
        self.btn_menu = Button(
            text="Volver al menú",
            pos=(400, 600),
            font=self.font_button,
            on_click=self.go_menu,
            size=(220, 70)
        )

        self.btn_restart = Button(
            text="Reiniciar",
            pos=(660, 600),
            font=self.font_button,
            on_click=self.restart,
            size=(220, 70)
        )

    # ===================================================================
    #       MÉTODO PARA RECIBIR RESULTADOS DESDE LEVEL1
    # ===================================================================
    def set_results(self, players_list):
        self.players = players_list

    # ===================================================================
    #       ACCIONES DE BOTONES
    # ===================================================================
    def go_menu(self):
        self.manager.change_state("OPTIONS")

    def restart(self):
        self.manager.start_playthrough()

    # ===================================================================
    #       EVENTOS
    # ===================================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            self.btn_menu.handle_event(event)
            self.btn_restart.handle_event(event)

    def update(self, dt):
        pass

    # ===================================================================
    #       DIBUJAR PANTALLA
    # ===================================================================
    def draw(self, surface):
        surface.fill((15, 15, 30))

        # Título
        title = self.font_title.render("Fin de la Partida", True, (255, 255, 255))
        surface.blit(title, (surface.get_width() / 2 - title.get_width() / 2, 50))

        # Mostrar jugadores (1 o 2)
        base_y = 200

        for idx, p in enumerate(self.players):
            y = base_y + idx * 200

            # Imagen jugador
            try:
                img = pygame.image.load(p["photo"]).convert_alpha()
                img = pygame.transform.scale(img, (140, 140))
            except:
                img = pygame.Surface((140, 140))
                img.fill((80, 80, 80))

            surface.blit(img, (200, y))

            # Texto
            text = self.font_text.render(
                f"{p['name']} — {p['score']} pts", True, (255, 255, 255)
            )
            surface.blit(text, (380, y + 50))

        # Botones
        self.btn_menu.draw(surface)
        self.btn_restart.draw(surface)
