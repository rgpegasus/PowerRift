from ursina import *
from ursinanetworking import *
from game.entities.demon import Demon

class NetworkManager(Entity):
    def __init__(self):
        super().__init__()
        self.server = None
        self.client = None
        self.is_host = False
        self.local_player = None
        self.adversaires = {}

    def start_host(self):
        # Création du serveur
        self.server = UrsinaNetworkingServer("0.0.0.0", 5555)
        self.is_host = True
        print("Serveur (Host) démarré !")

		#SERVER
        @self.server.event
        def update_position(client, x, y):
            # Le serveur reçoit la position d'un joueur et la renvoie à TOUS
            self.server.broadcast("update_position", client.id, x, y)

    def join_server(self, ip):
        # Création du client
        self.client = UrsinaNetworkingClient(ip, 5555)
        print(f"Connexion au serveur {ip}...")

        #CLIENT
        @self.client.event
        def update_position(id_joueur, x, y):
            if id_joueur in self.adversaires:
                # Joueur connu
                ennemi = self.adversaires[id_joueur]
                ennemi.target_position = Vec3(x, y, 0)
                
            else:
                # Nouveau joueur
                print(f"Nouveau joueur détecté : ID {id_joueur}")
                
				# Création du perso
                # is_mine = c'est mon perso
                nouvel_ennemi = Demon(position=(x,y,0), is_mine=False)
                
                # Je l'ajoute à mon carnet d'adresses
                self.adversaires[id_joueur] = nouvel_ennemi
    def set_local_player(self, player_entity):
        """Définit le personnage de l'utilisateur"""
        self.local_player = player_entity

    def update(self):
        if self.server: self.server.process_net_events()
        if self.client: self.client.process_net_events()
        if self.client and self.local_player and self.local_player.enabled:
            self.client.send("update_position", self.local_player.x, self.local_player.y)

network_manager = NetworkManager()