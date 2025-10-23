import pygame
from enum import Enum
from math import pi, cos, sin, sqrt, atan2

class Direcciones(Enum):
    Ninguna = None
    Este = 2*pi
    Noreste = pi/4
    Norte = pi/2
    Noroeste = 3*pi / 4
    Oeste = pi
    Suroeste = -3*pi/4
    Sur = -pi/2
    Sureste = -pi/4

def diff_ang(a, b):
    d = a - b
    while d > pi:
        d -= 2*pi
    while d < -pi:
        d += 2*pi
    return abs(d)

def distancia_entre_puntos(a, b):
    return sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

def angulo_entre_puntos(ref, obj):
    angulo = atan2(-(obj[1] - ref[1]), obj[0] - ref[0])
    angulos_enum = [d for d in Direcciones if d != Direcciones.Ninguna]
    direccion = min(angulos_enum, key=lambda d: diff_ang(angulo, d.value))
    return direccion 

def comprobación_cercania(ref, obj, epsilon = 10):
    return distancia_entre_puntos(ref, obj) <= epsilon



class Objeto_animado(pygame.sprite.Sprite):
    def __init__(self, surface, imagenes, x, y, velocidad = 0, direccion = Direcciones.Ninguna):
        super().__init__()
        self.surface = surface
        self.frames = self._cargar_frames(imagenes)
        self.frame_actual = self.frames[0]
        self.rect = self.frame_actual.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (x, y)
        self.velocidad = velocidad
        self.direccion = direccion
    
    def update(self, delta_t):
        self._mover(delta_t)
        self.rect = self.frame_actual.get_rect(center=(self.x, self.y))
        self.surface.blit(self.frame_actual, self.rect)
    
    def _cargar_frames(self, lista):
        nuevo = []
        for i in lista:
            nuevo.append(pygame.image.load(i).convert_alpha())
        return nuevo
    
    def _mover(self, delta_t):
        if self.direccion.value:
            self.x += self.velocidad * cos(self.direccion.value) * delta_t
            self.y -= self.velocidad * sin(self.direccion.value) * delta_t




class Objeto_con_trayectoria(Objeto_animado):
    def __init__(self, surface,  imagenes, x, y, velocidad=0, direccion=Direcciones.Ninguna, trayectoria = ((0,0))):
        super().__init__(surface, imagenes, x, y, velocidad, direccion)
        self.trayectoria = trayectoria
        self.objetivo_actual = 0
        self.cambio_objetivo = 1
    
    def update(self, delta_t):
        if comprobación_cercania((self.x, self.y), self.trayectoria[self.objetivo_actual]):
            self.objetivo_actual += self.cambio_objetivo
            if self.objetivo_actual >= len(self.trayectoria):
                self.objetivo_actual = len(self.trayectoria) - 2
                self.cambio_objetivo = -1
            elif self.objetivo_actual < 0:
                self.objetivo_actual = 1
                self.cambio_objetivo = 1
        self.direccion = angulo_entre_puntos((self.x, self.y), self.trayectoria[self.objetivo_actual])
        self._mover(delta_t)
        self.rect = self.frame_actual.get_rect(center=(self.x, self.y))
        self.surface.blit(self.frame_actual, self.rect)



class Nave_jugador(Objeto_animado):
    def __init__(self, surface, jugador, imagenes, x, y, velocidad, direccion=Direcciones.Ninguna):
        super().__init__(surface, imagenes, x, y, velocidad, direccion)
        self.tipo_disparo = 0
        self.jugador = jugador
        self.balas_disparadas = pygame.sprite.Group()
    
    def update(self, delta_t):
        self._mover(delta_t)
        if self.x < 0:
            self.x = self.surface.get_width()
        elif self.x > self.surface.get_width():
            self.x = 0
        self.rect = self.frame_actual.get_rect(center=(self.x, self.y))
        self.surface.blit(self.frame_actual, self.rect)
        self.balas_disparadas.update(delta_t)
    
    def set_direccion(self, direccion = 0):
        match direccion:
            case 0:
                self.direccion = Direcciones.Ninguna
            case 1:
                self.direccion = Direcciones.Este
            case 2:
                self.direccion = Direcciones.Oeste
    
    def disparar(self):
        bala = Disparo_basico_Jugador(
            surface=self.surface,
            imagenes=["GalactaTEC-Maquinas-Virtuales/juego/bala prueba.png"],
            x=self.x,
            y=self.y-self.rect.height/2,
            velocidad=300,
            direccion=Direcciones.Norte)
        return bala


class Disparo_basico_Jugador(Objeto_animado):
    def __init__(self, surface, imagenes, x, y, velocidad=0, direccion=Direcciones.Norte):
        super().__init__(surface, imagenes, x, y, velocidad, direccion)
    
    def update(self, delta_t):
        if self.y < 0:
            self.kill()
        self._mover(delta_t)
        self.rect = self.frame_actual.get_rect(center=(self.x, self.y))
        self.surface.blit(self.frame_actual, self.rect)