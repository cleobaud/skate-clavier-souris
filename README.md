# skate. (Skate 4) au clavier et à la souris

Jouer à **skate.** d'EA sur PC avec un clavier et une souris : le script transforme ton clavier et ta souris en
**manette Xbox virtuelle**, la seule chose que le jeu accepte en partie. La souris fait le stick droit, donc le
**Flick-It** (les tricks).

> ⚠️ **À lire avant d'installer**
> - Projet **non officiel**, sans lien avec Electronic Arts ni Full Circle. *skate.* est une marque d'Electronic Arts.
> - EA indique que le clavier/souris **n'est pas pris en charge** en partie (« only controller inputs can be used
>   for gameplay »). Ce script ne modifie aucun fichier du jeu, n'injecte rien et n'utilise pas Internet : il crée
>   seulement une manette virtuelle. **Mais c'est un logiciel tiers** : des joueurs rapportent que l'anti-triche du jeu
>   bloque déjà un outil de la même famille (reWASD). **Une sanction de ton compte EA n'est pas exclue.**
>   Tu l'utilises **à tes risques**.

## Installation (une seule fois)

1. Installe **Python 3** depuis [python.org](https://www.python.org/downloads/) en cochant **« Add python.exe to PATH »**.
2. Télécharge ce dépôt (bouton vert **Code → Download ZIP**) et décompresse-le.
3. Double-clique sur **`JOUER.bat`**. Au premier lancement, il installe la bibliothèque `vgamepad` puis vérifie la
   manette virtuelle. S'il manque le pilote **ViGEmBus**, il ouvre sa page officielle : installe
   `ViGEmBus_1.22.0_x64_x86_arm64.exe`, **redémarre le PC**, puis relance `JOUER.bat`.

## Jouer

1. Lance `JOUER.bat` : la fenêtre affiche les touches, puis **EN PAUSE**.
2. Lance skate., mets-toi en jeu, appuie sur **`F11`** : le curseur se fige, la souris pilote le stick droit.
3. **`F11`** (ou `Alt` droit) met en pause et te rend la souris. **`F12`** (ou `Ctrl` droit) quitte.

Dans le jeu, choisis le préréglage **Classic** (Options → Contrôles).

## Les touches

Pensé pour un clavier **QWERTY 60 %** : main gauche sur `WASD`, main droite sur la souris, aucune touche de la rangée
F ni flèche en pleine partie. Le script vérifie à chaque démarrage qu'aucune touche ne sert deux fois.

| Manette | Touche | Dans skate. |
|---|---|---|
| Stick gauche | `W` `A` `S` `D` | diriger |
| **Stick droit** | **la souris** | **tricks (Flick-It)** |
| L3 | `Maj` gauche | sprint à pied |
| R3 | `V` | |
| A | `Espace` | pousser, pied 1 |
| X | `E` | pousser, pied 2 |
| B | `C` | freiner / sortir d'un grind |
| Y | `R` | monter / descendre de la planche |
| LB | `Q` | |
| RB | `F` | handplant |
| LT | clic droit (ou `Ctrl` gauche) | grab |
| RT | clic gauche | grab |
| Croix haut / bas | `T` / `G` | caméra |
| Croix gauche / droite | `Z` / `X` | |
| Start | `Entrée` | menu pause |
| Back | `Tab` | carte |
| Guide | `B` | |

> Sur un clavier **AZERTY** : le script lit les **lettres**, pas les positions. Le plus simple est de passer Windows
> en disposition **QWERTY** le temps de jouer (`Alt` + `Maj` pour basculer) : tu retrouves `WASD` sous la main gauche.

## Régler la souris

- **En jeu** (le plus efficace) : Options → Contrôles → **Flick-It Sensitivity**.
- **Pendant la partie**, script actif : **`1`** = souris moins vive, **`2`** = plus vive. Le réglage est retenu
  (`reglages.txt`, créé à côté du script).
- Réglages du jeu qui aident : *Grind Assist Amount*, *Flip Trick Catch Assist*, *Streamlined Flick-It Tricks*,
  *Auto Curb Pop*.

## Désinstaller

Supprime le dossier, puis Paramètres Windows → Applications → **ViGEm Bus Driver** → Désinstaller.

## Fichiers

| Fichier | Rôle |
|---|---|
| `JOUER.bat` | vérifie Python, la bibliothèque et le pilote, puis lance le script |
| `skate_kbm.py` | le pont clavier/souris → manette Xbox virtuelle (souris lue en Raw Input, curseur figé sans clignotement) |
| `verifier_manette.py` | crée une manette, vérifie que Windows la voit en XInput et qu'un appui sur A passe |
| `requirements.txt` | `vgamepad` |

## Merci

- [jasperdevs/skate-kbm](https://github.com/jasperdevs/skate-kbm) (MIT) : l'idée de lire la souris en Raw Input et
  le placement des grabs sur les gâchettes.
- [vgamepad](https://github.com/yannbouteiller/vgamepad) (MIT) et [ViGEmBus](https://github.com/nefarius/ViGEmBus)
  (BSD-3-Clause, Nefarius Software Solutions) : la manette virtuelle.

Licence : MIT (voir `LICENSE`).

---

## English (short)

Play EA's **skate.** on PC with keyboard and mouse: the script turns them into a **virtual Xbox controller**
(mouse = right stick = Flick-It). **Unofficial**, not affiliated with EA. EA does not support keyboard/mouse for
gameplay; this is third-party software and players report the anti-cheat already blocks a similar tool (reWASD):
**your EA account could be sanctioned. Use at your own risk.** Install Python 3 (add to PATH), download this repo,
double-click `JOUER.bat` (installs `vgamepad`, checks the ViGEmBus driver and opens its official page if missing),
then in game press `F11` to start, `F12` to quit, `1`/`2` to change mouse sensitivity.
