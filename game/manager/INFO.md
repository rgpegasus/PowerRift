<h1 align="center">
Informations
</h1>
<p align="center">
L'objectif des fonctions manager est de simplifier l'import et l'utilisation de certaines actions
<p>

---

## `input.py`
##### Sert a relier une touche a une action
###### Avant chaque utilisation de il faut l'importer une fois tout en haut du fichier avec `from game.manager.input import inputManager`
- La fonction renvoie `True` ou `False` en fonction de si l'action existe ou non. Les noms visiblent dans `InputManager()` ne sont qu'a titre indicati. Par exemple `q` qui correspond a `left` peut etre setup de sorte que sa amène le joueur a sauter. Mais l'idéal est de garder la même action tout le long
- Pour l'utiliser il faut faire `inputManager.type("action")`. Le plus simple est de faire une condition `if`. Par exemple :

```py
if inputManager.pressed("left"):
    print("aller a gauche")
```
> Ce code va afficher "aller a gauche" tant que la touche q est préssée

```py
if inputManager.click("attack"):
    print("attaquer")
```
> Ce code va afficher "attaquer" une unique fois lorsque que le clique gauche de la souris est préssé

```py
if inputManager.combo_pressed([["up", "attack"]):
    print("attaquer vers le haut")
```
> Ce code va afficher "attaquer vers le haut" tant que le clique gauche de la souris ainsi que la touche z sont préssés en même temps

---

## `page.py`
##### Sert a charger une page en supprimant la précédente
###### Avant chaque utilisation de il faut l'importer une fois tout en haut du fichier avec `from game.manager.page import PageManager`
- Pour l'utiliser il faut juste faire `PageManager.load("nomDuFichier")` Par exemple :
```py
PageManager.load("menu")
```

---

## `resource.py`
##### Sert à importer les images/sons
###### Avant chaque utilisation de il faut l'importer une fois tout en haut du fichier avec `from game.manager.resource import resourceManager`
- Pour les images il faut faire par exemple `minecraftPig = resourceManager.picture("minecraft-pig/idle")` pour un fichier se trouvant dans :
```
resources
    |__pictures
            |__minecraft-pig
            |       |__idle.png
            |       |__...
            |__...
```
- Pour les icons il faut faire par exemple `homeIcon = resourceManager.icon("home")` pour un fichier se trouvant dans :
```
resources
    |__icons
        |__home.png
        |__...     
```
- Pour les sounds effects il faut faire par exemple `deathEffet = resourceManager.effect("death")` pour un fichier se trouvant dans :
```
resources
    |__sounds
            |__effects
            |       |__death.mp3
            |       |__...
            |__...
```
- Pour les musique il faut faire par exemple `mainMusic = resourceManager.music("main")` pour un fichier se trouvant dans :
```
resources
    |__sounds
            |__music
            |   |__main.mp3
            |   |__...
            |__...
```