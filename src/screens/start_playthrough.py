import pygame
import time

from pygame.color import Color
from assets.colors import Colors
from assets.level import Level


class Level1(Level):
    def __init__(self, manager):
        super().__init__(manager)  # Llama al constructor de Level
        
        # Personalización específica de Level 1
        self.nivel = 1
        self.jugador.vida = 5  # Por ejemplo, más vidas al comenzar
        self.vel_x = 1         # Enemigos más lentos
        self.vel_y = 15
        self.puntos_para_siguiente_nivel = 100  # Requiere menos puntos

        # Cambiar formación inicial de enemigos (8 filas)
        self.filas = 8
        self.crear_formacion_enemigos()

        # Mostrar un tutorial o mensaje introductorio si quieres
        self.mostrar_tutorial = True
        self.tiempo_inicio = time.time()

    def draw(self, surface):
        super().draw(surface)

