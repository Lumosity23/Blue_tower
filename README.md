
# BLUE TOWER #
Est un jeu tower defense/degestion une sorte de `Bloon TD5` fusionner avec un `Clash of Clan` le tout code en python avec Pygame.

## Histoire du jeu
Blue est une petite créature bleue, qui se retrouve seule au milieu d’une île déserte. Pensant être seul, il part à la découverte de ce nouveau monde, mais il se rend très vite compte qu’il n’est pas le seul à s’être retrouvé ici, qu’il y aurait un peu plus que du hasard pour que d’autres créatures comme lui se retrouvent comme lui. Pour survivre face aux autres créatures hostiles, il va devoir explorer, et améliorer son campement pour survivre le plus longtemps et qui sait, peut-être pourra-t-il lui aussi rejoindre les ```grands``` …

## Fonctionnalités du moteur de jeu :
Pour l’instant, le jeu embarque un éditeur d’UI, ce qui permet de manière visuelle de déplacer les éléments affichés à l’écran comme le score, les boutons ou encore les éléments du shop, juste avec la souris en activant le mode edit via la touche F1. 

Il emporte aussi avec lui pleins d’éléments de base comme un UIgraph avec de nombreux UIelement pour pouvoir développer de manière rapide son UI. 

On y retrouve aussi un système d’entité, une caméra et une scène. Ce qui permet de facilement diviser son jeu en couches logiques. 


``` 
App -> Managers -> Entity
 |       |
 |       -> Camera
 -> UI
``` 

```
L'idée derrière ce jeu est d’apprendre la programmation et le Game Dev.
```

## Quelques images de mon jeu

### Blue 
<img src="assets/player.png" alt="drawing" width="50">
 personnage principale [ vue de face ]

### Image (Menu/Pause/Shop/Ingame)
#### MENU
![](assets/ScreenShots/Screenshot%20from%202026-03-02%2022-11-27.png)
#### IN-GAME
![](assets/ScreenShots/Screenshot%20from%202026-03-02%2022-11-40.png)
#### PAUSE
![](assets/ScreenShots/Screenshot%20from%202026-03-02%2022-11-44.png)
#### SHOP
![](assets/ScreenShots/Screenshot%20from%202026-03-02%2022-11-59.png)

## Future MAJ/Ajout pour le jeu (d'ici le debut avril)
Un systeme d'upgrade pour les batiments et le joueurs.

## Update du JOUR ( 24 mars )
Entrain de travailler sur les ennemis, pour qu'ils soit affecter par les murs et qu'ils puissent les detruire.
Je travail aussi sur les systeme de chunk qui est encore un peu approximatif...

### voici un petit screen de cet Ajouts :
#### c'est pour montrer que mtn les ennemis sont bloquer par les murs
![](assets/ScreenShots/update_24_mars.png)

## Installation
Pour installer et test mon jeu, rien de plus simple : 

Clone le repo avec la commande suivante
```
git clone https://github.com/Lumosity23/Blue_tower.git
```

### Installer UV si vous ne l'avez pas ( c'est un packages manager comme pip mais en mieux )

#### pour linux :
```
sudo apt install uv
```

#### pour windows :
```
winget install uv
```

#### ensuite utiliser uv pour sync votre clonage pour avoir le meme environemnt que moi :
```
uv sync
```

#### pour finir pour lancer le jeu executer simplement la commande suivante :
```
uv run src/main.py
```

## Appropos de moi

Je suis un dev junior, j'apprend la programation depuis maintenant `3 mois`, j'essaye de faire ce qui me passe par la tete tout en ecoutant les retours de mes amis sur mon projet.

## [CREDITS](CREDITS.md)