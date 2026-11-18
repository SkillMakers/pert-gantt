# Méthode PERT et diagramme de Gantt : cours et exercice corrigé

Code de la vidéo [**Méthode PERT et diagramme de Gantt : cours et exercice corrigé**](https://youtu.be/NyxC21i8ZIU) de la chaîne
[IT Skills Maker](https://www.youtube.com/@ItSkillsMaker).

Le programme refait le corrigé **comme sur une copie** : niveaux, dates au plus tôt (le maximum des prédécesseurs),
dates au plus tard (le minimum des successeurs), marges totale et libre, chemin critique, réseau PERT avec sa tâche
fictive, et diagramme de Gantt. Les tests comparent ensuite ces calculs à un juge qui **écrit un par un tous les chemins complets** du
projet, sur 300 projets tirés au hasard, et vérifient la définition des marges en retardant chaque tâche.

## Lancer

Python 3.11 ou plus, aucune dépendance.

```
python demo.py           # le cours, l'exercice, et le piège des deux marges
python -m unittest -v    # les 20 tests
```

Les sorties obtenues pour la vidéo sont dans [`preuves/`](preuves/) : `demo.txt` (Python 3.15.1) et `tests.txt`
(20 tests verts sous 3.15.1 et 3.11).

## L'exercice : lancer la boutique en ligne

| Tâche | Libellé | Durée (jours) | Antériorités |
|---|---|---|---|
| A | Rédiger le cahier des charges | 3 | — |
| B | Concevoir la base de données | 4 | A |
| C | Dessiner les maquettes | 3 | A |
| D | Développer le back-end | 10 | B |
| E | Développer le front-end | 6 | C |
| F | Configurer l'hébergement | 2 | A |
| G | Rédiger les fiches produits | 7 | A |
| H | Tests d'intégration | 4 | D, E |
| I | Mise en ligne | 1 | F, G, H |

## Le corrigé

| Tâche | Début au plus tôt | Fin au plus tôt | Début au plus tard | Fin au plus tard | Marge totale | Marge libre |
|---|---|---|---|---|---|---|
| A | 0 | 3 | 0 | 3 | 0 | 0 |
| B | 3 | 7 | 3 | 7 | 0 | 0 |
| C | 3 | 6 | 8 | 11 | 5 | **0** |
| D | 7 | 17 | 7 | 17 | 0 | 0 |
| E | 6 | 12 | 11 | 17 | 5 | 5 |
| F | 3 | 5 | 19 | 21 | 16 | 16 |
| G | 3 | 10 | 14 | 21 | 11 | 11 |
| H | 17 | 21 | 17 | 21 | 0 | 0 |
| I | 21 | 22 | 21 | 22 | 0 | 0 |

Durée du projet : **22 jours**. Chemin critique : **A - B - D - H - I** (3 + 4 + 10 + 4 + 1).
Réseau PERT : F et G vont toutes deux de l'étape 2 au début de I, d'où **une tâche fictive** (durée 0).

**Le piège** : C et E ont chacune 5 jours de marge totale. Chacune prend 5 jours de retard, chacune « dans sa marge » :
le projet passe de 22 à **27 jours**. La marge totale de C suppose que E démarre le plus tard possible, et celle de E
suppose que C finit au plus tôt : elles ne s'additionnent pas. Seule la marge libre (0 pour C, 5 pour E) se consomme
sans décaler personne.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `pert.py` | niveaux, dates, marges, chemin critique, juge par énumération, vérification d'un réseau PERT, Gantt en texte |
| `enonces.py` | le petit exemple du cours et l'exercice, avec leurs réseaux PERT (et le réseau faux, sans tâche fictive) |
| `demo.py` | le cours et l'exercice, exécutés |
| `test_pert.py` | chaque chiffre de la vidéo, et le calcul contre le juge sur des projets au hasard |

## Ce que le programme simplifie

- Les durées sont certaines (pas d'estimation optimiste / probable / pessimiste du PERT probabiliste).
- Les antériorités sont toutes de type « fin avant début », sans délai ni chevauchement.
- Les dates sont en jours depuis le début du projet (date 0), sans calendrier ni week-ends.
