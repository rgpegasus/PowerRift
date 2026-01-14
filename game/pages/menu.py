# Exemple de menu simple
from ursina import *
from game.manager.page import PageManager

class Scene(Entity):
    def __init__(self):
        super().__init__()
        Text(
            "MENU PRINCIPAL", 
            x=-0.1, 
            y = 0.05
        )
        Button(
            "Jouer", 
            y=-0.05, 
            scale_x = 0.25, 
            scale_y = 0.035, 
            on_click=lambda: PageManager.load("test")
        )

#C'est Ilyan ! Pour celui qui fait les menus, il peut inclure ça dans son code pour le relier au mien (le networking) :


#from game.network.manager import network_manager # Importe le networking

#def on_host_button_click():
    #network_manager.start_host() # Quand t'appui sur le bouton host

#def on_join_button_click():
    #ip = input_field.text
    #network_manager.join_server(ip) # Quan dt'appuie sur le bouton "rejoindre"