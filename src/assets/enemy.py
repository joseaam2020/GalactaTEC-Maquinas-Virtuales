import pygame
import os
from assets.colors import Colors 

class Enemigo:
    def __init__(self, x, y, screen):
        self.x_inicial = x
        self.y_inicial = y
        self.x = x
        self.y = y
        self.tamaño = 40
        self.vivo = True
        self.ALTO = screen.get_size()[1]

        ruta_img = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "imgs", "enemigo.png")
        ruta_img = os.path.abspath(ruta_img)  # Convierte a ruta absoluta, por seguridad
        self.imagen = pygame.image.load(ruta_img).convert_alpha()
        self.imagen = pygame.transform.scale(self.imagen, (self.tamaño, self.tamaño))

    def dibujar(self, superficie):
        if self.vivo:
            superficie.blit(self.imagen, (self.x, self.y))
 
    def colisiona_con_disparo(self, disparo):
        return self.vivo and pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(disparo.x - disparo.radio, disparo.y - disparo.radio, disparo.radio*2, disparo.radio*2)
        )
 
    def colisiona_con_jugador(self, jugador):
        return self.vivo and pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(jugador.x, jugador.y, jugador.tamaño, jugador.tamaño)
        )
 
    def mover(self, dx, dy):
        if self.vivo:
            self.x += dx
            self.y += dy
            if self.y > self.ALTO:
                self.y = -self.tamaño  # reaparece arriba
 
    def reiniciar(self):
        self.x = self.x_inicial
        self.y = self.y_inicial
        self.vivo = True
