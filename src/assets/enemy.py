import pygame
import os
import random
from assets.colors import Colors
from assets.enemy_projectile import DisparoEnemigo
from assets.sound_manager import SoundManager

class Enemigo:
    def __init__(self, x, y, screen, image_path=None):
        self.x_inicial = x
        self.y_inicial = y
        self.x = x
        self.y = y
        self.tamaño = 40
        self.vivo = True
        self.ALTO = screen.get_size()[1]
        self.ya_disparo_cargado = False

        
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

        self.tiempo_ultimo_disparo = 0

    def dibujar(self, superficie):
        if self.vivo:
            superficie.blit(self.imagen, (self.x, self.y))

    def mover(self, dx, dy):
        if self.vivo:
            self.x += dx
            self.y += dy
            if self.y > self.ALTO:
                self.y = -self.tamaño

    def colisiona_con_disparo(self, disparo):
        return self.vivo and pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(disparo.x - disparo.radio, disparo.y - disparo.radio, disparo.radio*2, disparo.radio*2)
        )

    def colisiona_con_jugador(self, jugador):
        return self.vivo and pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(jugador.x, jugador.y, jugador.tamaño, jugador.tamaño)
        )
    
    def puede_disparar(self):
        # Solo dispara si está completamente dentro de la pantalla
        return (
            self.vivo and
            (0 <= self.x <= 1280) and
            (self.tamaño <= self.y <= self.ALTO - self.tamaño)
        )

    def disparar(self, tipo, nivel=None):
        if not self.vivo:
            return None

        if tipo == "cargado":
            if getattr(self, "ya_disparo_cargado", False):
                return None 
            else:
                self.ya_disparo_cargado = True

        # Posición inicial del disparo (centro inferior del enemigo)
        x = self.x + self.tamaño // 2
        y = self.y + self.tamaño
        # El sonido del disparo lo maneja `DisparoEnemigo` para permitir
        # variaciones por nivel (evitar duplicar la reproducción aquí).
        return DisparoEnemigo(x, y, tipo, nivel=nivel)

 
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
        self.ya_disparo_cargado = False
