import collections # Pour la queue rapide (deque)
import random

#### Parametre du code ####
cols = 30
rows = 30
wall = '#'
empty = 0 # On utilise 0 pour dire "vide/non visité"
target = (3, 7)

# Grille initialisée proprement (List Comprehension)
# On met des 0 partout
grid = [[empty for _ in range(rows)] for _ in range(cols)]

directions = [
    (1, 0), (-1, 0), (0, 1), (0, -1)
]

#### Fonctions ####

def addWall(numWall) -> None:
    count = 0
    while count < numWall:
        x = random.randint(0, cols - 1)
        y = random.randint(0, rows - 1)
        # On évite d'écraser la cible ou un mur existant
        if (x, y) != target and grid[x][y] != wall:
            grid[x][y] = wall
            count += 1

def showGrid():
    print("---------- GRID -----------")
    # Petite astuce d'affichage pour voir la grille dans le bon sens (transposée visuelle)
    # car grid[x][y] stocke par colonne en premier
    for y in range(rows):
        line = []
        for x in range(cols):
            val = grid[x][y]
            # Formattage pour aligner les chiffres (pour que ce soit joli)
            line.append(f"{str(val):>2}") 
        print(line)
    print('----------------------------')

def getValidNeighbors(posX, posY):
    validNeighbors = []
    for dx, dy in directions:
        newX = posX + dx
        newY = posY + dy

        # 1. Check Limites
        if 0 <= newX < cols and 0 <= newY < rows:
            # 2. Check Mur
            if grid[newX][newY] != wall:
                validNeighbors.append((newX, newY))
    return validNeighbors

#### CODE PRINCIPAL (BFS) ####

def main() -> None:
    addWall(15) # Ajoutons un peu plus de murs pour le test

    print("--- AVANT ---")
    showGrid()

    # 1. Utilisation de DEQUE pour la performance
    queue = collections.deque()
    
    # 2. Init de la cible
    tx, ty = target
    grid[tx][ty] = 0 # Distance 0
    queue.append(target)
    
    # Pour ne pas repasser sur des cases déjà faites, on peut utiliser un set 'visited'
    # OU mieux : regarder si la case a déjà une valeur > 0 (ou différente de 'empty')
    # Ici, pour être sûr, utilisons un set, c'est plus propre conceptuellement.
    visited = set()
    visited.add(target)

    # Debut du pipeline
    while queue:
        # OPTIMISATION 1 : popleft() est instantané
        current_x, current_y = queue.popleft() 
        current_dist = grid[current_x][current_y]

        for n_x, n_y in getValidNeighbors(current_x, current_y):
            
            # OPTIMISATION 2 : On vérifie TOUT DE SUITE si on doit l'ajouter
            if (n_x, n_y) not in visited:
                
                # On calcule la distance
                grid[n_x][n_y] = current_dist + 1
                
                # On marque comme visité IMMÉDIATEMENT (pour que les autres ne l'ajoutent pas)
                visited.add((n_x, n_y))
                
                # On ajoute à la file
                queue.append((n_x, n_y))
    
    print(f"\n--- APRÈS (Cible en {target}) ---")
    showGrid()

if __name__ == '__main__':
    main()