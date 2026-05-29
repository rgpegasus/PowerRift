from game.core.engine import engine
from game.core.state import state
from game.manager.page import PageManager

def update():
    if engine.netRole:
        engine.netRole.update_network()
        
        # Si le client a reçu la map du host, charger le jeu
        if (engine.netRole.role == "client" and 
            engine.netRole.map_to_load is not None):
            state.selected_map = engine.netRole.map_to_load
            PageManager.load(state.game_mode)
            engine.netRole.map_to_load = None  # Reset pour éviter les recharges

if __name__ == "__main__":
    engine.run()