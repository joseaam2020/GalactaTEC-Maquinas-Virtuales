import pygame
import time
import random
import sys
import math
import os
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

    def crear_formacion_enemigos(self):
        self.enemigos.clear()
        for fila in range(self.filas):
            enemigos_en_fila = self.filas - fila
            for col in range(enemigos_en_fila):
                x = Level.ANCHO//2 - (enemigos_en_fila * self.espacio_x)//2 + col * self.espacio_x
                y = -50 + fila * self.espacio_y
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

        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas)

    def update(self, dt):
        if self.jugador.vida <= 0:
            self.game_over = True
            return

        self.jugador.actualizar_bonus()

        # Mover enemigos
        vivos = [e for e in self.enemigos if e.vivo]
        if vivos:
            max_x = max(e.x for e in vivos) + 40
            min_x = min(e.x for e in vivos)
            if max_x >= Level.ANCHO - 10:
                self.direccion_x = -1
                for e in self.enemigos:
                    e.mover(0, self.vel_y)
            elif min_x <= 10:
                self.direccion_x = 1
                for e in self.enemigos:
                    e.mover(0, self.vel_y)
            for e in self.enemigos:
                e.mover(self.vel_x * self.direccion_x, 0)

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
                                self.jugador.puntos += 200 * (2 if self.jugador.doble_puntos else 1)
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


        self.jugador.dibujar(surface)
        for enemigo in self.enemigos:
            enemigo.dibujar(surface)
        for disparo in self.disparos:
            disparo.dibujar(surface)
        if self.bonus_actual and self.bonus_actual.activo:
            self.bonus_actual.dibujar(surface)

        # HUD
        hud_texto = f"Nivel: {self.nivel}   Vida: {self.jugador.vida}   Puntos: {self.jugador.puntos}"
        hud = self.fuente.render(hud_texto, True, Colors.BLANCO)
        texto_rect = hud.get_rect(bottomright=(Level.ANCHO - 40, Level.ALTO - 130))

        # Panel del HUD
        panel_ancho = 380
        panel_alto = 140
        panel_x = Level.ANCHO - panel_ancho - 20
        panel_y = Level.ALTO - panel_alto - 20

        # Dibujar fondo del panel
        pygame.draw.rect(surface, (25, 25, 25), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=12)
        # Borde blanco suave
        pygame.draw.rect(surface, (200, 200, 200), (panel_x, panel_y, panel_ancho, panel_alto), width=2, border_radius=12)

        # Dibujar texto principal (nivel, vida, puntos)
        surface.blit(hud, texto_rect)

        # === Inventario de bonus con íconos ===
        base_x = panel_x + 30
        base_y = panel_y + 60
        separacion = 60

        for i in range(1, 6):
            valor = self.jugador.bonus_teclas[i]
            activo = valor > 0 if isinstance(valor, (int, float)) else bool(valor)

            # Marco del icono
            marco_color = (200, 200, 200) if activo else (100, 100, 100)
            pygame.draw.rect(surface, marco_color, (base_x + (i - 1) * separacion, base_y, 44, 44), border_radius=6)

            icono = self.iconos_bonus.get(i)
            if icono:
                # Si el bonus no está activo → versión en escala de grises
                if not activo:
                    icono_gris = pygame.transform.average_color(icono)
                    # Crear superficie gris con alpha
                    icono_descolorado = icono.copy()
                    arr = pygame.surfarray.pixels3d(icono_descolorado)
                    gris = sum(icono_gris[:3]) // 3
                    arr[:, :, :] = gris
                    del arr  # liberar bloqueo de memoria de surfarray
                    surface.blit(icono_descolorado, (base_x + (i - 1) * separacion, base_y))
                else:
                    surface.blit(icono, (base_x + (i - 1) * separacion, base_y))
            else:
                # Mostrar número si no hay icono
                txt = self.fuente.render(str(i), True, Colors.BLANCO)
                surface.blit(txt, (base_x + (i - 1) * separacion + 14, base_y + 10))

        # Game Over
        if self.game_over:
            fin = self.fuente.render("GAME OVER", True, Colors.ROJO)
            surface.blit(fin, (Level.ANCHO//2 - 100, Level.ALTO//2))
