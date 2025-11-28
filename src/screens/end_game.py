import os
import random
import pygame
from widgets.button import Button
from assets.sound_manager import SoundManager

class EndGameScreen:
    def __init__(self, manager):
        self.manager = manager
        self.screen = manager.screen
        self.fanfare_played = False
        self.fanfare_timer = None  # tiempo (ms) en que se debe reproducir la fanfarria

        # Fuentes
        self.font_title = pygame.font.Font(None, 90)
        self.font_text  = pygame.font.Font(None, 50)
        self.font_button = pygame.font.Font(None, 40)

        # Resultados
        self.players = []  # [{"name":..., "photo":..., "score":...}, ...]
        self.winner_indices = []
        self.confetti_particles = []
        self.confetti_active = False

        # Botones: Volver al menú y Reiniciar
        self.btn_menu = Button(
            text="Volver al menú",
            pos=(360, 600),
            font=self.font_button,
            on_click=self.go_menu,
            size=(220, 70)
        )
        self.btn_restart = Button(
            text="Reiniciar",
            pos=(700, 600),
            font=self.font_button,
            on_click=self.restart,
            size=(220, 70)
        )

    # ===================================================================
    #       MÉTODO PARA RECIBIR RESULTADOS DESDE LEVEL
    # ===================================================================
    def set_results(self, players_list):
        """Recibe lista de jugadores, determina ganador(es), inicia confetti y programa la fanfarria."""
        self.players = players_list or []

        # determinar ganador/es por puntuación
        if not self.players:
            self.winner_indices = []
        else:
            try:
                scores = [p.get("score", 0) for p in self.players]
                max_score = max(scores)
                self.winner_indices = [i for i, s in enumerate(scores) if s == max_score]
            except Exception:
                self.winner_indices = []

        # iniciar confetti
        self._start_confetti_for_winners()

        # Programar la fanfarria con un pequeño retraso (ms)
        try:
            delay_ms = 500  # ajustar si se desea más/menos retraso
            self.fanfare_timer = pygame.time.get_ticks() + delay_ms
            self.fanfare_played = False
            # hacer un pequeño fadeout de la música de fondo para que la fanfarria destaque
            try:
                pygame.mixer.music.fadeout(600)
            except Exception:
                pass
        except Exception:
            self.fanfare_timer = None
            self.fanfare_played = False

    def _start_confetti_for_winners(self):
        """Genera partículas de confetti centradas sobre cada ganador y activa la animación."""
        self.confetti_particles.clear()
        self.confetti_active = False

        if not self.winner_indices:
            return

        # posiciones aproximadas donde se dibujan los retratos en draw()
        base_y = 200
        img_w, img_h = 140, 140

        for idx in self.winner_indices:
            y = base_y + idx * 200
            center_x = 200 + img_w // 2
            center_y = y + img_h // 2

            for _ in range(40):
                vx = random.uniform(-0.2, 0.2) * 300   # px/s scaled later
                vy = random.uniform(-0.8, -0.3) * 300
                life = random.uniform(800, 1600)  # ms
                size = random.randint(4, 9)
                color = random.choice([
                    (255, 50, 50), (255, 200, 0), (100, 200, 80),
                    (70, 180, 255), (200, 120, 255)
                ])
                self.confetti_particles.append({
                    "x": center_x + random.uniform(-30, 30),
                    "y": center_y + random.uniform(-20, 20),
                    "vx": vx / 1000.0,   # px per ms
                    "vy": vy / 1000.0,
                    "life": life,
                    "size": size,
                    "color": color
                })

        if self.confetti_particles:
            self.confetti_active = True

    # ===================================================================
    #       ACCIONES DE BOTONES
    # ===================================================================
    def go_menu(self):
        try:
            # Detener la música al volver al menú
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        except Exception:
            pass
        self.manager.change_state("OPTIONS")

    def restart(self):
        try:
            # Parar cualquier música/fanfarria antes de reiniciar la playthrough
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            # Reutiliza el manager para iniciar playthrough si existe (usa la lógica de logged_users)
            self.manager.start_playthrough()
        except Exception:
            # Fallback: cambiar a MAIN
            try:
                self.manager.change_state("MAIN")
            except Exception:
                pass

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
        """Actualizar animación de confetti y reproducir fanfarria tras retraso.
           dt puede ser segundos (0.016) o ms; normalizamos a ms.
        """
        # Normalizar dt a ms si es necesario
        try:
            dt_ms = float(dt)
            if dt_ms <= 0.1:
                dt_ms = dt_ms * 1000.0
        except Exception:
            dt_ms = 16.0

        # Actualizar confetti
        if self.confetti_active:
            g = 0.0009  # px per ms^2
            new_particles = []
            for p in self.confetti_particles:
                p["x"] += p["vx"] * dt_ms
                p["y"] += p["vy"] * dt_ms
                p["vy"] += g * dt_ms
                p["life"] -= dt_ms
                if p["life"] > 0:
                    new_particles.append(p)
            self.confetti_particles = new_particles
            if not self.confetti_particles:
                self.confetti_active = False

        # Reproducir fanfarria si llegó el momento y no se ha reproducido
        try:
            if not self.fanfare_played and self.fanfare_timer is not None:
                if pygame.time.get_ticks() >= self.fanfare_timer:
                    SoundManager.play("fanfarria")
                    self.fanfare_played = True
        except Exception:
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
        img_size = (140, 140)

        for idx, p in enumerate(self.players):
            y = base_y + idx * 200

            # Imagen jugador
            try:
                img = pygame.image.load(p.get("photo", "")).convert_alpha()
                img = pygame.transform.scale(img, img_size)
            except Exception:
                img = pygame.Surface(img_size)
                img.fill((80, 80, 80))

            img_rect = pygame.Rect(200, y, img_size[0], img_size[1])

            # Si es ganador, dibujar marco dorado y brillo
            if idx in self.winner_indices:
                gold = (212, 175, 55)
                try:
                    pygame.draw.rect(surface, gold, img_rect.inflate(22, 22), border_radius=8)
                    pygame.draw.rect(surface, (255, 230, 120), img_rect.inflate(12, 12), border_radius=6)
                except Exception:
                    pygame.draw.rect(surface, gold, img_rect.inflate(12, 12), 4)

            surface.blit(img, img_rect.topleft)

            # Texto con puntuación
            text = self.font_text.render(f"{p.get('name','Jugador')} — {p.get('score',0)} pts", True, (255, 255, 255))
            surface.blit(text, (380, y + 50))

        # Dibujar confetti encima de todo
        if self.confetti_active:
            for p in self.confetti_particles:
                rect = pygame.Rect(int(p["x"]), int(p["y"]), p["size"], p["size"])
                try:
                    surface.fill(p["color"], rect)
                except Exception:
                    pygame.draw.rect(surface, p["color"], rect)

        # Botones
        self.btn_menu.draw(surface)
        self.btn_restart.draw(surface)
