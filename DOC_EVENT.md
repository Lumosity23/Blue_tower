# 📋 Documentation des Événements

> **Généré automatiquement** - Dernière mise à jour : 2026-02-06 23:02

## 📌 Table des matières
- [Introduction](#introduction)
- [Liste des événements](#liste-des-événements)

---

## Introduction

Cette documentation référence tous les événements utilisés dans le système `eventManager`.

### Convention de nommage
- Les événements suivent le format `SNAKE_CASE`
- Les types Python sont annotés avec la syntaxe moderne (PEP 484)

### Syntaxe utilisée
| Symbole | Signification |
|---------|---------------|
| `*` | Paramètre obligatoire |
| `?` | Paramètre optionnel |
| `→` | Retour de fonction |

---

## Liste des événements


### 1. `ENEMY_KILLED`

**Signature :** `ENEMY_KILLED(int)` → `None`

**Description :** L'événement `ENEMY_KILLED` prend un argument de type `int` qui represente le type de l'ennemi tue.

> **Détails :** permet de d'activer les fonctions lies a la mort d'un ennemi

📁 *Fichier concerné :* `settings.py`

#### 🎯 Souscription

Pour écouter cet événement :

```python
# Méthode de callback (doit accepter le type int)
def on_enemy_killed(enemy_type: int):
    """Gestionnaire pour ENEMY_KILLED."""
    print(f"Event reçu: {enemy_type}")

# Souscription
self.game.eventManager.subscribe("ENEMY_KILLED", on_enemy_killed)
```
⚠️ **Important :** La méthode callback doit impérativement accepter un paramètre de type `int`.

#### 📢 Publication

Pour déclencher cet événement (represente le type de l'ennemi tue) :

```python
# Quand l'événement se produit
enemy_type = ...  # Represente le type de l'ennemi tue
self.game.eventManager.publish("ENEMY_KILLED", enemy_type)
```
#### 📝 Notes de type

- **Type attendu :** `int`
- **Valeurs possibles :** Nombres entiers

---

### 2. `ERROR_SOUND`

**Type :** 🔔 Signal pur (aucune donnée)

**Description :** Declencher lors qu'une erreur est apparus lors de l'execution d'une fonction et que toute les condition ne sont pas respecter.
Que pour de element du UI, qui sont diretemtn lier avec le user

📁 **Source :** `SoundManager.py`

#### 🎯 Souscription

```python
# Le callback ne prend aucun argument
def on_error_sound():
    """Gestionnaire pour ERROR_SOUND."""
    print("Signal ERROR_SOUND reçu !")

# Souscription
self.game.eventManager.subscribe("ERROR_SOUND", on_error_sound)
```
#### 📢 Publication

```python
# Déclenchement du signal
self.game.eventManager.publish("ERROR_SOUND")  # Aucun argument !
```
#### 💡 Notes

ATTENTION --> a ne pas utiliser a tout bout de champs

---

### 3. `ERROR_PAYMENT`

**Type :** 🔔 Signal pur (aucune donnée)

**Description :** Lors d'une transaction pour poser de mur ou pour de action qui ne requiet pas de UI en particuler juste le terrain de jeu

📁 **Source :** `wallet.py et SoundManager.py`

#### 🎯 Souscription

```python
# Le callback ne prend aucun argument
def on_error_payment():
    """Gestionnaire pour ERROR_PAYMENT."""
    print("Signal ERROR_PAYMENT reçu !")

# Souscription
self.game.eventManager.subscribe("ERROR_PAYMENT", on_error_payment)
```
#### 📢 Publication

```python
# Déclenchement du signal
self.game.eventManager.publish("ERROR_PAYMENT")  # Aucun argument !
```
---
