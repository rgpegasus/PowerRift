from ursinanetworking import *


class Networking:
    def __init__(self, role, ipServer="0.0.0.0", on_ready=None, on_client_connected=None):
        self.ennemis = {}
        self.role = role
        self.my_id = None
        self.connected = False
        self.opponent_disconnected = False
        self.on_ready = on_ready                        # Callback quand TOUS les joueurs sont prêts (spawn)
        self.on_client_connected = on_client_connected  # Callback quand un vrai client se connecte (host)
        self.pending_hit = None     # Knockback reçu à appliquer au prochain update
        self.map_to_load = None     # Map à charger (côté client, reçue du host)
        self.ready_clients = set()  # IDs des clients ayant ACK la map
        self._self_client_id = None # ID de la connexion localhost du host sur lui-même

        if role == "host":
            self.host = UrsinaNetworkingServer("0.0.0.0", 5555)
            # Le host s'assigne son propre ID statiquement, sans passer par le serveur
            self.my_id = 0
            self.connected = True
            # Se connecte à lui-même pour pouvoir émettre des messages via self.client
            self.client = UrsinaNetworkingClient("localhost", 5555)

            @self.host.event
            def onClientConnected(subject):
                # Le premier client à se connecter est TOUJOURS le host lui-même (localhost),
                # car self.client est instancié avant qu'un vrai client externe puisse arriver.
                if self._self_client_id is None:
                    self._self_client_id = subject.id
                    print(f"[serveur] connexion localhost mémorisée (id interne: {subject.id})")
                    return

                print(f"[serveur] vrai client connecté — id: {subject.id} | vrais joueurs: {len(self._real_clients())}")
                subject.send_message("your_id", {"id": subject.id})

                if self.on_client_connected:
                    self.on_client_connected()

            @self.host.event
            def onClientDisconnected(subject):
                if subject.id == self._self_client_id:
                    return
                print(f"[serveur] joueur déconnecté — id: {subject.id}")
                for client in self.host.clients:
                    if client.id != self._self_client_id:
                        client.send_message("game_ended", {
                            "reason": "opponent_disconnected",
                            "id": subject.id
                        })

            @self.host.event
            def server_inputs(client_sender, data):
                for client in self.host.clients:
                    # Relayer à tous sauf l'expéditeur — y compris le client localhost
                    # du host, pour que sa scène de jeu reçoive les enemy_inputs.
                    if client.id != client_sender.id:
                        client.send_message("enemy_inputs", {
                            "id": client_sender.id,
                            **data
                        })

            @self.host.event
            def server_hit(client_sender, data):
                for client in self.host.clients:
                    # Idem : le host doit recevoir les hits via son client localhost.
                    if client.id != client_sender.id:
                        client.send_message("enemy_hit", {
                            "id":          client_sender.id,
                            "knockback_x": data["knockback_x"],
                            "knockback_y": data["knockback_y"],
                            "kokoro":      data["kokoro"],
                        })

            @self.host.event
            def map_selected_ack(client_sender, data):
                if client_sender.id == self._self_client_id:
                    return

                self.ready_clients.add(client_sender.id)
                print(f"[serveur] ACK map reçu de client {client_sender.id}")

                # Lancer la partie quand tous les vrais clients ont confirmé
                real_clients = self._real_clients()
                if real_clients and all(c.id in self.ready_clients for c in real_clients):
                    print("[serveur] tous les clients prêts — lancement de la partie")
                    if self.on_ready:
                        self.on_ready()

        else:
            self.host = None
            self._self_client_id = None
            self.client = UrsinaNetworkingClient(ipServer, 5555)

        # ── Événements côté client (host et client pur) ──

        @self.client.event
        def onConnectionEstablished():
            if self.role == "host":
                return  # Le host est déjà marqué connecté
            self.connected = True
            print(f"[client] socket connectée, en attente de l'id serveur...")

        @self.client.event
        def your_id(data):
            # Reçu uniquement par les vrais clients (le host a my_id=0 statiquement)
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
                "kokoro": data.get("kokoro", 1),
            }

        @self.client.event
        def enemy_hit(data):
            self.pending_hit = {
                "knockback_x": data["knockback_x"],
                "knockback_y": data["knockback_y"],
                "kokoro":      data["kokoro"],
            }

        @self.client.event
        def game_ended(data):
            self.opponent_disconnected = True
            print(f"[client] partie terminée — raison: {data['reason']}")

        @self.client.event
        def map_selected(data):
            # Reçu uniquement par les vrais clients (le host ne s'envoie plus ce message)
            self.map_to_load = data["map_name"]
            print(f"[client] map reçue : {self.map_to_load} — en attente du chargement local...")
            # ACK envoyé via confirm_map_ready() depuis la scène de jeu,
            # une fois la map chargée et le joueur prêt à spawner.

    # ── Helpers ──

    def _real_clients(self):
        """Retourne les clients connectés hors connexion localhost du host."""
        if not self.host:
            return []
        return [c for c in self.host.clients if c.id != self._self_client_id]

    def real_client_count(self):
        """Nombre de vrais clients connectés."""
        return len(self._real_clients())

    # ── API publique ──

    def send(self, message, data):
        if self.connected and self.my_id is not None:
            self.client.send_message(message, data)

    def send_map_selection(self, map_name):
        """Host envoie la map sélectionnée aux vrais clients uniquement."""
        if self.role != "host" or not self.host:
            return
        self.ready_clients.clear()
        targets = self._real_clients()
        for client in targets:
            client.send_message("map_selected", {"map_name": map_name})
        print(f"[serveur] map '{map_name}' envoyée à {len(targets)} client(s)")

    def confirm_map_ready(self):
        """
        À appeler depuis la scène de jeu côté CLIENT, une fois la map chargée
        et le joueur prêt à spawner. Envoie l'ACK au host pour déclencher
        le lancement simultané de la partie.
        """
        if self.role == "client" and self.connected:
            print("[client] map chargée — envoi ACK au host")
            self.client.send_message("map_selected_ack", {"status": "confirmed"})

    def update_network(self):
        if self.host:
            self.host.process_net_events()
        if self.client:
            self.client.process_net_events()