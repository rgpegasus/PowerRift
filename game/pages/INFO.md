<h1 align="center">
Informations
</h1>
<p align="center">
Ce dossier contient toutes les pages du jeu
<p>

---

## Import
- Toujours importer `from ursina import *`, si vous savez quels imports vous allez utiliser, n'importez que ce en question
- S'il y a des redirections vers une autre page, importer `from game.manager.page import PageManager`
- S'il y a des variables, importer `from game.core.variables import Variables`
- S'il y a des images/sons, importer `from game.manager.resource import resourceManager` (voir `resource.py` dans `game/manager/INFO.py`)
- S'il y a des entités, importer `from game.entities.nom-du-fichier import NomDeLaClass` par exemple : 
    ```py
    from game.entities.exemple import Exemple
    ```
    
---

### Code
- Après que les imports ont été ajouté, il faut créer une class :
    ```py 
    class Scene(Entity):
        def __init__(self):
            super().__init__()
    ```
> Le nom de la class doit etre `Scene` pour correspondre au PageManager, L'`Entity` sert a relier ursina a notre scène il faut donc toujours le mettre. Enfin le `super().__init__()` sert a transmettre les paramètres de la class `Entity` à la class `Scene`
- Pour le reste faites vos propres recherches