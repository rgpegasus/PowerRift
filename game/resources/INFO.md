<h1 align="center">
Information
</h1>
<p align="center">
Ce dossier contient uniquement des images
<p>

---

## Nommage et architecture des fichiers
- Nommer vos ficher en suivant la forme `nom-du-fichier.extension` par exemple pour le bouton pour lancer le jeu `PlayIcon.png`
- Donner des noms clairs
- S'il s'agit d'une icon suivez la forme `nom-du-fichier.extension` 
- Privilégiez les images sans fond comme avec les `.png`  ( les `.svg` ne sont pas pris en charge il me semble)
- Si vous avez plusieurs images du meme type par exemple pour `character-1`, il y a une image ou il est debout et une autre mort alors vous aurez :
```
pictures
    |__character-1
    |            |__standing.png
    |            |__dead.png
    |__...
```
- Tout est pareil pour les sons. Priviligiez les sons avec les extensions `.mp3` ou `.wav`

---

## Taille
- Pour les icons l'idéal serait d'avoir des images entre 24 et 48px pour la qualité
- Pour les images de background au moins du 1080p
- Le reste a vous de voir mais il faut trouver un équilibre entre qualité et taille sur le disque, si il y a trop de grosse image le jeu risque d'etre surchargé

---

## Ou trouver
- Beaucoup d'image/logo seront a faire vous même, le plus simple est d'utiliser figma.com pour faire les designs
- Il existe des sites comme fonts.google.com/icons qui disposent de nombreux icons ou vous pouvez changer la taille/couleur 
- Vous pouvez prendre des sons de youtubes et les convertirs en mp3 avec des convertisseurs en ligne
- Pour le reste, cherchez par vous même


---

## Import
voir `resources.py` dans `.game/manager/INFO.md`