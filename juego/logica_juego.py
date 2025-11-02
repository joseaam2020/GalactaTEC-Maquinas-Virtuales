import pygame
import objetos_moviles
from math import sin, cos, pi

class jugador_dummy:
    def __init__(self):
        self.puntaje = 0

def generar_curva(funcion='seno', x_inicio=0, x_fin=800, paso=50, amplitud=100, frecuencia=1, desplazamiento_y=300):
    """
    Genera una lista de puntos (x, y) de una curva onda.

    Args:
        funcion (str): 'seno' o 'coseno'.
        x_inicio (int): valor inicial de x.
        x_fin (int): valor final de x.
        paso (int): incremento de x entre puntos.
        amplitud (float): altura máxima de la onda.
        frecuencia (float): número de ciclos en todo el rango x.
        desplazamiento_y (float): desplazamiento vertical (para centrar en la pantalla).
    
    Returns:
        List[Tuple[float, float]]: lista de coordenadas (x, y).
    """
    puntos = []
    for x in range(x_inicio, x_fin + 1, paso):
        angulo = 2 * pi * frecuencia * (x - x_inicio) / (x_fin - x_inicio)
        if funcion == 'seno':
            y = desplazamiento_y + amplitud * sin(angulo)
        elif funcion == 'coseno':
            y = desplazamiento_y + amplitud * cos(angulo)
        else:
            raise ValueError("Función no soportada: usa 'seno' o 'coseno'")
        puntos.append((x, y))
    return puntos

# Ejemplo de uso
puntos_seno = generar_curva('seno', x_inicio=0, x_fin=800, paso=50, amplitud=100, frecuencia=2, desplazamiento_y=300)
# Inicializar Pygame
pygame.init()

# Configuración de la ventana
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Ventana Básica")

jugador_prueba = objetos_moviles.Nave_jugador(surface=pantalla, jugador=jugador_dummy(), imagenes=["GalactaTEC-Maquinas-Virtuales/juego/nave prueba.png"], x=ALTO//2, y=ALTO//2, velocidad=200, direccion=objetos_moviles.Direcciones.Ninguna)
enemigo_prueba = objetos_moviles.Objeto_con_trayectoria(surface=pantalla, imagenes=["GalactaTEC-Maquinas-Virtuales/juego/nave prueba.png"], x=ALTO//2, y=ALTO//2, velocidad=200, trayectoria = puntos_seno)
grupo = pygame.sprite.Group()
grupo.add(enemigo_prueba)
grupo.add(jugador_prueba)

clock = pygame.time.Clock()
# Bucle principal
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                nueva_bala = jugador_prueba.disparar()
                jugador_prueba.balas_disparadas.add(nueva_bala)
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_d]:
            jugador_prueba.set_direccion(1)
        elif teclas[pygame.K_a]:
            jugador_prueba.set_direccion(2)
        else:
            jugador_prueba.set_direccion(0)
    
    
    delta_t = clock.tick(60) / 1000

    # Llenar la pantalla de negro
    pantalla.fill((255, 255, 255))
    grupo.update(delta_t)


    # Actualizar la pantalla
    pygame.display.flip()

# Salir de Pygame
pygame.quit()
