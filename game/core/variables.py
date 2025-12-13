#Contient tous les variables globals que ce soit des paramètres ou des constantes du jeu
from screeninfo import get_monitors

monitor = get_monitors()[0]

class Variables:
    WINDOW_SIZE = (monitor.width, monitor.height -1)
    PLAYER_SPEED = 6
    GRAVITY = 20
    JUMP_FORCE = 10

