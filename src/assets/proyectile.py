import pygame
from assets.colors import Colors
class Disparo:
    def __init__(self, x, y, tipo="normal"):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.vel = 7
        self.radio = 5
        self.impactado = False
        self.explosion_frames = 0
        self.explosion_radio = 0  # NUEVO — tamaño del área de daño

    def mover(self, _=None):
        # Solo se mueve si no ha explotado
        if not self.impactado:
            self.y -= self.vel
        # Si está explotando, no se mueve

    def dibujar(self, superficie):
        from assets.level import Level
        color = {"normal": Colors.BLANCO, "rastreador": Colors.MORADO, "area": Colors.ROJO}.get(self.tipo, Colors.BLANCO)
        pygame.draw.circle(superficie, color, (int(self.x), int(self.y)), self.radio)

        # Dibujar explosión AOE
        if self.tipo == "area" and self.impactado:
            pygame.draw.circle(superficie, (255, 150, 0), (int(self.x), int(self.y)), self.explosion_radio, 6)
            pygame.draw.circle(superficie, (255, 200, 50), (int(self.x), int(self.y)), self.explosion_radio + 20, 3)

    def iniciar_explosion(self, radio=100, duracion=15):
        """Activa la explosión visual y lógica del disparo AOE"""
        self.explosion_radio = radio
        self.explosion_frames = duracion
        self.impactado = True

    def fuera_de_pantalla(self):
        from assets.level import Level
        return self.y < -50 or self.y > Level.ALTO + 50 or self.x < -50 or self.x > Level.ANCHO + 50 or (self.tipo == "area" and self.explosion_frames <= 0)


