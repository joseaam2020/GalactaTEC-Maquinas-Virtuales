import pygame

class DisparoEnemigo:
    def __init__(self, x, y, tipo="basico"):
        """
        tipo puede ser 'basico' o 'cargado'
        """
        self.x = x
        self.y = y
        self.tipo = tipo
        self.velocidad = 5 if tipo == "basico" else 3
        self.radio = 5 if tipo == "basico" else 8
        self.color = (0, 255, 0) if tipo == "basico" else (0, 128, 255)  # verde / azul
        self.activo = True

        # daño y penetración de escudo
        self.daño = 0.5 if tipo == "basico" else 1.0
        self.penetracion_escudo = 1 if tipo == "basico" else 2

    def mover(self):
        """Mueve el disparo hacia abajo"""
        self.y += self.velocidad
        if self.y > 800:
            self.activo = False

    def dibujar(self, superficie):
        """Dibuja el disparo"""
        if self.activo:
            pygame.draw.circle(
                superficie,
                self.color,
                (int(self.x), int(self.y)),
                self.radio
            )

    def colisiona_con(self, jugador):
        """Detecta colisión con el jugador"""
        rect_disparo = pygame.Rect(
            self.x - self.radio, self.y - self.radio, self.radio * 2, self.radio * 2
        )
        rect_jugador = pygame.Rect(
            jugador.x, jugador.y, jugador.tamaño, jugador.tamaño
        )
        return rect_disparo.colliderect(rect_jugador)