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
from assets.sound_manager import SoundManager

class Level:
    ANCHO, ALTO = 1280, 720
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Juego Space Invaders con Bonus y Disparos")
    clock = pygame.time.Clock()

    def __init__(self, manager):
        self.fuente = pygame.font.Font(None, 28)
        self.manager = manager  # Referencia al StateManager
        self.jugador = Jugador(manager.screen)
        self.disparos = []
        self.bonus_actual = None
        self.bonus_usados_nivel = set()
        self.ultimo_bonus_tiempo = time.time()
        self.siguiente_bonus = random.randint(3, 4)
        self.nivel = 1
        self.tipo_patron = 1

        # Control de animación del brillo de bonus activos
        self.tiempo_inicio = time.time()

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
        self.filas = 6
        self.crear_formacion_enemigos()

        self.direccion_x = 1
        self.vel_x = 2
        self.vel_y = 20

        self.game_over = False

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
                print(f"⚠️ No se encontró el icono de bonus: {ruta_icono}")
                self.iconos_bonus[tecla] = None

        # Informacion jugadores
        self.user_1_info = UserInfo(
                font=self.fuente,
                pos=(20, 20),
                size=(100, 100),
                name="",
                photo="./resources/imgs/disponible.png"
            )

        self.user_2_info = UserInfo(
                font=self.fuente,
                pos=(Level.ANCHO - 120, 20),
                size=(100, 100),
                name="",
                photo="./resources/imgs/disponible.png"
        )


        help_text = (
            "Welcome to GalactaTEC!\n\n"
            "Your goal is to destroy all enemy waves before they reach you or drain your lives.\n\n"
            "- Move Left/Right: Use the arrow keys to move your ship horizontally.\n\n"
            "- Shoot: Press SPACE to fire at incoming enemies.\n\n"
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


    def crear_formacion_enemigos(self):
        self.enemigos.clear()
        for fila in range(self.filas):
            enemigos_en_fila = self.filas - fila
            for col in range(enemigos_en_fila):
                x = Level.ANCHO//2 - (enemigos_en_fila * self.espacio_x)//2 + col * self.espacio_x
                y = -200 + fila * self.espacio_y
                self.enemigos.append(Enemigo(x, y,self.manager.screen))

    def handle_events(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    self.jugador.disparar(self.disparos)
                if pygame.K_1 <= evento.key <= pygame.K_5:
                    self.jugador.usar_bonus(evento.key - pygame.K_1 + 1)

                if evento.key == pygame.K_j:
                    # Bajar volumen (mínimo 0.0)
                    volumen_actual = pygame.mixer.music.get_volume()
                    nuevo_volumen = max(0.0, volumen_actual - 0.1)
                    pygame.mixer.music.set_volume(nuevo_volumen)
                    print(f" Volumen bajado a: {nuevo_volumen:.1f}")
                elif evento.key == pygame.K_k:
                    # Subir volumen (máximo 1.0)
                    volumen_actual = pygame.mixer.music.get_volume()
                    nuevo_volumen = min(1.0, volumen_actual + 0.1)
                    pygame.mixer.music.set_volume(nuevo_volumen)
                    print(f" Volumen subido a: {nuevo_volumen:.1f}")

            # Botón de ayuda
            self.help_button.handle_event(evento)

        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas)


    def update(self, dt):
        if self.jugador.vida <= 0:
            self.game_over = True
            return

        self.jugador.actualizar_bonus()

        self.mover_enemigos(self.tipo_patron,dt)

        # Disparos y colisiones
        for disparo in self.disparos[:]:
            disparo.mover()
            if disparo.tipo == "area":
                if not disparo.impactado:
                    for enemigo in self.enemigos:
                        if enemigo.colisiona_con_disparo(disparo):
                            disparo.iniciar_explosion(radio=120, duracion=25)
                            break
                else:
                    for enemigo in self.enemigos:
                        if enemigo.vivo:
                            dx = (enemigo.x + enemigo.tamaño / 2) - disparo.x
                            dy = (enemigo.y + enemigo.tamaño / 2) - disparo.y
                            if math.hypot(dx, dy) <= disparo.explosion_radio:
                                SoundManager.play("enemigo_muere")
                                enemigo.vivo = False
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
                        self.jugador.puntos += 10 * (2 if self.jugador.doble_puntos else 1)
                        disparo.impactado = True
                        break
                if disparo.impactado:
                    self.disparos.remove(disparo)
                    continue
            if disparo.y < -50 or disparo.y > Level.ALTO + 50:
                self.disparos.remove(disparo)

        # Colisión jugador-enemigo
        for enemigo in self.enemigos:
            if enemigo.vivo and enemigo.colisiona_con_jugador(self.jugador):
                self.jugador.recibir_daño()
                SoundManager.play("enemigo_muere")
                enemigo.vivo = False

        # BONUS
        if self.bonus_actual and self.bonus_actual.activo:
            self.bonus_actual.mover()
            if not self.bonus_actual.recogido:  # 💡 solo puede colisionar si no fue recogido
                if self.bonus_actual.colisiona_con(self.jugador):
                    self.jugador.asignar_bonus_tecla(self.bonus_actual.tipo)
                    SoundManager.play("bonus")
            else:
                # Si ya fue recogido, dejamos que termine su animación
                if not self.bonus_actual.activo:
                    self.bonus_actual = None

        if time.time() - self.ultimo_bonus_tiempo >= self.siguiente_bonus and len(self.bonus_usados_nivel) < len(Bonus.TIPOS):
            tipo = random.choice([t for t in Bonus.TIPOS if t not in self.bonus_usados_nivel])
            self.bonus_actual = Bonus(tipo)
            self.bonus_usados_nivel.add(tipo)
            self.ultimo_bonus_tiempo = time.time()
            self.siguiente_bonus = random.randint(10, 20)

        # Nueva ronda
        if all(not e.vivo for e in self.enemigos):
            self.nivel += 1
            self.puntos_para_siguiente_nivel += 200
            self.bonus_usados_nivel.clear()
            for e in self.enemigos:
                e.reiniciar()

    def draw(self, surface):

        # Dibujar fondo dos veces para scroll continuo
        surface.blit(self.fondo, (0, self.fondo_y))
        surface.blit(self.fondo, (0, self.fondo_y - self.fondo.get_height()))

        # Mover fondo
        self.fondo_y += self.fondo_vel
        if self.fondo_y >= self.fondo.get_height():
            self.fondo_y = 0

        #Dibujar informacion jugadores
        self.user_1_info.update_info(score=self.jugador.puntos)
        self.user_1_info.draw(surface)

        # Si hay un segundo jugador, también se muestra
        if self.user_2_info:
            self.user_2_info.draw(surface)


        self.jugador.dibujar(surface)
        for enemigo in self.enemigos:
            enemigo.dibujar(surface)
        for disparo in self.disparos:
            disparo.dibujar(surface)
        if self.bonus_actual and self.bonus_actual.activo:
            self.bonus_actual.dibujar(surface)


        # === Indicador de vidas (parte inferior izquierda) ===
        base_x = 30
        base_y = Level.ALTO - 70
        separacion = 45
        tamaño_icono = 30

        # --- Fondo del panel de vidas ---
        total_ancho = separacion * max(self.jugador.vida, 3)
        fondo_rect = pygame.Rect(base_x - 15, base_y - 10, total_ancho + 20, tamaño_icono + 20)

        # Fondo oscuro semitransparente
        fondo = pygame.Surface((fondo_rect.width, fondo_rect.height), pygame.SRCALPHA)
        fondo.fill((20, 20, 20, 180))  # RGBA → 180 = transparencia
        surface.blit(fondo, fondo_rect.topleft)

        # Borde del panel
        pygame.draw.rect(surface, (200, 200, 200), fondo_rect, width=2, border_radius=12)

        # --- Dibujar los íconos de vida ---
        for i in range(self.jugador.vida):
            if self.jugador.imagen:
                icono_vida = pygame.transform.scale(self.jugador.imagen, (tamaño_icono, tamaño_icono))
                x = base_x + i * separacion
                y = base_y
                surface.blit(icono_vida, (x, y))

        # === Barra de bonus (parte inferior derecha) ===
        barra_ancho = 320
        barra_alto = 70
        barra_x = Level.ANCHO - barra_ancho - 30
        barra_y = Level.ALTO - barra_alto - 30

        # Fondo de la barra
        pygame.draw.rect(surface, (30, 30, 30), (barra_x, barra_y, barra_ancho, barra_alto), border_radius=10)
        pygame.draw.rect(surface, (200, 200, 200), (barra_x, barra_y, barra_ancho, barra_alto), 2, border_radius=10)

        # Posición inicial de los íconos
        base_x = barra_x + 25
        base_y = barra_y + 15
        separacion = 55

        # Calcular intensidad del brillo (parpadeo suave)
        t = time.time() - self.tiempo_inicio
        brillo = int((math.sin(t * 3) + 1) * 127)  # rango 0–254
        color_brillo = (brillo, brillo, 255)  # azul brillante parpadeante

        for i in range(1, 6):
            valor = self.jugador.bonus_teclas[i]
            activo = valor > 0 if isinstance(valor, (int, float)) else bool(valor)

            icono = self.iconos_bonus.get(i)
            if icono:
                icono_final = icono.copy()

                if not activo:
                    # Convertir icono a gris uniforme manteniendo transparencia
                    icono_final.fill((100, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)

                # Dibujar icono
                x_icono = base_x + (i - 1) * separacion
                y_icono = base_y
                surface.blit(icono_final, (x_icono, y_icono))

                # Marco para los activos (con brillo animado)
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


    def mover_enemigos(self, tipo_patron,dt):
        vivos = [e for e in self.enemigos if e.vivo]
        if not vivos:
            return
        
        if tipo_patron == 1:
            # Movimiento clásico: van a un lado y bajan cuando tocan bordes
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
            # Movimiento zigzag vertical + horizontal
            for e in self.enemigos:
                # Alternar dirección vertical para cada enemigo según fila o id
                direccion_y = self.vel_y/3 if (e.x // 50) % 2 == 0 else -self.vel_y/6
                e.mover(self.vel_x * self.direccion_x, direccion_y)

            # Invertir dirección horizontal al tocar bordes
            max_x = max(e.x for e in vivos) + 40
            min_x = min(e.x for e in vivos)
            if max_x >= Level.ANCHO - 10 or min_x <= 10:
                self.direccion_x *= -1

        elif tipo_patron == 3:
            # Bajada constante en Y
            delta_y = self.vel_y / 12  # movimiento vertical lento
            
            # Invertir dirección horizontal al tocar bordes
            max_x = max(e.x for e in vivos) + 40
            min_x = min(e.x for e in vivos)

            if max_x >= Level.ANCHO - 10 or min_x <= 10:
                self.direccion_x *= -1
            for e in self.enemigos:
                # Calculamos cuánto mover en X: diferencia entre base_x y la posición actual del enemigo
                
                # Movemos horizontal y verticalmente
                e.mover(self.direccion_x * 3 * math.sin(e.y / 100), delta_y)

        elif tipo_patron == 4:
            # Movimiento oscilante horizontal con bajada periódica
            for e in self.enemigos:
                e.mover(self.vel_x * self.direccion_x, 0)
            
            # Bajar y cambiar dirección cada cierto tiempo
            if pygame.time.get_ticks() % 2000 < 50:
                self.direccion_x *= -1
                for e in self.enemigos:
                    e.mover(0, self.vel_y)

        elif tipo_patron == 5:
            # Movimiento aleatorio controlado
            for e in self.enemigos:
          # Si sale por la derecha, reaparece por la izquierda
                if e.x > Level.ANCHO:
                    e.x = 0
            
                # Si sale por la izquierda, reaparece por la derecha
                elif e.x < 0:
                    e.x = Level.ANCHO
                dx = random.randint(-self.vel_x* 8, self.vel_x* 8)
                dy = random.randint(0, self.vel_y)
                e.mover(dx, dy)

        else:
            # Patrón por defecto: mismo que 1
            self.mover_enemigos(1,dt)
