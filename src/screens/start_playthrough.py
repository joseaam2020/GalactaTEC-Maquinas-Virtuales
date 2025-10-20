import pygame
import random
import math
import time

pygame.init()

# -----------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -----------------------------------------------------
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Space Invaders con Bonus y Disparos")
clock = pygame.time.Clock()
fuente = pygame.font.SysFont(None, 28)

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 128, 255)
AMARILLO = (255, 255, 0)
MORADO = (180, 0, 255)
CYAN = (0, 255, 255)

# -----------------------------------------------------
# CLASES
# -----------------------------------------------------
class Jugador:
    def __init__(self):
        self.x = ANCHO // 2
        self.y = ALTO - 60
        self.vel = 5
        self.vida = 3
        self.puntos = 0
        self.escudo = 0
        self.tamaño = 40
        self.doble_puntos = False
        self.doble_puntos_fin = 0
        self.tipo_disparo = "normal"
        self.invulnerable_hasta = 0
        self.bonus_teclas = {1: False, 2: False, 3: False, 4: 0, 5: 0}
        self.controles_invertidos = False
        self.fin_inversion = 0

    def mover(self, teclas):
        vel_x, vel_y = self.vel, self.vel

        # Si los controles están invertidos
        if self.controles_invertidos and time.time() < self.fin_inversion:
            vel_x, vel_y = -vel_x, -vel_y
        elif self.controles_invertidos and time.time() >= self.fin_inversion:
            self.controles_invertidos = False  # fin de la inversión

        # Movimiento horizontal
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x -= vel_x
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x += vel_x
        # Movimiento vertical
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.y -= vel_y
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.y += vel_y

        # Rebote al tocar paredes
        if self.x < 0:
            self.x = 0
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5  # invierte controles 0.5 segundos
        elif self.x > ANCHO - self.tamaño:
            self.x = ANCHO - self.tamaño
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5

        if self.y < 0:
            self.y = 0
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5
        elif self.y > ALTO - self.tamaño:
            self.y = ALTO - self.tamaño
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5

    def dibujar(self, superficie):
        color = AZUL if self.escudo == 0 else AMARILLO
        pygame.draw.rect(superficie, color, (self.x, self.y, self.tamaño, self.tamaño))
        if self.escudo > 0:
            pygame.draw.circle(superficie, CYAN, (self.x + 20, self.y + 20), 30, 2)

    def disparar(self, disparos):
        disparos.append(Disparo(self.x + 20, self.y-10, self.tipo_disparo))
        if self.tipo_disparo == "area":
            self.bonus_teclas[4] -= 1
            if self.bonus_teclas[4] <= 0:
                self.tipo_disparo = "normal"
        elif self.tipo_disparo == "rastreador":
            self.bonus_teclas[5] -= 1
            if self.bonus_teclas[5] <= 0:
                self.tipo_disparo = "normal"

    def recibir_daño(self):
        if time.time() < self.invulnerable_hasta:
            return
        if self.escudo > 0:
            self.escudo -= 1
        else:
            self.vida -= 1
        self.invulnerable_hasta = time.time() + 1

    def aplicar_bonus(self, tipo):
        if tipo == "vida" and self.vida < 3:
            self.vida += 1
        elif tipo == "doble_puntos":
            self.doble_puntos = True
            self.doble_puntos_fin = time.time() + 15
        elif tipo == "escudo":
            self.escudo = 3

    def actualizar_bonus(self):
        if self.doble_puntos and time.time() > self.doble_puntos_fin:
            self.doble_puntos = False

    def asignar_bonus_tecla(self, tipo):
        if tipo == "vida":
            self.bonus_teclas[1] = True
        elif tipo == "escudo":
            self.bonus_teclas[2] = True
        elif tipo == "doble_puntos":
            self.bonus_teclas[3] = True
        elif tipo == "area":
            self.bonus_teclas[4] = 1
        elif tipo == "rastreador":
            self.bonus_teclas[5] = 3

    def usar_bonus(self, tecla):
        if tecla == 1 and self.bonus_teclas[1]:
            self.aplicar_bonus("vida")
            self.bonus_teclas[1] = False
        elif tecla == 2 and self.bonus_teclas[2]:
            self.aplicar_bonus("escudo")
            self.bonus_teclas[2] = False
        elif tecla == 3 and self.bonus_teclas[3]:
            self.aplicar_bonus("doble_puntos")
            self.bonus_teclas[3] = False
        elif tecla == 4 and self.bonus_teclas[4] > 0:
            self.tipo_disparo = "area"
        elif tecla == 5 and self.bonus_teclas[5] > 0:
            self.tipo_disparo = "rastreador"

class Disparo:
    def __init__(self, x, y, tipo="normal"):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.vel = 7
        self.radio = 5
        self.impactado = False
        self.explosion_frames = 0
        self.explosion_radio = 0  # NUEVO — tamaño del área de daño

    def mover(self, _=None):
        # Solo se mueve si no ha explotado
        if not self.impactado:
            self.y -= self.vel
        # Si está explotando, no se mueve

    def dibujar(self, superficie):
        color = {"normal": BLANCO, "rastreador": MORADO, "area": ROJO}.get(self.tipo, BLANCO)
        pygame.draw.circle(superficie, color, (int(self.x), int(self.y)), self.radio)

        # Dibujar explosión AOE
        if self.tipo == "area" and self.impactado:
            pygame.draw.circle(superficie, (255, 150, 0), (int(self.x), int(self.y)), self.explosion_radio, 6)
            pygame.draw.circle(superficie, (255, 200, 50), (int(self.x), int(self.y)), self.explosion_radio + 20, 3)

    def iniciar_explosion(self, radio=100, duracion=15):
        """Activa la explosión visual y lógica del disparo AOE"""
        self.explosion_radio = radio
        self.explosion_frames = duracion
        self.impactado = True

    def fuera_de_pantalla(self):
        return self.y < -50 or self.y > ALTO + 50 or self.x < -50 or self.x > ANCHO + 50 or (self.tipo == "area" and self.explosion_frames <= 0)

class Bonus:
    TIPOS = ["vida", "doble_puntos", "escudo", "rastreador", "area"]
    COLORES = {"vida": VERDE, "doble_puntos": AMARILLO, "escudo": CYAN, "rastreador": MORADO, "area": ROJO}

    def __init__(self, tipo):
        self.tipo = tipo
        self.color = Bonus.COLORES[tipo]
        self.x = random.randint(20, ANCHO - 40)
        self.y = -20
        self.vel = 1  # más lento
        self.tamaño = 20
        self.activo = True

    def mover(self):
        self.y += self.vel
        if self.y > ALTO:
            self.activo = False

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, (self.x, self.y, self.tamaño, self.tamaño))

    def colisiona_con(self, jugador):
        return pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(jugador.x, jugador.y, jugador.tamaño, jugador.tamaño)
        )

class Enemigo:
    def __init__(self, x, y):
        self.x_inicial = x
        self.y_inicial = y
        self.x = x
        self.y = y
        self.tamaño = 40
        self.color = ROJO
        self.vivo = True

    def dibujar(self, superficie):
        if self.vivo:
            pygame.draw.rect(superficie, self.color, (self.x, self.y, self.tamaño, self.tamaño))

    def colisiona_con_disparo(self, disparo):
        return self.vivo and pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(disparo.x - disparo.radio, disparo.y - disparo.radio, disparo.radio*2, disparo.radio*2)
        )

    def colisiona_con_jugador(self, jugador):
        return self.vivo and pygame.Rect(self.x, self.y, self.tamaño, self.tamaño).colliderect(
            pygame.Rect(jugador.x, jugador.y, jugador.tamaño, jugador.tamaño)
        )

    def mover(self, dx, dy):
        if self.vivo:
            self.x += dx
            self.y += dy
            if self.y > ALTO:
                self.y = -self.tamaño  # reaparece arriba

    def reiniciar(self):
        self.x = self.x_inicial
        self.y = self.y_inicial
        self.vivo = True

# -----------------------------------------------------
# CONFIGURACIÓN DEL JUEGO
# -----------------------------------------------------
jugador = Jugador()
disparos = []
bonus_actual = None
bonus_usados_nivel = set()
ultimo_bonus_tiempo = time.time()
siguiente_bonus = random.randint(3, 4)

nivel = 1
puntos_para_siguiente_nivel = 200

# Creación de la formación de enemigos
enemigos = []
espacio_x = 55
espacio_y = 55
filas = 6
for fila in range(filas):
    enemigos_en_fila = filas - fila  # empieza con 6 y termina con 1
    for col in range(enemigos_en_fila):
        x = ANCHO//2 - (enemigos_en_fila * espacio_x)//2 + col * espacio_x
        y = -320 + fila * espacio_y
        enemigos.append(Enemigo(x, y))

direccion_x = 1
vel_x = 2
vel_y = 20

# -----------------------------------------------------
# BUCLE PRINCIPAL
# -----------------------------------------------------
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                jugador.disparar(disparos)
            if pygame.K_1 <= evento.key <= pygame.K_5:
                jugador.usar_bonus(evento.key - pygame.K_1 + 1)

    teclas = pygame.key.get_pressed()
    jugador.mover(teclas)
    jugador.actualizar_bonus()

    # -------------------------------------------------
    # MOVER ENEMIGOS
    # -------------------------------------------------
    vivos = [e for e in enemigos if e.vivo]
    if vivos:
        max_x = max(e.x for e in vivos) + 40
        min_x = min(e.x for e in vivos)
        if max_x >= ANCHO - 10:
            direccion_x = -1
            for e in enemigos:
                e.mover(0, vel_y)
        elif min_x <= 10:
            direccion_x = 1
            for e in enemigos:
                e.mover(0, vel_y)
        for e in enemigos:
            e.mover(vel_x * direccion_x, 0)

    # -------------------------------------------------
    # DISPAROS Y COLISIONES
    # -------------------------------------------------
    for disparo in disparos[:]:
        disparo.mover()

        # --- DISPARO AOE (de área) ---
        if disparo.tipo == "area":
            if not disparo.impactado:
                # Verifica si impacta un enemigo
                for enemigo in enemigos:
                    if enemigo.colisiona_con_disparo(disparo):
                        disparo.iniciar_explosion(radio=120, duracion=25)
                        break
            else:
                # Daño radial mientras dura la explosión
                for enemigo in enemigos:
                    if enemigo.vivo:
                        dx = (enemigo.x + enemigo.tamaño / 2) - disparo.x
                        dy = (enemigo.y + enemigo.tamaño / 2) - disparo.y
                        distancia = math.hypot(dx, dy)
                        if distancia <= disparo.explosion_radio:
                            enemigo.vivo = False
                            jugador.puntos += 10 * (2 if jugador.doble_puntos else 1)

                # Reducir frames de la animación
                disparo.explosion_frames -= 1
                if disparo.explosion_frames <= 0:
                    disparos.remove(disparo)
                    continue

        # --- DISPARO NORMAL O RASTREADOR ---
        else:
            for enemigo in enemigos:
                if enemigo.colisiona_con_disparo(disparo) and not disparo.impactado:
                    enemigo.vivo = False
                    jugador.puntos += 10 * (2 if jugador.doble_puntos else 1)
                    disparo.impactado = True
                    break
            if disparo.impactado:
                disparos.remove(disparo)
                continue

        # Eliminar disparos fuera de pantalla
        if disparo.y < -50 or disparo.y > ALTO + 50:
            disparos.remove(disparo)
            continue

    # -------------------------------------------------
    # COLISION JUGADOR-ENEMIGOS (daño mutuo)
    # -------------------------------------------------
    for enemigo in enemigos:
        if enemigo.vivo and enemigo.colisiona_con_jugador(jugador):
            jugador.recibir_daño()   # El jugador recibe daño
            enemigo.vivo = False      # El enemigo muere al chocar

    # -------------------------------------------------
    # BONUS
    # -------------------------------------------------
    if bonus_actual and bonus_actual.activo:
        bonus_actual.mover()
        if bonus_actual.colisiona_con(jugador):
            jugador.asignar_bonus_tecla(bonus_actual.tipo)
            bonus_actual.activo = False

    if time.time() - ultimo_bonus_tiempo >= siguiente_bonus and len(bonus_usados_nivel) < len(Bonus.TIPOS):
        tipo = random.choice([t for t in Bonus.TIPOS if t not in bonus_usados_nivel])
        bonus_actual = Bonus(tipo)
        bonus_usados_nivel.add(tipo)
        ultimo_bonus_tiempo = time.time()
        siguiente_bonus = random.randint(10, 20)

    # -------------------------------------------------
    # NUEVA RONDA
    # -------------------------------------------------
    if all(not e.vivo for e in enemigos):
        nivel += 1
        puntos_para_siguiente_nivel += 200
        bonus_usados_nivel.clear()
        for e in enemigos:
            e.reiniciar()

    # -------------------------------------------------
    # DIBUJAR ESCENA
    # -------------------------------------------------
    pantalla.fill(NEGRO)
    jugador.dibujar(pantalla)
    for enemigo in enemigos:
        enemigo.dibujar(pantalla)
    for disparo in disparos:
        disparo.dibujar(pantalla)
    if bonus_actual and bonus_actual.activo:
        bonus_actual.dibujar(pantalla)

    # HUD
    hud = fuente.render(f"Nivel:{nivel}  Vida:{jugador.vida}  Puntos:{jugador.puntos}", True, BLANCO)
    pantalla.blit(hud, (20, 20))

    # Inventario de bonus
    for i in range(1, 6):
        valor = jugador.bonus_teclas[i]
        if i in [1,2,3]:
            color = VERDE if valor else (80,80,80)
        else:
            color = MORADO if i==5 and valor>0 else (255,100,100) if i==4 and valor>0 else (80,80,80)
        pygame.draw.rect(pantalla, color, (20+(i-1)*60, ALTO-50, 40, 40))
        txt = fuente.render(str(i), True, BLANCO)
        pantalla.blit(txt, (30+(i-1)*60, ALTO-45))

    # Game Over
    if jugador.vida <= 0:
        fin = fuente.render("GAME OVER", True, ROJO)
        pantalla.blit(fin, (ANCHO//2 - 100, ALTO//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        ejecutando = False
        continue

    pygame.display.flip()
    clock.tick(60)

pygame.quit()