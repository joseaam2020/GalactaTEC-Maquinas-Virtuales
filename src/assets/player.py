import pygame
import time
from assets.proyectile import Disparo
from assets.colors import Colors
from assets.sound_manager import SoundManager

class Jugador:
    def __init__(self,screen):
        self.ALTO = screen.get_size()[1]
        self.ANCHO = screen.get_size()[0]
        self.x = self.ANCHO // 2
        self.y = self.ALTO - 60
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
        self.ultimo_sonido_mov = 0
        self.estela = []  # lista de posiciones para la estela
        self.estela_max = 15  # máximo de "partículas" visibles

    def mover(self, teclas):
        vel_x, vel_y = self.vel, self.vel
        movido = False

        # Si los controles están invertidos
        if self.controles_invertidos and time.time() < self.fin_inversion:
            vel_x, vel_y = -vel_x, -vel_y
        elif self.controles_invertidos and time.time() >= self.fin_inversion:
            self.controles_invertidos = False  # fin de la inversión

        # Movimiento horizontal
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x -= vel_x
            movido = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x += vel_x
            movido = True
        # Movimiento vertical
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.y -= vel_y
            movido = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.y += vel_y
            movido = True

        #Sonido al moverse
        if movido and time.time() - self.ultimo_sonido_mov >= 0.2:
            SoundManager.play("jugador_mueve")
            self.ultimo_sonido_mov = time.time()
        else:
            movido=False

        # Rebote al tocar paredes
        if self.x < 0:
            self.x = 0
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5  # invierte controles 0.5 segundos
        elif self.x > self.ANCHO - self.tamaño:
            self.x = self.ANCHO - self.tamaño
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5

        if self.y < 0:
            self.y = 0
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5
        elif self.y > self.ALTO - self.tamaño:
            self.y = self.ALTO - self.tamaño
            self.controles_invertidos = True
            self.fin_inversion = time.time() + 0.5

        # Guardar posición para la estela si bonus activo
        if self.doble_puntos:
            self.estela.append((self.x + self.tamaño//2, self.y + self.tamaño//2))
            if len(self.estela) > self.estela_max:
                self.estela.pop(0)

    def dibujar(self, superficie):
        # Dibujar estela si bonus activo
        if self.doble_puntos and self.estela:
            for i, pos in enumerate(self.estela):
                alpha = int(255 * (i + 1) / len(self.estela) / 2)  # más transparente hacia atrás
                radio = self.tamaño // 3
                capa = pygame.Surface((radio*2, radio*2), pygame.SRCALPHA)
                pygame.draw.circle(capa, (255, 255, 0, alpha), (radio, radio), radio)
                superficie.blit(capa, (pos[0] - radio, pos[1] - radio))

        # Dibujar el jugador (sea un rectángulo o una skin)
        if hasattr(self, "imagen") and self.imagen:  # si tiene una skin
            superficie.blit(self.imagen, (self.x, self.y))
        else:
            color = Colors.AZUL if self.escudo == 0 else Colors.AMARILLO
            pygame.draw.rect(superficie, color, (self.x, self.y, self.tamaño, self.tamaño))

        # Dibujar escudo visual (independiente de skin)
        if self.escudo > 0:
            centro = (self.x + self.tamaño // 2, self.y + self.tamaño // 2)
            max_radio = int(self.tamaño * 1.2)

            # Dibujar tres capas con distintos radios y transparencias
            for i in range(self.escudo):  # 3, 2 o 1 dependiendo del escudo restante
                radio = max_radio + (i * 6)
                alpha = 120 + i * 40  # más fuerte con más capas
                color = (0, 200, 255, alpha)  # cian brillante

                # Crear una superficie temporal con canal alfa
                capa = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
                pygame.draw.circle(capa, color, (radio, radio), radio, width=3)
                superficie.blit(capa, (centro[0] - radio, centro[1] - radio))

    def disparar(self, disparos):
        disparos.append(Disparo(self.x + 20, self.y-10, self.tipo_disparo))
        if self.tipo_disparo == "area":
            SoundManager.play("disparo_area")
            self.bonus_teclas[4] -= 1
            if self.bonus_teclas[4] <= 0:
                self.tipo_disparo = "normal"
        elif self.tipo_disparo == "rastreador":
            SoundManager.play("disparo_rastreador")
            self.bonus_teclas[5] -= 1
            if self.bonus_teclas[5] <= 0:
                self.tipo_disparo = "normal"
        else: 
            SoundManager.play("disparo_normal")

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
