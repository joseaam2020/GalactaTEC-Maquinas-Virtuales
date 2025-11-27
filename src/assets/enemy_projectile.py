import os
import pygame

class DisparoEnemigo:
    # Caché de sonidos para no recargar en cada disparo
    _sound_basic = None
    _sound_charged = None

    def __init__(self, x, y, tipo='basico', velocidad=5, *args, **kwargs):
        """
        tipo puede ser 'basico' o 'cargado'
        """
        self.x = x
        self.y = y
        self.tipo = tipo  # esperar 'basico' / 'cargado' o valores equivalentes
        self.velocidad = velocidad
        self.radio = 5 if tipo == "basico" else 8
        self.color = (0, 255, 0) if tipo == "basico" else (0, 128, 255)  # verde / azul
        self.activo = True

        # daño y penetración de escudo
        self.daño = 0.5 if tipo == "basico" else 1.0
        self.penetracion_escudo = 1 if tipo == "basico" else 2

        # Cargar sonidos (una sola vez por clase)
        if DisparoEnemigo._sound_basic is None:
            try:
                ruta_basic = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "audio", "enemigo_disparo_basico.wav")
                DisparoEnemigo._sound_basic = pygame.mixer.Sound(os.path.abspath(ruta_basic))
                # Reducir volumen por defecto (0.0 a 1.0)
                DisparoEnemigo._sound_basic.set_volume(0.30)
            except Exception:
                DisparoEnemigo._sound_basic = None

        if DisparoEnemigo._sound_charged is None:
            try:
                ruta_charged = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "audio", "enemigo_disparo_cargado.wav")
                DisparoEnemigo._sound_charged = pygame.mixer.Sound(os.path.abspath(ruta_charged))
                # Volumen ligeramente superior al básico para distinguirlo
                DisparoEnemigo._sound_charged.set_volume(0.40)
            except Exception:
                DisparoEnemigo._sound_charged = None

        # Reproducir sonido según tipo de disparo
        try:
            if str(self.tipo).lower() in ('cargado', 'charged', '2'):
                if DisparoEnemigo._sound_charged:
                    DisparoEnemigo._sound_charged.play()
            else:
                if DisparoEnemigo._sound_basic:
                    DisparoEnemigo._sound_basic.play()
        except Exception:
            pass

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