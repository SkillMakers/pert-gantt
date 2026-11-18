"""Les deux projets de la video : le petit exemple du cours et l'exercice corrige."""
from pert import Tache, projet

# Cours : mettre en ligne une page « soldes » sur la boutique
COURS = projet(
    Tache("A", "Maquette de la page", 2),
    Tache("B", "Coder la page", 4, ("A",)),
    Tache("C", "Ecrire les textes", 3, ("A",)),
    Tache("D", "Tester la page", 1, ("B",)),
    Tache("E", "Mettre en ligne", 1, ("C", "D")),
)

# Reseau PERT du cours : etapes 1 a 5, aucune tache fictive
RESEAU_COURS = [(1, 2, "A"), (2, 3, "B"), (2, 4, "C"), (3, 4, "D"), (4, 5, "E")]

# Exercice : lancer la boutique en ligne
EXERCICE = projet(
    Tache("A", "Rediger le cahier des charges", 3),
    Tache("B", "Concevoir la base de donnees", 4, ("A",)),
    Tache("C", "Dessiner les maquettes", 3, ("A",)),
    Tache("D", "Developper le back-end", 10, ("B",)),
    Tache("E", "Developper le front-end", 6, ("C",)),
    Tache("F", "Configurer l'hebergement", 2, ("A",)),
    Tache("G", "Rediger les fiches produits", 7, ("A",)),
    Tache("H", "Tests d'integration", 4, ("D", "E")),
    Tache("I", "Mise en ligne", 1, ("F", "G", "H")),
)

# Reseau PERT du corrige : F et G vont toutes deux de l'etape 2 a l'etape du debut de I,
# d'ou une etape 6 et une tache fictive de 6 a 7
RESEAU_EXERCICE = [
    (1, 2, "A"),
    (2, 3, "B"), (2, 4, "C"), (2, 6, "F"), (2, 7, "G"),
    (3, 5, "D"), (4, 5, "E"),
    (5, 7, "H"),
    (6, 7, None),  # tache fictive
    (7, 8, "I"),
]

# L'erreur classique : F et G dessinees toutes les deux de 2 a 7, sans tache fictive
RESEAU_EXERCICE_FAUX = [
    (1, 2, "A"),
    (2, 3, "B"), (2, 4, "C"), (2, 7, "F"), (2, 7, "G"),
    (3, 5, "D"), (4, 5, "E"),
    (5, 7, "H"),
    (7, 8, "I"),
]
