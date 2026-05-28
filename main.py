from game.core.engine import engine

def update():
    if engine.netRole:
        engine.netRole.update_network()

if __name__ == "__main__":
    engine.run()