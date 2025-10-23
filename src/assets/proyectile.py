import pygame
import math
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
        self.objetivo = None

    def mover(self, enemigos=None):
        # === Movimiento normal ===
        if self.tipo != "rastreador":
            if not self.impactado:
                self.y -= self.vel
            return

        # === Movimiento rastreador ===
        if not self.impactado:
            # Si no tiene objetivo o el enemigo ya murió, buscar uno nuevo
            if not self.objetivo or not self.objetivo.vivo:
                self.seleccionar_objetivo(enemigos)

            # Si hay un objetivo válido, moverse hacia él
            if self.objetivo and self.objetivo.vivo:
                dx = self.objetivo.x + self.objetivo.tamaño/2 - self.x
                dy = self.objetivo.y + self.objetivo.tamaño/2 - self.y
                distancia = math.hypot(dx, dy)

                if distancia != 0:
                    self.x += (dx / distancia) * self.vel
                    self.y += (dy / distancia) * self.vel

    def seleccionar_objetivo(self, enemigos):
            """Selecciona un enemigo vivo de la lista para seguirlo."""
            vivos = [e for e in enemigos if e.vivo]
            if vivos:
                # Escoge uno al azar o el más cercano
                self.objetivo = min(vivos, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))
            else:
                self.objetivo = None

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


