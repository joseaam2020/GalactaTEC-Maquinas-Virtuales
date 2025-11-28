import pygame
import time
import random
import sys
import math
import os
from widgets.userinfo import UserInfo
from widgets.helpbutton import HelpButton
from assets.player import Jugador
from assets.enemy import Enemigo
from assets.bonus import Bonus
from assets.colors import Colors
from assets.enemy_projectile import DisparoEnemigo
from assets.sound_manager import SoundManager

class Level:
    ANCHO, ALTO = 1280, 720
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Juego GalactaTEC")
    clock = pygame.time.Clock()

    def __init__(self, manager):
        self.fuente = pygame.font.Font(None, 28)
        self.manager = manager  # Referencia al StateManager
        # Crear instancias separadas por jugador para poder alternar realmente
        self.jugadores_inst = {
            1: Jugador(manager.screen),
            2: Jugador(manager.screen)
        }
        # Intentar dar una apariencia distinta al jugador 2 si existe la imagen
        try:
            ruta_j2 = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "imgs", "player_ship_2.png")
            ruta_j2 = os.path.abspath(ruta_j2)
            if os.path.exists(ruta_j2):
                self.jugadores_inst[2].cambiar_imagen(ruta_j2)
        except Exception:
            pass

        # Referencia al jugador activo
        self.jugador = self.jugadores_inst[1]
        self.disparos = []
        self.bonus_actual = None
        self.bonus_usados_nivel = set()
        self.ultimo_bonus_tiempo = time.time()
        self.siguiente_bonus = random.randint(3, 4)
        self.nivel = 1
        self.tipo_patron = 1
        self.pausado = False
        self.disparos_enemigos = []
        self.ultimo_disparo_enemigo = 0
        self.frecuencia_disparo = 1000  # milisegundos entre disparos
        self.explosiones = []
        
        # Número máximo de niveles por playthrough
        self.max_niveles = 3

        # Control de animación del brillo de bonus activos
        self.tiempo_inicio = time.time()

        # === SISTEMA DE TURNOS ===
        self.jugador_actual = 1  # 1 o 2
        self.total_jugadores = 2  # Puedes cambiarlo a 1 para single player
        
        # Guardar estado de cada jugador (vidas iniciales = 5)
        self.jugadores_data = {
            1: {"puntos": 0, "vidas": 5, "bonus_teclas": {i: 0 for i in range(1, 6)}, "finished": False, "nivel": 1},
            2: {"puntos": 0, "vidas": 5, "bonus_teclas": {i: 0 for i in range(1, 6)}, "finished": False, "nivel": 1}
        }
        
        # === POPUP DE CAMBIO DE TURNO ===
        self.popup_active = False
        self.popup_font = pygame.font.Font(None, 40)
        self.game_paused = False
        # Cuando true evita que otros popups sobrescriban el destino del botón
        self.popup_locked = False
        
        popup_width, popup_height = 500, 300
        self.popup_rect = pygame.Rect(
            (Level.ANCHO - popup_width) // 2,
            (Level.ALTO - popup_height) // 2,
            popup_width,
            popup_height
        )
        
        # Importar Button
        from widgets.button import Button
        
        # Botón OK del popup (se crea aquí pero se posiciona cuando se muestra)
        self.popup_button = Button(
            text="Continue",
            pos=(0, 0),  # Se actualizará en show_player_lost_popup
            font=self.popup_font,
            on_click=self.cambiar_turno,
            size=(250, 60)
        )

        # Fondo
        ruta_fondo = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "imgs", "fondo.png")
        ruta_fondo = os.path.abspath(ruta_fondo)
        imagen = pygame.image.load(ruta_fondo).convert()
        
        # Ajustar manteniendo proporción y cubrir pantalla
        ancho_fondo, alto_fondo = imagen.get_size()
        ratio_x = Level.ANCHO / ancho_fondo
        ratio_y = Level.ALTO / alto_fondo
        ratio = max(ratio_x, ratio_y)
        nuevo_ancho = int(ancho_fondo * ratio)
        nuevo_alto = int(alto_fondo * ratio)
        self.fondo = pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))
        
        self.fondo_y = 0        # posición inicial vertical
        self.fondo_vel = 1      # velocidad de scroll

        # Crear enemigos
        self.enemigos = []
        self.espacio_x = 55
        self.espacio_y = 55
        self.filas = 8
        self.crear_formacion_enemigos()
        # Se inicializa con la formación actual (solo vivos)
        self.enemies_to_shoot = [e for e in self.enemigos if e.vivo]
        random.shuffle(self.enemies_to_shoot)  # mezcla el orden para aleatoriedad

        self.direccion_x = 1
        self.vel_x = 2
        self.vel_y = 20

        self.game_over = False
        # Flag para suprimir un popup inmediatamente después de ciertos eventos (p.ej. escudo absorbe impacto)
        self.suppress_popup = False
        # Flag para indicar que al reiniciar el nivel deben limpiarse los bonuses activos del jugador
        self.clear_bonuses_on_restart = False

        # Cargar íconos de bonus para HUD
        self.iconos_bonus = {}
        nombres_bonus = {
            1: "bonus_vida.png",
            2: "bonus_escudo.png",
            3: "bonus_doble_puntos.png",
            4: "bonus_area.png",
            5: "bonus_rastreador.png"
        }

        for tecla, archivo in nombres_bonus.items():
            ruta_icono = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "imgs", archivo)
            ruta_icono = os.path.abspath(ruta_icono)
            if os.path.exists(ruta_icono):
                self.iconos_bonus[tecla] = pygame.transform.scale(
                    pygame.image.load(ruta_icono).convert_alpha(), (40, 40)
                )
            else:
                print(f" No se encontró el icono de bonus: {ruta_icono}")
                self.iconos_bonus[tecla] = None

        # Detectar Control
        self.joystick = None
        if pygame.joystick.get_count() == 0:
            print("No se detectó ningún control. Se utilizan flechas de teclado")
        else:
            # Inicializar el joystick (DualShock 4)
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Control detectado: {self.joystick.get_name()}")
            self.bonus_num = 0
            self.tiempo_ultimo_disparo = 0
            self.tiempo_ultimo_boton = 0
            self.cooldown_disparo = 100  # milisegundos


        # Informacion jugadores
        self.user_1_info = UserInfo(
                font=self.fuente,
                pos=(20, 20),
                size=(100, 100),
                name="Player 1",
                photo="./resources/imgs/disponible.png"
            )

        self.user_2_info = UserInfo(
                font=self.fuente,
                pos=(Level.ANCHO - 120, 20),
                size=(100, 100),
                name="Player 2",
                photo="./resources/imgs/disponible.png"
        )

        help_text = (
            "Welcome to GalactaTEC!\n\n"
            "Your goal is to destroy all enemy waves before they reach you or drain your lives.\n\n"
            "- Move Left/Right: Use the arrow keys to move your ship horizontally.\n\n"
            "- Shoot: Press SPACE to fire at incoming enemies.\n\n"
            "- Adjust Volume: Press J to lower the music volume and K to increase it.\n\n"
            "- Use Bonus: Press keys 1–5 to activate collected power-ups.\n\n"
            "- Bonuses: Catch the floating bonus icons to gain special effects — extra life, shield, double points, area shot, or homing shot.\n\n"
            "- Lives: Your remaining lives appear at the bottom-left corner of the screen.\n\n"
            "- Bonus Bar: Active and available bonuses are displayed at the bottom-right corner. Active ones glow with a blue frame.\n\n"
            "- Scoring: Each enemy destroyed gives you points. With the double-points bonus, you earn twice as much.\n\n"
            "- Levels: When all enemies are defeated, you advance to the next level, where movement patterns and difficulty increase.\n\n"
            "- Game Over: If you lose all your lives, the game ends. Try again and beat your high score!\n\n"
            "Tip: Use your bonuses strategically and keep moving — the galaxy depends on you!\n\n"
        )
        self.help_button = HelpButton(
                font=pygame.font.Font(None,20), 
                title="Options",
                text=help_text,
                pos=(10,Level.ALTO-30),
                screen_size=[Level.ANCHO,Level.ALTO]
        )

        # Cargar estado inicial del jugador 1
        self.cargar_estado_jugador(1)
        # Tipo de popup actual ('lost' o 'level_cleared')
        self.popup_type = None

    def guardar_estado_jugador(self, jugador_num):
        """Guarda el estado actual del jugador en jugadores_data"""
        # Guardar desde la instancia del jugador
        self.jugadores_data[jugador_num]["puntos"] = self.jugadores_inst[jugador_num].puntos
        self.jugadores_data[jugador_num]["vidas"] = self.jugadores_inst[jugador_num].vida
        self.jugadores_data[jugador_num]["bonus_teclas"] = self.jugadores_inst[jugador_num].bonus_teclas.copy()
        # Guardar nivel actual del jugador
        try:
            self.jugadores_data[jugador_num]["nivel"] = self.nivel
        except Exception:
            pass

    def cargar_estado_jugador(self, jugador_num):
        """Carga el estado del jugador desde jugadores_data"""
        # Apuntar la referencia al jugador correspondiente
        self.jugador = self.jugadores_inst[jugador_num]
        # Cargar los valores guardados en la instancia
        self.jugador.puntos = self.jugadores_data[jugador_num]["puntos"]
        self.jugador.vida = self.jugadores_data[jugador_num]["vidas"]
        self.jugador.bonus_teclas = self.jugadores_data[jugador_num]["bonus_teclas"].copy()
        # Cargar y aplicar el nivel del jugador
        try:
            nivel_j = self.jugadores_data[jugador_num].get("nivel", 1)
            self.nivel = nivel_j
        except Exception:
            pass
        # Actualizar el patrón de vuelo según el jugador actual (si hay mapping de usernames)
        try:
            username = None
            if hasattr(self, 'player_usernames'):
                username = self.player_usernames.get(jugador_num)
            if not username:
                # fallback a manager.current_player si existe
                username = getattr(self.manager, 'current_player', None)
            if username and username in getattr(self.manager, 'patterns', {}):
                patrones = self.manager.patterns[username]
                # Obtener patrón para el nivel actual (por defecto mantener self.tipo_patron)
                patron = patrones.get(self.nivel, None)
                if patron is not None:
                    self.tipo_patron = patron
        except Exception:
            pass
        # Asegurar que los widgets muestren los nombres correctos si hay mapping de usernames
        try:
            self.update_userinfo_names()
        except Exception:
            pass

    def show_player_lost_popup(self):
        """Muestra el popup cuando el jugador pierde una vida"""
        # Si se marcó suprimir popup (p. ej. impacto absorbido por escudo), no mostrarlo
        if getattr(self, 'suppress_popup', False):
            try:
                self.suppress_popup = False
            except Exception:
                pass
            return
        self.popup_type = 'lost'
        self.popup_active = True
        self.game_paused = True

        # Pausar música mientras el popup está activo
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

        # Asegurar que el botón cierre popup y cambie turno (o continue en singleplayer)
        # Si el popup está bloqueado (ej. Game Over), no sobrescribimos el destino.
        if getattr(self, 'popup_locked', False):
            pass
        else:
            if getattr(self, 'total_jugadores', 1) <= 1:
                # Single-player: no cambiar turno, solo continuar el mismo jugador
                self.popup_button.on_click = self.continue_singleplayer_after_loss
            else:
                self.popup_button.on_click = self.cambiar_turno
        self.popup_button.update_text("Continue")
        try:
            self.popup_button.text_surf = self.popup_font.render(self.popup_button.text, True, (255,255,255))
        except Exception:
            pass

        # Actualizar posición del botón OK
        button_x = self.popup_rect.centerx - 125
        button_y = self.popup_rect.bottom - 80
        self.popup_button.update_pos((button_x, button_y))

        # Pausar la música o efectos si se desea (opcional)

    def cambiar_turno(self):
        """Cambia al siguiente jugador"""
        # Guardar estado del jugador actual
        self.guardar_estado_jugador(self.jugador_actual)
        
        # Cambiar al siguiente jugador (soporta N jugadores) y saltar jugadores inactivos
        next_index = self.jugador_actual
        found = False
        try:
            total = getattr(self, 'total_jugadores', max(self.jugadores_data.keys()))
            for _ in range(total):
                candidate = (next_index % total) + 1
                next_index = candidate
                data = self.jugadores_data.get(next_index, {})
                vidas = data.get('vidas', 0)
                finished = data.get('finished', False)
                if vidas > 0 and not finished:
                    found = True
                    break
            if not found:
                # No hay jugadores activos: terminar playthrough
                self.show_game_over_popup()
                return
        except Exception:
            # Fallback simple toggle
            next_index = 2 if self.jugador_actual == 1 else 1

        self.jugador_actual = next_index
        
        # Cargar estado del nuevo jugador
        self.cargar_estado_jugador(self.jugador_actual)
        
        # Cerrar popup y reanudar juego
        self.popup_active = False
        self.game_paused = False
        
        # Reiniciar posición del jugador
        self.jugador.x = Level.ANCHO // 2 - self.jugador.tamaño // 2
        self.jugador.y = Level.ALTO - 100
        
        print(f" Turno del Jugador {self.jugador_actual}")
        # Reanudar música al continuar
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass
        # Reiniciar únicamente el nivel: recrear enemigos y limpiar disparos/bonus
        # pero mantener puntos/vidas/bonus_teclas del jugador (ya cargados en self.jugador)
        try:
            # Si este cambio de turno se produce tras una muerte, el flag
            # `clear_bonuses_on_restart` habrá sido seteado por el popup.
            self.restart_level(clear_active_bonuses=getattr(self, 'clear_bonuses_on_restart', False))
        except Exception:
            pass
        finally:
            # Siempre limpiar el flag después del reinicio
            try:
                self.clear_bonuses_on_restart = False
            except Exception:
                pass
        # Actualizar current_player en el StateManager si tenemos mapeo de usernames
        try:
            if hasattr(self, 'player_usernames'):
                username = self.player_usernames.get(self.jugador_actual)
                if username:
                    self.manager.current_player = username
                    # Actualizar el patrón de vuelo según el nuevo jugador
                    try:
                        patrones = self.manager.patterns.get(username, {})
                        patron = patrones.get(self.nivel, None)
                        if patron is not None:
                            self.tipo_patron = patron
                    except Exception:
                        pass
        except Exception:
            pass

    def continue_singleplayer_after_loss(self):
        """Cerrar popup y continuar en modo single-player reiniciando el nivel."""
        self.popup_active = False
        self.game_paused = False
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass
        try:
            # Reiniciar el nivel para que el mismo jugador continúe.
            # Limpiar bonuses activos porque venimos de una pérdida de vida.
            self.restart_level(clear_active_bonuses=True)
        except Exception:
            pass
        # Reposicionar jugador actual
        try:
            self.jugador.x = Level.ANCHO // 2 - self.jugador.tamaño // 2
            self.jugador.y = Level.ALTO - 100
        except Exception:
            pass

    def update_userinfo_names(self):
        """Actualiza los nombres mostrados en los widgets `UserInfo` con los usernames proporcionados.
        Si no hay usernames disponibles, usa 'Player 1'/'Player 2' por defecto."""
        try:
            p1 = None
            p2 = None
            if hasattr(self, 'player_usernames') and isinstance(self.player_usernames, dict):
                p1 = self.player_usernames.get(1)
                p2 = self.player_usernames.get(2)

            # Actualizar nombre de player 1
            if getattr(self, 'user_1_info', None) is not None:
                if p1:
                    self.user_1_info.update_info(name=p1)
                else:
                    self.user_1_info.update_info(name="Player 1")

            # Actualizar nombre de player 2 si existe
            if getattr(self, 'user_2_info', None) is not None:
                if p2:
                    self.user_2_info.update_info(name=p2)
                else:
                    self.user_2_info.update_info(name="Player 2")
        except Exception:
            pass

    def ensure_player_instances(self):
        """Asegura que `self.jugadores_inst` tenga una instancia `Jugador`
        para cada número presente en `self.player_usernames`.
        Llama a esto cuando el mapping de usernames se establezca dinámicamente.
        """
        try:
            if not hasattr(self, 'player_usernames') or not isinstance(self.player_usernames, dict):
                return
            for idx in sorted(k for k in self.player_usernames.keys() if k is not None):
                if idx not in self.jugadores_inst:
                    self.jugadores_inst[idx] = Jugador(self.manager.screen)
        except Exception:
            pass

    def apply_player_usernames(self):
        """Aplicar mapping de `player_usernames` a la instancia Level:
        - crea instancias de jugador según el mapping
        - establece `total_jugadores` y `jugador_actual`
        - actualiza `manager.current_player` y `tipo_patron` para el primer jugador
        - actualiza los UserInfo
        """
        try:
            if not hasattr(self, 'player_usernames') or not isinstance(self.player_usernames, dict):
                return

            # Crear instancias de jugador necesarias
            self.ensure_player_instances()

            # Contar jugadores válidos (filtrar None)
            jugadores_validos = [u for u in [self.player_usernames.get(i) for i in sorted(self.player_usernames.keys())] if u]
            self.total_jugadores = max(1, len(jugadores_validos))

            # Asegurar entries en jugadores_data para cada slot
            for idx in range(1, self.total_jugadores + 1):
                if idx not in self.jugadores_data:
                    self.jugadores_data[idx] = {"puntos": 0, "vidas": 5, "bonus_teclas": {i: 0 for i in range(1, 6)}, "finished": False}

            # Establecer jugador actual a la primera posición
            self.jugador_actual = 1

            # Actualizar manager.current_player con el username del primer slot
            first_username = self.player_usernames.get(1) or getattr(self.manager, 'current_player', None)
            if first_username:
                self.manager.current_player = first_username
                # Establecer patrón inicial según las preferencias guardadas
                try:
                    patrones = self.manager.patterns.get(first_username, {})
                    patron = patrones.get(self.nivel, None)
                    if patron is not None:
                        self.tipo_patron = patron
                except Exception:
                    pass

            # === CARGAR MÚSICA DEL NIVEL ===
            try:
                music_loaded = False
                user_music_map = getattr(self.manager, 'player_music', {})
                music_pref = None
                if user_music_map:
                    music_pref = user_music_map.get(first_username, {}).get(self.nivel)
                if music_pref:
                    from assets.sound_manager import SoundManager
                    music_loaded = SoundManager.cargar_musica("./resources/audio/", music_pref)
                if not music_loaded:
                    default_music = f"game_music{self.nivel}.mp3"
                    from assets.sound_manager import SoundManager
                    SoundManager.cargar_musica("./resources/audio/", default_music)
            except Exception as e:
                print(f"[MUSIC] Error loading music for level {self.nivel}: {e}")

            # Asegurar que el widget muestre los nombres correctos
            try:
                self.update_userinfo_names()
            except Exception:
                pass

            # Cargar estado del primer jugador (poniendo la referencia a self.jugador)
            try:
                self.cargar_estado_jugador(1)
            except Exception:
                pass
            # Recrear la formación para que use la imagen correspondiente al nivel del jugador
            try:
                self.restart_level()
            except Exception:
                pass
        except Exception:
            pass

    def close_popup(self):
        """Cierra el popup y cambia de turno"""
        self.cambiar_turno()

    def show_level_cleared_popup(self):
        """Muestra popup cuando se completó el nivel (todos los enemigos muertos)"""
        # Evitar mostrar popup de nivel completado si justo suprimimos popups
        # (por ejemplo, un enemigo fue destruido por el escudo recientemente).
        if getattr(self, 'suppress_popup', False):
            try:
                self.suppress_popup = False
            except Exception:
                pass
            return
        self.popup_type = 'level_cleared'
        self.popup_active = True
        self.game_paused = True

        # Pausar música mientras el popup está activo
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

        # Cambiar comportamiento del botón: si ya era el último nivel, volver a Options;
        # si no, avanzar al siguiente nivel.
        if getattr(self, 'popup_locked', False):
            # Si el popup está bloqueado por otro flujo (ej. Game Over), no sobrescribimos
            pass
        else:
            # Usar el nivel del jugador actual almacenado en jugadores_data
            nivel_actual = self.jugadores_data.get(self.jugador_actual, {}).get('nivel', self.nivel)
            # Si el jugador completó su último nivel
            if nivel_actual >= getattr(self, 'max_niveles', 3):
                # Marcar jugador actual como finalizado
                try:
                    if self.jugador_actual in self.jugadores_data:
                        self.jugadores_data[self.jugador_actual]['finished'] = True
                except Exception:
                    pass

                # Verificar si quedan jugadores activos (vidas>0 y not finished)
                otros_activos = False
                try:
                    for idx, data in self.jugadores_data.items():
                        if idx == self.jugador_actual:
                            continue
                        if data.get('vidas', 0) > 0 and not data.get('finished', False):
                            otros_activos = True
                            break
                except Exception:
                    otros_activos = False

                if otros_activos:
                    # Pasar turno al siguiente jugador activo
                    self.popup_button.on_click = self.cambiar_turno
                    self.popup_button.update_text("Next Player")
                else:
                    # No hay más jugadores -> terminar playthrough
                    self.popup_button.on_click = self.finish_playthrough
                    self.popup_button.update_text("Continue")
            else:
                # Permitir que el mismo jugador avance al siguiente nivel
                self.popup_button.on_click = self.next_level
                self.popup_button.update_text("Next Level")
        try:
            self.popup_button.text_surf = self.popup_font.render(self.popup_button.text, True, (255,255,255))
        except Exception:
            pass

        # Posicionar el botón
        button_x = self.popup_rect.centerx - 125
        button_y = self.popup_rect.bottom - 80
        self.popup_button.update_pos((button_x, button_y))

    def show_game_over_popup(self):
        """Enviar resultados y terminar la playthrough (fallback muestra popup visual)."""
        try:
            players_data = self._build_players_data()
            # Enviar resultados al estado END_GAME y cambiar de estado
            if hasattr(self, 'manager') and 'END_GAME' in getattr(self.manager, 'states', {}):
                try:
                    self.manager.states["END_GAME"].set_results(players_data)
                except Exception:
                    pass
            try:
                self.manager.change_state("END_GAME")
                return
            except Exception:
                pass
        except Exception:
            pass

        # Fallback visual si no se pudo cambiar al estado END_GAME
        self.popup_type = 'game_over'
        self.popup_active = True
        self.game_paused = True
        self.popup_button.on_click = self.finish_playthrough
        self.popup_locked = True
        self.popup_button.update_text("Continue")
        try:
            self.popup_button.text_surf = self.popup_font.render(self.popup_button.text, True, (255,255,255))
        except Exception:
            pass
        # Posicionar el botón OK
        button_x = self.popup_rect.centerx - 125
        button_y = self.popup_rect.bottom - 80
        self.popup_button.update_pos((button_x, button_y))

    def next_level(self):
        """Avanza al siguiente nivel usando el patrón elegido por el jugador, recrea enemigos."""
        # Incrementar el nivel del jugador actual (progreso por jugador)
        try:
            if self.jugador_actual in self.jugadores_data:
                self.jugadores_data[self.jugador_actual]['nivel'] = self.jugadores_data[self.jugador_actual].get('nivel', self.nivel) + 1
                self.nivel = self.jugadores_data[self.jugador_actual]['nivel']
        except Exception:
            self.nivel = self.nivel + 1

        # Determinar patrón para el siguiente nivel desde manager.patterns si existe
        try:
            username = None
            if hasattr(self, 'player_usernames'):
                username = self.player_usernames.get(self.jugador_actual)
            if not username:
                username = getattr(self.manager, 'current_player', None)
            if username and username in getattr(self.manager, 'patterns', {}):
                patrones = self.manager.patterns[username]
                nuevo_patron = patrones.get(self.nivel, None)
                if nuevo_patron is not None:
                    self.tipo_patron = nuevo_patron
        except Exception:
            pass

        # === CARGAR MÚSICA DEL NIVEL ===
        try:
            music_loaded = False
            user_music_map = getattr(self.manager, 'player_music', {})
            music_pref = None
            if user_music_map and username:
                music_pref = user_music_map.get(username, {}).get(self.nivel)
            if music_pref:
                from assets.sound_manager import SoundManager
                music_loaded = SoundManager.cargar_musica("./resources/audio/", music_pref)
            if not music_loaded:
                default_music = f"game_music{self.nivel}.mp3"
                from assets.sound_manager import SoundManager
                SoundManager.cargar_musica("./resources/audio/", default_music)
        except Exception as e:
            print(f"[MUSIC] Error loading music for level {self.nivel}: {e}")

        # Reiniciar estado de enemigo/bonus para el nuevo nivel
        self.bonus_usados_nivel.clear()
        self.ultimo_bonus_tiempo = time.time()

        # Recrear la formación de enemigos
        self.enemigos.clear()
        self.crear_formacion_enemigos()

        # Asegurar que no queden disparos en pantalla al comenzar el nuevo nivel
        try:
            self.disparos_enemigos.clear()
            self.disparos.clear()
        except Exception:
            pass

        # Cerrar popup y reanudar
        self.popup_active = False
        self.game_paused = False

        # Reiniciar posición del jugador activo
        self.jugador.x = Level.ANCHO // 2 - self.jugador.tamaño // 2
        self.jugador.y = Level.ALTO - 100

        # Restaurar el comportamiento del popup_button (por si se reutiliza)
        self.popup_button.on_click = self.cambiar_turno
        self.popup_button.update_text("Continue")
        try:
            self.popup_button.text_surf = self.popup_font.render(self.popup_button.text, True, (255,255,255))
        except Exception:
            pass
        # Reanudar música al iniciar siguiente nivel
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass

    def finish_playthrough(self):
        """Finaliza la playthrough y regresa a la pantalla de opciones."""
        # Cerrar popup y reanudar (no seguimos con nuevos niveles)
        self.popup_active = False
        self.game_paused = False

        # Detener la música al finalizar la playthrough
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        # Intentar enviar resultados al estado END_GAME y cambiar a esa pantalla
        try:
            players_data = self._build_players_data()
            if hasattr(self, 'manager') and 'END_GAME' in getattr(self.manager, 'states', {}):
                try:
                    # Pasar resultados al EndGameScreen y cambiar de estado
                    try:
                        self.manager.states["END_GAME"].set_results(players_data)
                    except Exception:
                        pass
                    try:
                        self.manager.change_state("END_GAME")
                        return
                    except Exception:
                        # fallback a asignar current_state si change_state falla
                        if hasattr(self.manager, 'states') and 'END_GAME' in self.manager.states:
                            self.manager.current_state = self.manager.states['END_GAME']
                            return
                except Exception:
                    pass
        except Exception:
            pass

        # Fallback: volver a Options si no existe END_GAME o no se pudo cambiar
        try:
            self.manager.change_state("OPTIONS")
        except Exception:
            # Fallback: intentar acceder directamente
            if hasattr(self.manager, 'states') and 'OPTIONS' in self.manager.states:
                self.manager.current_state = self.manager.states['OPTIONS']
        finally:
            # Desbloquear popup por si la instancia se reutiliza
            try:
                self.popup_locked = False
            except Exception:
                pass

    def crear_formacion_enemigos(self):
        self.enemigos.clear()
        # Seleccionar imagen según el nivel actual
        try:
            img_name = "enemigo.png"
            if getattr(self, 'nivel', 1) == 2:
                img_name = "enemigo2.png"
            elif getattr(self, 'nivel', 1) == 3:
                img_name = "enemigo3.png"
            ruta_img = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "imgs", img_name)
            ruta_img = os.path.abspath(ruta_img)
        except Exception:
            ruta_img = None

        for fila in range(self.filas):
            enemigos_en_fila = self.filas - fila
            for col in range(enemigos_en_fila):
                x = Level.ANCHO//2 - (enemigos_en_fila * self.espacio_x)//2 + col * self.espacio_x
                y = -400 + fila * self.espacio_y
                # Pasar la ruta de la imagen al crear cada enemigo
                if ruta_img:
                    self.enemigos.append(Enemigo(x, y, self.manager.screen, image_path=ruta_img))
                else:
                    self.enemigos.append(Enemigo(x, y, self.manager.screen))

    def restart_level(self, clear_active_bonuses: bool = False):
        """Reinicia el estado del nivel actual (enemigos, disparos y bonus)
        Mantiene los atributos del jugador (puntos, vidas, bonus_teclas).
        
        """
        # Recrear enemigos a su formación inicial
        self.enemigos.clear()
        self.crear_formacion_enemigos()

        # Limpiar disparos en pantalla
        self.disparos.clear()
        # Limpiar también los disparos de enemigos para evitar que queden balas
        # del intento anterior cuando se reinicia por pérdida de vida / cambio de turno.
        try:
            self.disparos_enemigos.clear()
        except Exception:
            pass

        # Si se solicita, desactivar los bonuses activos del jugador (no las
        # disponibilidades), por ejemplo: doble_puntos, escudo y tipo_disparo activo.
        if clear_active_bonuses:
            try:
                # Doble puntos
                if getattr(self.jugador, 'doble_puntos', False):
                    self.jugador.doble_puntos = False
                    self.jugador.doble_puntos_fin = 0
                # Escudo
                if getattr(self.jugador, 'escudo', 0) > 0:
                    self.jugador.escudo = 0
                # Tipo de disparo activo (area / rastreador) -> volver a normal
                try:
                    if getattr(self.jugador, 'tipo_disparo', None) in ('area', 'rastreador'):
                        self.jugador.tipo_disparo = 'normal'
                except Exception:
                    pass
            except Exception:
                pass

        # Reiniciar bonus en escenario
        self.bonus_actual = None
        self.bonus_usados_nivel.clear()
        self.ultimo_bonus_tiempo = time.time()
        self.siguiente_bonus = random.randint(10, 20)

        # Opcional: resetear scroll de fondo para que el nivel parezca reiniciado
        try:
            self.fondo_y = 0
        except Exception:
            pass
        # Asegurar que los enemigos y patrón correspondan al nivel del jugador actual
        try:
            # Ajustar tipo_patron según el jugador actual y su nivel
            username = None
            if hasattr(self, 'player_usernames'):
                username = self.player_usernames.get(self.jugador_actual)
            if not username:
                username = getattr(self.manager, 'current_player', None)
            nivel_j = self.jugadores_data.get(self.jugador_actual, {}).get('nivel', self.nivel)
            self.nivel = nivel_j
            if username and username in getattr(self.manager, 'patterns', {}):
                patrones = self.manager.patterns[username]
                patron = patrones.get(self.nivel, None)
                if patron is not None:
                    self.tipo_patron = patron
        except Exception:
            pass

        # === CARGAR MÚSICA DEL NIVEL ===
        try:
            music_loaded = False
            user_music_map = getattr(self.manager, 'player_music', {})
            music_pref = None
            if user_music_map and username:
                music_pref = user_music_map.get(username, {}).get(self.nivel)
            if music_pref:
                from assets.sound_manager import SoundManager
                music_loaded = SoundManager.cargar_musica("./resources/audio/", music_pref)
            if not music_loaded:
                default_music = f"game_music{self.nivel}.mp3"
                from assets.sound_manager import SoundManager
                SoundManager.cargar_musica("./resources/audio/", default_music)
        except Exception as e:
            print(f"[MUSIC] Error loading music for level {self.nivel}: {e}")

    def handle_events(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # === MANEJO DE EVENTOS DEL POPUP ===
            if self.popup_active:
                self.popup_button.handle_event(evento)
                continue #return  # No procesar otros eventos mientras el popup está activo
            
            # === EVENTOS NORMALES DEL JUEGO ===
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:
                    self.pausado = not self.pausado
                    return   # Evita procesar movimiento/disparos durante este frame

                if self.pausado: return

                if(self.joystick is None):
                    if evento.key == pygame.K_SPACE:
                        self.jugador.disparar(self.disparos)
                    if pygame.K_1 <= evento.key <= pygame.K_5:
                        self.jugador.usar_bonus(evento.key - pygame.K_1 + 1)

                if evento.key == pygame.K_j:
                    volumen_actual = pygame.mixer.music.get_volume()
                    nuevo_volumen = max(0.0, volumen_actual - 0.1)
                    pygame.mixer.music.set_volume(nuevo_volumen)
                    print(f" Volumen bajado a: {nuevo_volumen:.1f}")
                elif evento.key == pygame.K_k:
                    volumen_actual = pygame.mixer.music.get_volume()
                    nuevo_volumen = min(1.0, volumen_actual + 0.1)
                    pygame.mixer.music.set_volume(nuevo_volumen)
                    print(f" Volumen subido a: {nuevo_volumen:.1f}")

            # Botón de ayuda
            self.help_button.handle_event(evento)

        if(self.joystick is None):

            if self.pausado: return
            teclas = pygame.key.get_pressed()
            self.jugador.mover(teclas)
        else:
            tiempo_actual = pygame.time.get_ticks()

            if self.joystick.get_button(9) and (tiempo_actual - self.tiempo_ultimo_boton > self.cooldown_disparo): # L1
                self.pausado = not self.pausado
                self.tiempo_ultimo_boton = tiempo_actual

            if self.pausado: return


            # Leer el joystick izquierdo para movimiento
            eje_x = self.joystick.get_axis(0)  # Eje horizontal izquierdo
            eje_y = self.joystick.get_axis(1)  # Eje vertical izquierdo

            # Zona muerta para evitar drift
            if abs(eje_x) < 0.1:
                eje_x = 0
            if abs(eje_y) < 0.1:
                eje_y = 0

            # Crear un diccionario simulando teclas
            teclas_virtuales = {
                pygame.K_LEFT:  eje_x < -0.2,
                pygame.K_a:     eje_x < -0.2,

                pygame.K_RIGHT: eje_x > 0.2,
                pygame.K_d:     eje_x > 0.2,

                pygame.K_UP:    eje_y < -0.2,
                pygame.K_w:     eje_y < -0.2,

                pygame.K_DOWN:  eje_y > 0.2,
                pygame.K_s:     eje_y > 0.2,
            }

            # Mover jugador
            self.jugador.mover(teclas_virtuales)

            # Disparar 
            if self.joystick.get_button(0):
                if tiempo_actual - self.tiempo_ultimo_disparo > self.cooldown_disparo:
                    self.jugador.disparar(self.disparos)
                    self.tiempo_ultimo_disparo = tiempo_actual

            #Bonus
            # Obtener bonus activos
            bonus_activos = [i for i in range(1, 6) if self.jugador.bonus_teclas[i]]

            # Si no hay bonus activos -> no hay selección
            if not bonus_activos:
                self.bonus_num = 0

            else:
                # Si la selección actual ya no existe, seleccionar el primero
                if self.bonus_num not in bonus_activos:
                    self.bonus_num = bonus_activos[0]

                # Índice dentro de la lista de activos
                idx = bonus_activos.index(self.bonus_num)

                # Navegar entre bonus activos
                if self.joystick.get_button(4) and (tiempo_actual - self.tiempo_ultimo_boton > self.cooldown_disparo): # L1
                    idx = (idx - 1) % len(bonus_activos)  # circular
                    self.bonus_num = bonus_activos[idx]
                    self.tiempo_ultimo_boton = tiempo_actual

                if self.joystick.get_button(5) and (tiempo_actual - self.tiempo_ultimo_boton > self.cooldown_disparo): # R1
                    idx = (idx + 1) % len(bonus_activos)  # circular
                    self.bonus_num = bonus_activos[idx]
                    self.tiempo_ultimo_boton = tiempo_actual

            if self.joystick.get_button(1) and self.bonus_num > 0:
                self.jugador.usar_bonus(self.bonus_num)




    def update(self, dt):
        if self.pausado:
            return  # No actualizar nada mientras está en pausa
            
        # Si el popup está activo, no actualizar el juego
        if self.popup_active or self.game_paused:
            return

        # Verificar si el jugador perdió todas sus vidas
        if self.jugador.vida <= 0:
            # Guardar estado del jugador que murió
            self.guardar_estado_jugador(self.jugador_actual)
            # Marcar jugador actual como finalizado si se quedó sin vidas
            try:
                if self.jugador_actual in self.jugadores_data:
                    self.jugadores_data[self.jugador_actual]['finished'] = True
            except Exception:
                pass

            # Si TODOS los jugadores no tienen vidas -> enviar resultados y cambiar a END_GAME
            try:
                # Considerar sólo los slots activos (1..total_jugadores)
                total = getattr(self, 'total_jugadores', 1)
                active_players = [data for idx, data in self.jugadores_data.items() if idx <= total]
                if all(data.get("vidas", 0) <= 0 for data in active_players):
                     players_data = self._build_players_data()
                     try:
                         if hasattr(self, 'manager') and 'END_GAME' in getattr(self.manager, 'states', {}):
                             self.manager.states["END_GAME"].set_results(players_data)
                     except Exception:
                         pass
                     try:
                         self.manager.change_state("END_GAME")
                         return
                     except Exception:
                         pass
                else:
                    # Mostrar popup de cambio de turno (muerte individual)
                    self.show_player_lost_popup()
                    return
            except Exception:
                # En caso de cualquier error, intentar mostrar popup de cambio de turno
                try:
                    self.show_player_lost_popup()
                except Exception:
                    pass
                return

        self.jugador.actualizar_bonus()
        self.mover_enemigos(self.tipo_patron, dt)

        # === DISPAROS DE ENEMIGOS ===
        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.ultimo_disparo_enemigo >= self.frecuencia_disparo:
            self.ultimo_disparo_enemigo = tiempo_actual

            # Mantener solo enemigos vivos
            self.enemies_to_shoot = [e for e in self.enemies_to_shoot if e.vivo]

            # Reiniciar el ciclo si todos ya dispararon
            if not self.enemies_to_shoot:
                self.enemies_to_shoot = [e for e in self.enemigos if e.vivo]
                random.shuffle(self.enemies_to_shoot)

            if self.enemies_to_shoot:
                enemigo = self.enemies_to_shoot.pop(0)

                # Verificar si ya existe un disparo cargado activo
                hay_disparo_cargado_en_pantalla = any(
                    d.tipo == "cargado" and d.activo for d in self.disparos_enemigos
                )

                # Seleccionar tipo de disparo
                if not hay_disparo_cargado_en_pantalla and not enemigo.ya_disparo_cargado:
                    tipo_disparo = "cargado"
                else:
                    tipo_disparo = "basico"

                # Determinar si se permite disparar (método del enemigo o fallback)
                allow_shoot = False
                try:
                    allow_shoot = bool(enemigo.puede_disparar())
                except Exception:
                    allow_shoot = True

                # Permitir disparos desde arriba de la pantalla siempre
                if getattr(enemigo, "y", 0) < 0:
                    allow_shoot = True

                if allow_shoot:
                    disparo = None
                    spawn_x = None
                    spawn_y = None
                    try:
                        if hasattr(enemigo, "rect"):
                            spawn_x = enemigo.rect.centerx
                            spawn_y = enemigo.rect.bottom
                        else:
                            ex = getattr(enemigo, "x", None)
                            ey = getattr(enemigo, "y", None)
                            w = getattr(enemigo, "width", None) or getattr(enemigo, "ancho", None) or getattr(enemigo, "tamaño", None)
                            h = getattr(enemigo, "height", None) or getattr(enemigo, "alto", None) or getattr(enemigo, "tamaño", None)
                            if ex is not None and ey is not None:
                                spawn_x = ex + (w / 2 if isinstance(w, (int, float)) else 0)
                                spawn_y = ey + (h if isinstance(h, (int, float)) else 0)
                    except Exception:
                        spawn_x = None
                        spawn_y = None

                    # Crear el disparo en la posición calculada o usar el método del enemigo como fallback
                    if spawn_x is not None and spawn_y is not None:
                        try:
                            disparo = DisparoEnemigo(spawn_x, spawn_y, tipo=tipo_disparo)
                        except Exception:
                            disparo = None

                    if disparo is None and hasattr(enemigo, "disparar"):
                        try:
                            disparo = enemigo.disparar(tipo_disparo)
                        except Exception:
                            disparo = None

                    if disparo:
                        self.disparos_enemigos.append(disparo)
                        # Marcar que el enemigo ya disparó cargado para evitar duplicados
                        if tipo_disparo == "cargado":
                            try:
                                enemigo.ya_disparo_cargado = True
                            except Exception:
                                pass

        # Disparos y colisiones
        for disparo in self.disparos[:]:
            if disparo.tipo == "rastreador":
                enemigos = self.enemigos
            else:
                enemigos = None
            disparo.mover(enemigos)
            
            if disparo.tipo == "area":
                if not disparo.impactado:
                    for enemigo in self.enemigos:
                        if enemigo.colisiona_con_disparo(disparo):
                            disparo.iniciar_explosion(radio=120, duracion=25)
                            break
                else:
                    for enemigo in self.enemigos:
                        if enemigo.vivo :
                            dx = (enemigo.x + enemigo.tamaño / 2) - disparo.x
                            dy = (enemigo.y + enemigo.tamaño / 2) - disparo.y
                            if math.hypot(dx, dy) <= disparo.explosion_radio:
                                SoundManager.play("enemigo_muere")
                                enemigo.vivo = False
                                self.explosiones.append({
                                    "x": enemigo.x,
                                    "y": enemigo.y,
                                    "start": time.time(),
                                    "dur": 0.2  # duración de la animación
                                })
                                self.jugador.puntos += 10 * (2 if self.jugador.doble_puntos else 1)
                    disparo.explosion_frames -= 1
                    if disparo.explosion_frames <= 0:
                        self.disparos.remove(disparo)
                        continue
            else:
                for enemigo in self.enemigos:
                    if enemigo.colisiona_con_disparo(disparo) and not disparo.impactado:
                        SoundManager.play("enemigo_muere")
                        enemigo.vivo = False
                        self.explosiones.append({
                            "x": enemigo.x,
                            "y": enemigo.y,
                            "start": time.time(),
                            "dur": 0.2  # duración de la animación
                        })
                        self.jugador.puntos += 200 * (2 if self.jugador.doble_puntos else 1)
                        disparo.impactado = True
                        break
                if disparo.impactado:
                    self.disparos.remove(disparo)
                    continue
            
            if disparo.y < -50 or disparo.y > Level.ALTO + 50:
                self.disparos.remove(disparo)

        # === Movimiento y colisión de disparos enemigos ===
        for disparo in self.disparos_enemigos[:]:
            disparo.mover()
            if disparo.y > Level.ALTO:
                try:
                    self.disparos_enemigos.remove(disparo)
                except ValueError:
                    pass
                continue

            if disparo.colisiona_con(self.jugador):
                # Aplicar daño/efecto según tipo de disparo, pero sólo mostrar popup si se perdió una vida
                vidas_antes = getattr(self.jugador, "vida", 0)
                try:
                    self.jugador.recibir_impacto_disparo(disparo.tipo)
                except Exception:
                    # Fallback: restar una vida si el método falla
                    try:
                        self.jugador.vida = max(0, vidas_antes - 1)
                    except Exception:
                        pass

                # Eliminar el disparo que impactó
                try:
                    self.disparos_enemigos.remove(disparo)
                except ValueError:
                    pass

                # Si la vida disminuyó, guardar estado y mostrar popup (o game over)
                try:
                    vidas_despues = getattr(self.jugador, "vida", 0)
                    if vidas_despues < vidas_antes:
                        # Guardar estado actual del jugador
                        self.guardar_estado_jugador(self.jugador_actual)
                        try:
                            if self.jugador_actual in self.jugadores_data:
                                self.jugadores_data[self.jugador_actual]['finished'] = (vidas_despues <= 0)
                        except Exception:
                            pass

                        total = getattr(self, 'total_jugadores', 1)
                        active_players = [data for idx, data in self.jugadores_data.items() if idx <= total]
                        if all(data.get("vidas", 0) <= 0 for data in active_players):
                            self.show_game_over_popup()
                        else:
                            self.show_player_lost_popup()
                    else:
                        # Impacto no redujo vida (p. ej. escudo/contador): no mostrar popup
                        pass
                except Exception:
                    pass

        # Colisión jugador-enemigo
        # === COLISIÓN JUGADOR-ENEMIGO (MODIFICADO) ===
        for enemigo in self.enemigos:
            if enemigo.vivo and enemigo.colisiona_con_jugador(self.jugador):
                # El enemigo siempre muere en la colisión
                enemigo.vivo = False
                SoundManager.play("enemigo_muere")

                # explosión para el enemigo (pequeña)
                self.explosiones.append({
                    "x": enemigo.x,
                    "y": enemigo.y,
                    "start": time.time(),
                    "dur": 0.25,
                    "kind": "enemy",
                    "base_radius": 20
                })

                # Si el jugador tiene escudo activo -> consumir UNA capa y NO morir
                try:
                    if getattr(self.jugador, 'tiene_escudo', False):
                        try:
                            # Reducir solo una capa de escudo
                            self.jugador.reducir_capas_escudo(1)
                        except Exception:
                            # Fallback directo
                            try:
                                self.jugador.escudo = max(0, getattr(self.jugador, 'escudo', 0) - 1)
                            except Exception:
                                pass
                        # Marcar que este enemigo fue destruido por el escudo para
                        # que no cuente como muerte que avance de nivel.
                        try:
                            enemigo.killed_by_shield = True
                        except Exception:
                            pass
                        # Suprimir cualquier popup inmediato (p. ej. pérdida de vida o level cleared)
                        try:
                            self.suppress_popup = True
                        except Exception:
                            pass
                        # No crear explosión del jugador ni restar vidas
                        break
                except Exception:
                    pass

                # Si NO tiene escudo -> ambos mueren (comportamiento anterior)
                # explosión para el jugador (más grande, más roja)
                self.explosiones.append({
                    "x": self.jugador.x + getattr(self.jugador, 'tamaño', 32) // 2,
                    "y": self.jugador.y + getattr(self.jugador, 'tamaño', 32) // 2,
                    "start": time.time(),
                    "dur": 0.6,
                    "kind": "player",
                    "base_radius": 40
                })

                # Vibración del joystick si aplica
                if(self.joystick is not None):
                    try:
                        self.joystick.rumble(0.7, 0.7, 500)  # vibración por 500ms
                    except Exception:
                        pass

                SoundManager.play("enemigo_muere")

                # El jugador recibe daño (pierde una vida)
                try:
                    self.jugador.recibir_daño()
                except Exception:
                    try:
                        self.jugador.vida = max(0, getattr(self.jugador, 'vida', 0) - 1)
                    except Exception:
                        pass

                # Si el jugador aún tiene vidas, mostrar popup
                if self.jugador.vida > 0:
                    self.show_player_lost_popup()
                else:
                    # Si perdió todas las vidas, guardar y verificar game over
                    self.guardar_estado_jugador(self.jugador_actual)
                    # Marcar jugador actual como finalizado si se quedó sin vidas
                    try:
                        if self.jugador_actual in self.jugadores_data:
                            self.jugadores_data[self.jugador_actual]['finished'] = True
                    except Exception:
                        pass
                    total = getattr(self, 'total_jugadores', 1)
                    active_players = [data for idx, data in self.jugadores_data.items() if idx <= total]
                    if all(data.get("vidas", 0) <= 0 for data in active_players):
                        # Mostrar popup de Game Over (todos los jugadores perdieron)
                        self.show_game_over_popup()
                    else:
                        self.show_player_lost_popup()

                break  # Solo una colisión por frame

        # BONUS
        if self.bonus_actual and self.bonus_actual.activo:
            self.bonus_actual.mover()
            if not self.bonus_actual.recogido:  #olo puede colisionar si no fue recogido
                if self.bonus_actual.colisiona_con(self.jugador):
                    self.jugador.asignar_bonus_tecla(self.bonus_actual.tipo)
                    SoundManager.play("bonus")
            else:
                if not self.bonus_actual.activo:
                    self.bonus_actual = None

        if time.time() - self.ultimo_bonus_tiempo >= self.siguiente_bonus and len(self.bonus_usados_nivel) < len(Bonus.TIPOS):
            tipo = random.choice([t for t in Bonus.TIPOS if t not in self.bonus_usados_nivel])
            self.bonus_actual = Bonus(tipo)
            self.bonus_usados_nivel.add(tipo)
            self.ultimo_bonus_tiempo = time.time()
            self.siguiente_bonus = random.randint(10, 20)

        # Nueva ronda: si todos los enemigos murieron, mostrar popup de nivel completado
        if all(not e.vivo for e in self.enemigos):
            # Do not auto-increment level here — show the popup and let
            # `next_level()` handle progression when the player confirms.
            self.show_level_cleared_popup()

        # Actualizar explosiones
        for ex in self.explosiones[:]:  # ← importante copiar la lista
            if time.time() - ex["start"] > ex["dur"]:
                self.explosiones.remove(ex)

    def draw(self, surface):
        # Dibujar fondo dos veces para scroll continuo
        surface.blit(self.fondo, (0, self.fondo_y))
        surface.blit(self.fondo, (0, self.fondo_y - self.fondo.get_height()))

        # Mover fondo (se detiene si el popup está activo)
        if not self.popup_active:
            self.fondo_y += self.fondo_vel
            if self.fondo_y >= self.fondo.get_height():
                self.fondo_y = 0

        # Actualizar nombres (si hubo mapping de usernames) y dibujar información jugadores
        try:
            self.update_userinfo_names()
        except Exception:
            pass

        # Mostrar puntajes en tiempo real desde las instancias de jugador
        self.user_1_info.update_info(score=self.jugadores_inst[1].puntos)
        self.user_1_info.draw(surface)

        if self.total_jugadores >= 2 and self.user_2_info is not None:
            self.user_2_info.update_info(score=self.jugadores_inst[2].puntos)
            self.user_2_info.draw(surface)

        # Indicador de turno actual (mostrar username si existe)
        turno_name = None
        if hasattr(self, 'player_usernames') and isinstance(self.player_usernames, dict):
            turno_name = self.player_usernames.get(self.jugador_actual)
        if not turno_name:
            turno_name = f"Player {self.jugador_actual}"
        turno_text = self.fuente.render(f"Turn: {turno_name}", True, Colors.BLANCO)
        surface.blit(turno_text, (Level.ANCHO // 2 - 160, 30))

        self.jugador.dibujar(surface)
        for enemigo in self.enemigos:
            enemigo.dibujar(surface)
        for disparo in self.disparos:
            disparo.dibujar(surface)
        for disparo in self.disparos_enemigos:
            disparo.dibujar(surface)
        if self.bonus_actual and self.bonus_actual.activo:
            self.bonus_actual.dibujar(surface)

        # Dibujar explosiones (usar 'kind' y 'base_radius' si están presentes)
        for ex in self.explosiones:
            progreso = (time.time() - ex["start"]) / ex["dur"]
            if progreso > 1:
                continue  # por si alguna no fue borrada aún

            alpha = int(255 * (1 - progreso))
            base = ex.get("base_radius", 20)
            radio = int(base * (1 + progreso))

            capa = pygame.Surface((radio*2, radio*2), pygame.SRCALPHA)
            kind = ex.get("kind", "enemy")
            if kind == "player":
                outer_color = (255, 220, 200, alpha)
                inner_color = (255, 40, 40, alpha)
            else:
                outer_color = (255,180,0,alpha)
                inner_color = (255,80,0,alpha)

            pygame.draw.circle(capa, outer_color, (radio,radio), radio)
            pygame.draw.circle(capa, inner_color, (radio,radio), max(1, radio//2))

            surface.blit(capa, (ex["x"] - radio, ex["y"] - radio))

        # === Indicador de vidas (parte inferior izquierda) ===
        # === Indicador de vidas ===
        base_x = 30
        base_y = Level.ALTO - 70
        separacion = 45
        tamaño_icono = 30

        total_ancho = separacion * max(self.jugador.vida, 3)
        fondo_rect = pygame.Rect(base_x - 15, base_y - 10, total_ancho + 20, tamaño_icono + 20)

        fondo = pygame.Surface((fondo_rect.width, fondo_rect.height), pygame.SRCALPHA)
        fondo.fill((20, 20, 20, 180))
        surface.blit(fondo, fondo_rect.topleft)
        pygame.draw.rect(surface, (200, 200, 200), fondo_rect, width=2, border_radius=12)

        for i in range(self.jugador.vida):
            if self.jugador.imagen:
                icono_vida = pygame.transform.scale(self.jugador.imagen, (tamaño_icono, tamaño_icono))
                x = base_x + i * separacion
                y = base_y
                surface.blit(icono_vida, (x, y))

        # === Barra de bonus ===
        barra_ancho = 320
        barra_alto = 70
        barra_x = Level.ANCHO - barra_ancho - 30
        barra_y = Level.ALTO - barra_alto - 30

        pygame.draw.rect(surface, (30, 30, 30), (barra_x, barra_y, barra_ancho, barra_alto), border_radius=10)
        pygame.draw.rect(surface, (200, 200, 200), (barra_x, barra_y, barra_ancho, barra_alto), 2, border_radius=10)

        base_x = barra_x + 25
        base_y = barra_y + 15
        separacion = 55

        t = time.time() - self.tiempo_inicio
        brillo = int((math.sin(t * 3) + 1) * 127)
        color_brillo = (brillo, brillo, 255)

        for i in range(1, 6):
            valor = self.jugador.bonus_teclas[i]
            activo = valor > 0 if isinstance(valor, (int, float)) else bool(valor)

            icono = self.iconos_bonus.get(i)
            if icono:
                icono_final = icono.copy()
                if not activo:
                    icono_final.fill((100, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)

                x_icono = base_x + (i - 1) * separacion
                y_icono = base_y
                surface.blit(icono_final, (x_icono, y_icono))

                # Marco para los activos (con brillo animado)
                if self.joystick is not None:
                    if activo and i == self.bonus_num:
                                pygame.draw.rect(
                                    surface,
                                    color_brillo,               # azul animado
                                    (x_icono - 2, y_icono - 2, 44, 44),
                                    2,
                                    border_radius=5
                                )
                    elif activo: 
                        pygame.draw.rect(
                            surface,
                            (200, 200, 255),            # un azul claro estático
                            (x_icono - 2, y_icono - 2, 44, 44),
                            2,
                            border_radius=5
                        )
                else:
                    if activo:
                        pygame.draw.rect(
                            surface,
                            color_brillo,
                            (x_icono - 2, y_icono - 2, 44, 44),
                            2,
                            border_radius=5
                        )
            else:
                # Mostrar número si no hay icono
                txt = self.fuente.render(str(i), True, Colors.BLANCO)
                surface.blit(txt, (base_x + (i - 1) * separacion + 15, base_y + 10))

        # Game Over
        if self.game_over:
            fin = self.fuente.render("GAME OVER", True, Colors.ROJO)
            surface.blit(fin, (Level.ANCHO//2 - 100, Level.ALTO//2))

        # Dibujar botón de ayuda
        self.help_button.draw(surface)

        # Dibujar mensaje de Pausa
        if self.pausado:
            texto = self.fuente.render("PAUSED", True, (255,255,255))
            surface.blit(texto, (Level.ANCHO//2 - 50, Level.ALTO//2))

        # === DIBUJAR POPUP ===
        if self.popup_active:
            self.draw_popup(surface)

    def draw_popup(self, surface):
        """Dibuja el popup de cambio de turno"""
        # Fondo semi-transparente
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Cuadro del popup
        pygame.draw.rect(surface, (40, 40, 60), self.popup_rect, border_radius=15)
        pygame.draw.rect(surface, (255, 100, 100), self.popup_rect, 4, border_radius=15)

        # Título y mensaje según el tipo de popup
        mensaje_font = pygame.font.Font(None, 32)
        if self.popup_type == 'level_cleared':
            title = self.popup_font.render("Level Cleared!", True, (255, 255, 255))
            surface.blit(title, (self.popup_rect.centerx - title.get_width() // 2, self.popup_rect.y + 40))

            # Intentar obtener el patrón siguiente para mostrarlo usando el nivel del jugador actual
            try:
                jugador_idx = self.jugador_actual
                nivel_j = self.jugadores_data.get(jugador_idx, {}).get('nivel', self.nivel)
                next_lvl = nivel_j + 1
                next_pattern = None
                username = None
                if hasattr(self, 'player_usernames'):
                    username = self.player_usernames.get(jugador_idx)
                if not username:
                    username = getattr(self.manager, 'current_player', None)
                if username and username in self.manager.patterns:
                    patrones = self.manager.patterns[username]
                    next_pattern = patrones.get(next_lvl, None)
                if next_pattern is None:
                    msg = f"Next level: Pattern {self.tipo_patron}"
                else:
                    msg = f"Next level: Pattern {next_pattern}"
            except Exception:
                msg = f"Next level: Pattern {self.tipo_patron}"

            texto1 = mensaje_font.render(msg, True, (100, 255, 100))
            surface.blit(texto1, (self.popup_rect.centerx - texto1.get_width() // 2, self.popup_rect.centery - 10))

        elif self.popup_type == 'game_over':
            # Game Over popup
            title = self.popup_font.render("GAME OVER", True, (255, 255, 255))
            surface.blit(title, (self.popup_rect.centerx - title.get_width() // 2, self.popup_rect.y + 40))
            texto1 = mensaje_font.render("All players have played.", True, (255, 100, 100))
            surface.blit(texto1, (self.popup_rect.centerx - texto1.get_width() // 2, self.popup_rect.centery - 10))

        else:
            # Default -> lost life popup
            title = self.popup_font.render(f"Player {self.jugador_actual} Lost!", True, (255, 255, 255))
            surface.blit(title, (self.popup_rect.centerx - title.get_width() // 2, self.popup_rect.y + 40))

            vidas_restantes = self.jugador.vida
            if vidas_restantes > 0:
                msg = f"Lives remaining: {vidas_restantes}"
                msg2 = f"Next turn: Player {2 if self.jugador_actual == 1 else 1}"
            else:
                otro_jugador = 2 if self.jugador_actual == 1 else 1
                msg = "All lives lost!"
                msg2 = f"Player {otro_jugador}'s turn"

            texto1 = mensaje_font.render(msg, True, (255, 255, 255))
            texto2 = mensaje_font.render(msg2, True, (100, 255, 100))
            surface.blit(texto1, (self.popup_rect.centerx - texto1.get_width() // 2, self.popup_rect.centery - 30))
            surface.blit(texto2, (self.popup_rect.centerx - texto2.get_width() // 2, self.popup_rect.centery + 10))

        # Botón OK
        self.popup_button.draw(surface)

    def mover_enemigos(self, tipo_patron, dt):
        vivos = [e for e in self.enemigos if e.vivo]
        if not vivos:
            return
        
        if tipo_patron == 1:
            max_x = max(e.x for e in vivos) + 40
            min_x = min(e.x for e in vivos)
            if max_x >= Level.ANCHO - 10:
                self.direccion_x = -1
                for e in self.enemigos:
                    e.mover(0, self.vel_y * 3)
            elif min_x <= 10:
                self.direccion_x = 1
                for e in self.enemigos:
                    e.mover(0, self.vel_y * 3)
            for e in self.enemigos:
                e.mover(self.vel_x * self.direccion_x * 5, 0)

        elif tipo_patron == 2:
            for e in self.enemigos:
                direccion_y = self.vel_y/3 if (e.x // 50) % 2 == 0 else -self.vel_y/6
                e.mover(self.vel_x * self.direccion_x, direccion_y)

            max_x = max(e.x for e in vivos) + 40
            min_x = min(e.x for e in vivos)
            if max_x >= Level.ANCHO - 10 or min_x <= 10:
                self.direccion_x *= -1

        elif tipo_patron == 3:
            delta_y = self.vel_y / 12
            max_x = max(e.x for e in vivos) + 40
            min_x = min(e.x for e in vivos)

            if max_x >= Level.ANCHO - 10 or min_x <= 10:
                self.direccion_x *= -1
            for e in self.enemigos:
                e.mover(self.direccion_x * 3 * math.sin(e.y / 100), delta_y)

        elif tipo_patron == 4:
            for e in self.enemigos:
                e.mover(self.vel_x * self.direccion_x, 0)
            
            if pygame.time.get_ticks() % 2000 < 50:
                self.direccion_x *= -1
                for e in self.enemigos:
                    e.mover(0, self.vel_y)

        elif tipo_patron == 5:
            for e in self.enemigos:
                if e.x > Level.ANCHO:
                    e.x = 0
                elif e.x < 0:
                    e.x = Level.ANCHO
                dx = random.randint(-self.vel_x* 8, self.vel_x* 8)
                dy = random.randint(0, self.vel_y)
                e.mover(dx, dy)
        else:
            self.mover_enemigos(1, dt)

    def _build_players_data(self):
        """Construye lista de jugadores para enviar a END_GAME de forma segura."""
        players_data = []
        total = getattr(self, 'total_jugadores', 1)
        for idx in range(1, total + 1):
            try:
                user_info = getattr(self, f"user_{idx}_info", None)
                name = getattr(user_info, "name", f"Player {idx}") if user_info else f"Player {idx}"
                photo = getattr(user_info, "photo_path", getattr(user_info, "photo", "")) if user_info else ""
                score = getattr(self.jugadores_inst.get(idx), "puntos", 0) if isinstance(self.jugadores_inst, dict) else (getattr(self.jugador, "puntos", 0) if idx == self.jugador_actual else 0)
                players_data.append({"name": name, "photo": photo, "score": score})
            except Exception:
                players_data.append({"name": f"Player {idx}", "photo": "", "score": 0})
 
        return players_data