import pygame
import os

class SoundManager:
    sonidos = {}
    inicializado = False
    base_path = "./resources/audio/"

    @staticmethod
    def init():
        if SoundManager.inicializado:
            return
        pygame.mixer.init()


        SoundManager.sonidos = {
            "disparo_normal": SoundManager.cargar(SoundManager.base_path,"disparo_normal.wav"),
            "disparo_area": SoundManager.cargar(SoundManager.base_path,"disparo_area.wav"),
            "disparo_rastreador": SoundManager.cargar(SoundManager.base_path,"disparo_rastreador.wav"),
            "enemigo_muere": SoundManager.cargar(SoundManager.base_path,"enemigo_muere.wav"),
            "bonus": SoundManager.cargar(SoundManager.base_path,"bonus.wav"),
            "jugador_mueve": SoundManager.cargar(SoundManager.base_path,"jugador_mueve.wav"),
            "fanfarria": SoundManager.cargar(SoundManager.base_path, "fanfarria.wav"),
        }

        # Ajusta volúmenes
        disparo_area = SoundManager.sonidos["disparo_area"]
        if(disparo_area):
            disparo_area.set_volume(0.8)

        enemigo_muere = SoundManager.sonidos["enemigo_muere"]
        if(enemigo_muere):
            enemigo_muere.set_volume(0.7)

        disparo_normal = SoundManager.sonidos["disparo_normal"]
        if(disparo_normal):
            disparo_normal.set_volume(0.5)

        jugador_mueve = SoundManager.sonidos["jugador_mueve"]
        if(jugador_mueve):
            jugador_mueve.set_volume(0.1)

        fanfarria = SoundManager.sonidos.get("fanfarria")
        if fanfarria:
            # Subir un poco el volumen de la fanfarria
            fanfarria.set_volume(0.60)

        SoundManager.inicializado = True

    @staticmethod
    def play(nombre):
        """Reproduce un sonido si existe"""
        if not SoundManager.inicializado:
            SoundManager.init()
        sonido = SoundManager.sonidos.get(nombre)
        if sonido:
            sonido.play()

    @staticmethod
    def cargar(base_path,nombre):
        ruta = os.path.abspath(os.path.join(base_path, nombre))
        if not os.path.exists(ruta):
            print(f"⚠️ No se encontró el sonido: {ruta}")
            return None
        return pygame.mixer.Sound(ruta)

    @staticmethod
    def cargar_musica(base_path, nombre):
        ruta = os.path.abspath(os.path.join(base_path, nombre))
        if not os.path.exists(ruta):
            print(f"⚠️ No se encontró el sonido: {ruta}")
            return False
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
        return True
