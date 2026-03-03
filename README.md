
# BLUE TOWER #
Est un jeu tower defense/degestion une sorte de `Bloon TD5` fusionner avec un `Clash of Clan` le tout code en python avec Pygame.

## Histoire du jeu
Blue est une petite creature bleu, qui se retrouve seul au millieu d'une Ile dessertique.
Pensant etre seul il pars a la decouverte de se nouveau monde, mais il se rendra tres vite compte qu'il n'est pas le seul a s'etre retouver ici qu'il y aurai un peu plus que du hasrad pour que d'autre creature comme lui se retrouve comme lui.
Pour survire fasse au autre creature hostile il va devoir explorer, et ameliorer son campemant
pour survire le plus longtemps et qui sais peut-etre pourra t-il lui aussi rejoindre `LES GRANDS` ...

## Fonctionnalite du moteur de jeu
pour l'instant le jeu embarque un editeur de UI, ce qui permet de maniere visuel de deplacer les element afficher a l'ecran comme le ``score``, les `boutons` ou encore les `element du shop` juste avec la souris en activant le mode edit via la touche F1.

Il enporte aussi avec lui plein d'elemtn de base comme un UIgraph avec ne nombreux UIElement pour pouvoir developper de maniere rapide son UI,

On y retoiuve aussi un systeme d'Entity,une Camera et Une Scene. ce qui permet de facilement diviser son jeu en couche logic

``` 
App -> Managers -> Entity
 |       |
 |       -> Camera
 -> UI
``` 

```
L'idee deriere ce jeu est d'apprendre la programmation et le Game Dev
```

## Qql image de mon jeu
### Blue 
<img src="assets/player.png" alt="drawing" width="50">
 le perso principale

### Image (Menu/Pause/Shop/Ingame)
#### MENU
![](assets/Screenshot%20from%202026-03-02%2022-11-27.png)
#### IN-GAME
![](assets/Screenshot%20from%202026-03-02%2022-11-40.png)
#### PAUSE
![](assets/Screenshot%20from%202026-03-02%2022-11-44.png)
#### SHOP
![](assets/Screenshot%20from%202026-03-02%2022-11-59.png)

## Future MAJ/Ajout pour le jeu (d'ici le 15 mars)
Un systeme d'upgrade pour les batiments et le joueurs, un panel pour avoir des info sur les element selectionner.


## Installation
Pour installer et test mon jeu, rien de plus simple : 

Clone le repo avec la commande suivante
```
git clone https://github.com/Lumosity23/Blue_tower.git
```

Installer UV si vous ne l'avez pas ( c'est un packages manager comme pip mais en mieux )

pour linux :
```
sudo apt install uv
```

pour windows :
```
winget install uv
```

ensuite utiliser uv pour sync votre clonage pour avoir le meme environemnt que moi :
```
uv sync
```

et pour finir pour lancer le jeu executer simplement la commande suivante :
```
uv run src/main.py
```

## Appropos de moi

Je suis un dev junior, j'apprend la programation depuis maintenant `3 mois`, j'essaye de faire ce qui me passe par la tete tout en ecoutant les retours de mes amis sur mon projet.