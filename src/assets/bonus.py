import pygame
import random
from assets.colors import Colors
import os
import time

class Bonus:
    TIPOS = ["vida", "doble_puntos", "escudo", "rastreador", "area"]

    # Cargar la imagen del bonus (imagen común para todos)
    RUTA_IMAGEN = os.path.join("resources", "imgs", "bonus.png")
    IMAGEN_BONUS = None  # se inicializa más adelante

    def __init__(self, tipo):
        self.tipo = tipo
        self.x = 0 
        self.y = -20
        self.vel = 1  # más lento
        self.tamaño = 40
        self.activo = True
        self.ALTO = 0

        # Variables de animación al ser recogido
        self.recogido = False
        self.anim_tiempo_inicio = 0
        self.anim_duracion = 0.6  # segundos
        self.anim_radio = 0.5

        # Cargar la imagen si no se ha hecho aún
        if Bonus.IMAGEN_BONUS is None:
            if os.path.exists(Bonus.RUTA_IMAGEN):
                imagen = pygame.image.load(Bonus.RUTA_IMAGEN).convert_alpha()
                Bonus.IMAGEN_BONUS = pygame.transform.scale(imagen, (self.tamaño, self.tamaño))
            else:
                print(f"[⚠️] No se encontró la imagen del bonus en {Bonus.RUTA_IMAGEN}")
                Bonus.IMAGEN_BONUS = pygame.Surface((self.tamaño, self.tamaño))
                Bonus.IMAGEN_BONUS.fill((255, 0, 255))  # magenta como marcador de error

    def mover(self):
        if not self.recogido:  # solo se mueve si no fue recogido
            self.y += self.vel
            if self.y > self.ALTO:
                self.activo = False

    def dibujar(self, superficie):
        if not self.ALTO:
            self.ALTO = superficie.get_size()[1]
        if not self.x:
            self.x = random.randint(20, superficie.get_size()[0] - 40)

        if not self.recogido:
            superficie.blit(Bonus.IMAGEN_BONUS, (self.x, self.y))
        else:
            # Animación de brillo / explosión
            tiempo_pasado = time.time() - self.anim_tiempo_inicio
            progreso = tiempo_pasado / self.anim_duracion
            if progreso < 1:
                alpha = max(0, 255 - int(progreso * 255))
                self.anim_radio = int(30 + 50 * progreso)

                efecto = pygame.Surface((self.anim_radio * 2, self.anim_radio * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    efecto,
                    (255, 255, 100, alpha),  # color amarillento brillante
                    (self.anim_radio, self.anim_radio),
                    self.anim_radio,
                )
                superficie.blit(efecto, (self.x - self.anim_radio + self.tamaño // 2,
                                         self.y - self.anim_radio + self.tamaño // 2))
            else:
                self.activo = False  # fin de animación

    def colisiona_con(self, jugador):
        rect_bonus = pygame.Rect(self.x, self.y, self.tamaño, self.tamaño)
        rect_jugador = pygame.Rect(jugador.x, jugador.y, jugador.tamaño, jugador.tamaño)
        if rect_bonus.colliderect(rect_jugador):
            self.iniciar_animacion()
            return True
        return False
    
    def iniciar_animacion(self):
        """Llama esto al ser recogido para iniciar la animación."""
        self.recogido = True
        self.anim_tiempo_inicio = time.time()
