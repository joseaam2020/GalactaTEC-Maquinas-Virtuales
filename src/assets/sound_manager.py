import pygame
import os

class SoundManager:
    sonidos = {}
    inicializado = False

    @staticmethod
    def init():
        if SoundManager.inicializado:
            return
        pygame.mixer.init()
        base_path = os.path.join(os.path.dirname(__file__), "../../resources/audio")

        def cargar(nombre):
            ruta = os.path.abspath(os.path.join(base_path, nombre))
            if not os.path.exists(ruta):
                print(f"⚠️ No se encontró el sonido: {ruta}")
                return None
            return pygame.mixer.Sound(ruta)

        SoundManager.sonidos = {
            "disparo_normal": cargar("disparo_normal.wav"),
            "disparo_area": cargar("disparo_area.wav"),
            "disparo_rastreador": cargar("disparo_rastreador.wav"),
            "enemigo_muere": cargar("enemigo_muere.wav"),
            "bonus": cargar("bonus.wav"),
            "jugador_mueve": cargar("jugador_mueve.wav"),
        }

        # Ajusta volúmenes
        SoundManager.sonidos["disparo_area"].set_volume(0.7)
        SoundManager.sonidos["enemigo_muere"].set_volume(0.6)

        SoundManager.inicializado = True

    @staticmethod
    def play(nombre):
        """Reproduce un sonido si existe"""
        if not SoundManager.inicializado:
            SoundManager.init()
        sonido = SoundManager.sonidos.get(nombre)
        if sonido:
            sonido.play()