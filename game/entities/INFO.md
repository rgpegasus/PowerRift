<h1 align="center">
Informations
</h1>
<p align="center">
Ce dossier contient toutes les entitées du jeu
<p>

---

## Import
- Toujours importer `from ursina import *`, si vous savez quels imports vous allez utiliser, n'importez que ce en question
- S'il y a des redirections vers une autre page, importer `from game.manager.page import PageManager`
- S'il y a des variables, importer `from game.core.variables import Variables`
- S'il y a des images/sons, importer `from game.manager.resource import resourceManager` (voir `resource.py` dans `game/manager/INFO.py`)
    
---

### Code
- Après que les imports ont été ajouté, il faut créer une class :
    ```py 
    class Exemple(Entity):
        def __init__(self, **kwargs):
            super().__init__(model="quad", texture=minecraftPigIdle, scale=(1,1), collider="box", **kwargs)
    ```
> Le nom de la class peut etre ce que vous voulez mais de préférence suivez la forme `NomDeLaClass`, L'`Entity` sert a relier ursina a notre scène il faut donc toujours le mettre. Le `super().__init__()` sert a transmettre les paramètres de la class `Entity` à votre class. Le `**kwargs` est aussi important. Il permet de changer certains paramètres lors de l'appel de la class. Par exemple `self.pig = Exemple(y = -1)` change la hauteur d'apparition du cochon sur la map
- Pour le reste faites vos propres recherches