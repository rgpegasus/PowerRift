<h1 align="center">
Information
</h1>
<p align="center">
Ce dossier contient uniquement des images
<p>

---

## Nommage et architecture des fichiers
- Nommer vos ficher en suivant la forme `nom-du-fichier.extension` par exemple pour le personnage `minecraft-pig.png`
- Donner des noms clairs et organiser bien les images, les icons dans `resources/icons` et les autres images dans `resources/pictures`
- Privilégiez les images sans fond comme avec les `.png`  ( les `.svg` ne sont pas pris en charge il me semble)
- Si vous avez plusieurs images du meme type par exemple pour `minecraft-pig`, il y a une image ou il est inactif et une autre en train de marcher alors vous aurez :
```
pictures
    |__minecraft-pig
    |            |__idle.png
    |            |__walk.png
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