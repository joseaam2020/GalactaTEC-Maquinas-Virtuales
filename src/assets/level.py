import pygame
import time
import random
import sys
import math
from assets.player import Jugador
from assets.enemy import Enemigo
from assets.bonus import Bonus
from assets.colors import Colors
from assets.sound_manager import SoundManager

class Level:
    ANCHO, ALTO = 800, 600
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
        self.puntos_para_siguiente_nivel = 200

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
            if self.bonus_actual.colisiona_con(self.jugador):
                self.jugador.asignar_bonus_tecla(self.bonus_actual.tipo)
                self.bonus_actual.activo = False
                SoundManager.play("bonus")

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
        surface.fill(Colors.NEGRO)
        self.jugador.dibujar(surface)
        for enemigo in self.enemigos:
            enemigo.dibujar(surface)
        for disparo in self.disparos:
            disparo.dibujar(surface)
        if self.bonus_actual and self.bonus_actual.activo:
            self.bonus_actual.dibujar(surface)

        # HUD
        hud = self.fuente.render(f"Nivel:{self.nivel}  Vida:{self.jugador.vida}  Puntos:{self.jugador.puntos}", True, Colors.BLANCO)
        surface.blit(hud, (20, 20))

        # Inventario de bonus
        for i in range(1, 6):
            valor = self.jugador.bonus_teclas[i]
            if i in [1, 2, 3]:
                color = Colors.VERDE if valor else (80, 80, 80)
            else:
                color = Colors.MORADO if i == 5 and valor > 0 else (255, 100, 100) if i == 4 and valor > 0 else (80, 80, 80)
            pygame.draw.rect(surface, color, (20 + (i - 1) * 60, Level.ALTO - 50, 40, 40))
            txt = self.fuente.render(str(i), True, Colors.BLANCO)
            surface.blit(txt, (30 + (i - 1) * 60, Level.ALTO - 45))

        # Game Over
        if self.game_over:
            fin = self.fuente.render("GAME OVER", True, Colors.ROJO)
            surface.blit(fin, (Level.ANCHO//2 - 100, Level.ALTO//2))
