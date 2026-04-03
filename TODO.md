# TODO

Ici vous retrouverez toutes les choses a faire dans mon jeu

## UI and DESIGNE

Pour que le jeu soit un minimum beau, il faut absolument trouver une DA !!!.

- [ ] Trouver un DA
  - [ ] Faire quelque sprite ou tile avec
  - [ ] Designer un bouton universel pour l'implementer au jeu
  - [ ] Faire l'OSD pour enfin avoir un ecran de jeu propre



## Chunk LOGIC

La mecanique des chunk est hyper important pour la stabiliter du jeu et avoir un bon Culling et eviter les drop FPS

- [ ] Faire en sorte que toutes les entites soit bien retirer de ces derniers si morts ou hors de la map
  


## API EVENT

Les Appel API, sont super important car il permet d'avoir une structure propre et reutilisable

- [ ] Cree un NotificationManager
  - [ ] permetre de faire apparaitre des message de debug ou d'info en generale


## SFX and MUSIC

Pour donner vie a son jeu et ses personnage la MUSIC est indispensable ( MERCIIIII A AMINE POUR CA !).

- [ ] Trouver des sounds effects pour les batiment
  - [ ] la bank
  - [ ] la tourelle
  - [ ] le kernel (base)



## UPGRADE system

La base de mon jeu repose sur les upgrade ( pour l'instant inexistant )

- [ ] Cree un bouton upgrade dans le info panel
  - [ ] qu'il soit clickable et ouvrel le UpgradePanel
  - [ ] Affiche les stats actuele de l'entite selectionner

- [ ] Cree un system minimal d'upgrade des perfs du joueur
- [ ] idem pour la tourelle et le kernel


## InfoPanel

c'est un element essentiel, mais si peu attentdu par les joueur dans un premier temps

- [ ] Ajouter un bouton Upgrade et Sell en bas de ce dernier


# BACKLOG

- [ ] Regler le soucis de la taille des ennemis --> trop grand == pas attirer par la base\
        - pour l'instant laisse de cote avec juste un taille endessous de la taille max



# DONE

- [x] System de l'info panel dynamique
- [x] Destruction de batiement par les ennemis

- [x] Cree un VFXManager
  - [x] Cree un endPoint pour l'affichage de text instantane
  - [x] ajouter une animation de monter et fondu