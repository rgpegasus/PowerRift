from ursinanetworking import *

class Networking:
    def __init__(self, role, ipServer = "0.0.0.0"):
        self.ennemis = {}
        self.role = role
        self.my_id = None
        
        if role == "host":
            self.host = UrsinaNetworkingServer("0.0.0.0", 5555)
            self.client = UrsinaNetworkingClient("localhost", 5555)
            
            @self.host.event
            def onClientConnected(subject):
                print(f"[serveur] joueur connecté — id: {subject.id} | joueurs en ligne: {len(self.host.clients)}")
                for client in self.host.clients:
                    if client.id != subject.id:
                        subject.send_message("get_pos", {
                            "id": client.id,
                            "x": 0,
                            "y": 0
                        })
            
            @self.host.event
            def onClientDisconnected(subject):
                print(f"[serveur] joueur déconnecté — id: {subject.id} | joueurs restants: {len(self.host.clients)}")
                for client in self.host.clients:
                    client.send_message("player_disconnected", {"id": subject.id})
            
            @self.host.event
            def server_update_pos(client_sender, data):
                for client in self.host.clients:
                    if client.id != client_sender.id:
                        client.send_message("get_pos", {
                            "id": client_sender.id,
                            "x": data["x"],
                            "y": data["y"]
                        })
        else:
            self.host = None
            self.client = UrsinaNetworkingClient(ipServer, 5555)
        
        @self.client.event
        def onConnectionEstablished():
            self.my_id = getattr(self.client, 'id', None)
            print(f"[client] connecté au serveur — id local: {self.my_id}")
            self.client.send_message("server_update_pos", {
                "x": 0,
                "y": 0
            })
        
        @self.client.event
        def get_pos(data):
            if self.my_id is not None and data["id"] == self.my_id:
                return
            est_nouveau = data["id"] not in self.ennemis
            self.ennemis[data["id"]] = {"x": data["x"], "y": data["y"]}
            if est_nouveau:
                print(f"[client] nouvel ennemi détecté — id: {data['id']}")
        
        @self.client.event
        def player_disconnected(data):
            if data["id"] in self.ennemis:
                del self.ennemis[data["id"]]
                print(f"[client] ennemi déconnecté — id: {data['id']}")

    def update_network(self):
        if self.host:
            self.host.process_net_events()
        if self.client:
            self.client.process_net_events()