import pygame
import os
from assets.colors import Colors 

class Enemigo:
    def __init__(self, x, y, screen, image_path=None):
        self.x_inicial = x
        self.y_inicial = y
        self.x = x
        self.y = y
        self.tamaño = 40
        self.vivo = True
        self.ALTO = screen.get_size()[1]
        # Si se proporciona una ruta de imagen, usarla; si no, usar el enemy por defecto
        try:
            if image_path:
                ruta_img = image_path
            else:
                ruta_img = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "imgs", "enemigo.png")
                ruta_img = os.path.abspath(ruta_img)
            self.imagen = pygame.image.load(ruta_img).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (self.tamaño, self.tamaño))
        except Exception:
            # Fallback: crear superficie simple si la imagen falla
            self.imagen = pygame.Surface((self.tamaño, self.tamaño), pygame.SRCALPHA)
            self.imagen.fill((200, 50, 50))

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
