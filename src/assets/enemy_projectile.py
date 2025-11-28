import os
import pygame

class DisparoEnemigo:
    # Caché de sonidos para no recargar en cada disparo
    _sound_basic = None
    _sound_charged = None
    # Cachés por nivel: {nivel: Sound}
    _sound_basic_by_level = {}
    _sound_charged_by_level = {}

    def __init__(self, x, y, tipo='basico', velocidad=5, nivel=None, *args, **kwargs):
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

        # Cargar sonidos (una sola vez por clase o por nivel)
        # Intentar cargar sonido específico de nivel si se proporciona `nivel`.
        basic_sound = None
        charged_sound = None
        try:
            if nivel is not None:
                # Buscar en caché por nivel
                basic_sound = DisparoEnemigo._sound_basic_by_level.get(nivel)
                charged_sound = DisparoEnemigo._sound_charged_by_level.get(nivel)
                # Intentar cargar archivos específicos por nivel. Se prueban varios candidatos
                # Posibles nombres: enemigo_disparo_basico_lvl{n}.wav, enemigo_disparo_basico_lvl{n}.mp3,
                # disparo{n}.mp3 (p.ej. disparo2.mp3), y lo equivalente para 'cargado'.
                def try_load(candidates):
                    for fname in candidates:
                        ruta = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "audio", fname)
                        ruta_abs = os.path.abspath(ruta)
                        if os.path.exists(ruta_abs):
                            try:
                                s = pygame.mixer.Sound(ruta_abs)
                                return s
                            except Exception:
                                continue
                    return None

                if basic_sound is None:
                    basic_candidates = [
                        f"enemigo_disparo_basico_lvl{nivel}.wav",
                        f"enemigo_disparo_basico_lvl{nivel}.mp3",
                        f"disparo{nivel}.mp3",
                        f"disparo_normal.wav",
                    ]
                    basic_sound = try_load(basic_candidates)
                    if basic_sound:
                        basic_sound.set_volume(0.30)
                        DisparoEnemigo._sound_basic_by_level[nivel] = basic_sound

                if charged_sound is None:
                    charged_candidates = [
                        f"enemigo_disparo_cargado_lvl{nivel}.wav",
                        f"enemigo_disparo_cargado_lvl{nivel}.mp3",
                        f"disparo{nivel}.mp3",
                        f"disparo_rastreador.wav",
                    ]
                    charged_sound = try_load(charged_candidates)
                    if charged_sound:
                        charged_sound.set_volume(0.40)
                        DisparoEnemigo._sound_charged_by_level[nivel] = charged_sound

            # Si no se encontraron versiones por nivel, cargar los por-defecto únicos
            if basic_sound is None:
                if DisparoEnemigo._sound_basic is None:
                    try:
                        ruta_basic = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "audio", "enemigo_disparo_basico.wav")
                        DisparoEnemigo._sound_basic = pygame.mixer.Sound(os.path.abspath(ruta_basic))
                        DisparoEnemigo._sound_basic.set_volume(0.30)
                    except Exception:
                        DisparoEnemigo._sound_basic = None
                basic_sound = DisparoEnemigo._sound_basic

            if charged_sound is None:
                if DisparoEnemigo._sound_charged is None:
                    try:
                        ruta_charged = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "audio", "enemigo_disparo_cargado.wav")
                        DisparoEnemigo._sound_charged = pygame.mixer.Sound(os.path.abspath(ruta_charged))
                        DisparoEnemigo._sound_charged.set_volume(0.40)
                    except Exception:
                        DisparoEnemigo._sound_charged = None
                charged_sound = DisparoEnemigo._sound_charged
        except Exception:
            basic_sound = DisparoEnemigo._sound_basic
            charged_sound = DisparoEnemigo._sound_charged

        # Reproducir sonido según tipo de disparo
        try:
            if str(self.tipo).lower() in ('cargado', 'charged', '2'):
                if charged_sound:
                    charged_sound.play()
            else:
                if basic_sound:
                    basic_sound.play()
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