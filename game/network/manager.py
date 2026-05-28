from ursinanetworking import *


class Networking:
    def __init__(self, role, ipServer="0.0.0.0", on_ready=None):
        self.ennemis = {}
        self.role = role
        self.my_id = None
        self.connected = False
        self.opponent_disconnected = False
        self.on_ready = on_ready
        self.pending_hit = None   # knockback reçu à appliquer au prochain update

        if role == "host":
            self.host = UrsinaNetworkingServer("0.0.0.0", 5555)
            self.client = UrsinaNetworkingClient("localhost", 5555)

            @self.host.event
            def onClientConnected(subject):
                print(f"[serveur] joueur connecté — id: {subject.id} | joueurs en ligne: {len(self.host.clients)}")
                subject.send_message("your_id", {"id": subject.id})

            @self.host.event
            def onClientDisconnected(subject):
                print(f"[serveur] joueur déconnecté — id: {subject.id}")
                for client in self.host.clients:
                    client.send_message("game_ended", {
                        "reason": "opponent_disconnected",
                        "id": subject.id
                    })

            @self.host.event
            def server_inputs(client_sender, data):
                for client in self.host.clients:
                    if client.id != client_sender.id:
                        client.send_message("enemy_inputs", {
                            "id": client_sender.id,
                            **data
                        })

            @self.host.event
            def server_hit(client_sender, data):
                # Renvoyer le hit à la victime (tous sauf l'attaquant)
                for client in self.host.clients:
                    if client.id != client_sender.id:
                        client.send_message("enemy_hit", {
                            "id":          client_sender.id,
                            "knockback_x": data["knockback_x"],
                            "knockback_y": data["knockback_y"],
                            "kokoro":      data["kokoro"],
                        })

        else:
            self.host = None
            self.client = UrsinaNetworkingClient(ipServer, 5555)

        @self.client.event
        def onConnectionEstablished():
            self.connected = True
            print(f"[client] socket connectée, en attente de l'id serveur...")

        @self.client.event
        def your_id(data):
            self.my_id = data["id"]
            print(f"[client] id assigné : {self.my_id}")
            if self.on_ready:
                self.on_ready()

        @self.client.event
        def enemy_inputs(data):
            if self.my_id is not None and data["id"] == self.my_id:
                return
            self.ennemis[data["id"]] = {
                "inputs": data["inputs"],
                "facing": data["facing"],
                "x":      data["x"],
                "y":      data["y"],
            }

        @self.client.event
        def enemy_hit(data):
            # C'est MOI qui suis touché — stocker pour application dans 1v1.update()
            self.pending_hit = {
                "knockback_x": data["knockback_x"],
                "knockback_y": data["knockback_y"],
                "kokoro":      data["kokoro"],
            }

        @self.client.event
        def game_ended(data):
            self.opponent_disconnected = True
            print(f"[client] partie terminée — raison: {data['reason']}")

    def send(self, message, data):
        if self.connected and self.my_id is not None:
            self.client.send_message(message, data)

    def update_network(self):
        if self.host:
            self.host.process_net_events()
        if self.client:
            self.client.process_net_events()