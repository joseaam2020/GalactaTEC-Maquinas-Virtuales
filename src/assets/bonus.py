import pygame
import random
from assets.colors import Colors

class Bonus:
    TIPOS = ["vida", "doble_puntos", "escudo", "rastreador", "area"]
    COLORES = {
            "vida": Colors.VERDE,
            "doble_puntos": Colors.AMARILLO,
            "escudo": Colors.CYAN,
            "rastreador": Colors.MORADO,
            "area": Colors.ROJO}

    def __init__(self, tipo):
        self.tipo = tipo
        self.color = Bonus.COLORES[tipo]
        self.x = 0 
        self.y = -20
        self.vel = 1  # más lento
        self.tamaño = 20
        self.activo = True
        self.ALTO = 0

    def mover(self):
        self.y += self.vel
        if self.y > self.ALTO:
            self.activo = False

    def dibujar(self, superficie):
        if(not self.ALTO):
            self.ALTO = superficie.get_size()[1]
        if(not self.x):
            self.x = random.randint(20, superficie.get_size()[0] - 40)
        pygame.draw.rect(superficie, self.color, (self.x, self.y, self.tamaño, self.tamaño))

    def colisiona_con(self, jugador):
        return pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(jugador.x, jugador.y, jugador.tamaño, jugador.tamaño)
        )
