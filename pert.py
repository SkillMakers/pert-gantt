"""Ordonnancement d'un projet : niveaux, dates au plus tot et au plus tard, marges, chemin critique,
reseau PERT (taches sur les fleches) et diagramme de Gantt.

Les dates sont comptees en jours depuis le debut du projet : une tache qui commence a la date 3 commence
apres le 3e jour. Une tache de duree 4 qui commence a 3 finit a 7.
"""
from collections import Counter
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Tache:
    nom: str
    libelle: str
    duree: int
    avant: tuple = ()  # les taches qui doivent etre finies avant (anteriorites)


def projet(*taches):
    """Range les taches par nom et verifie l'enonce : noms uniques, durees positives, anteriorites connues et
    sans doublon, pas de cycle."""
    doubles = sorted(n for n, k in Counter(t.nom for t in taches).items() if k > 1)
    if doubles:
        raise ValueError(f"deux taches portent le meme nom : {', '.join(doubles)}")
    p = {t.nom: t for t in taches}
    for t in taches:
        if t.duree < 0:
            raise ValueError(f"{t.nom} a une duree negative")
        if len(set(t.avant)) != len(t.avant):
            raise ValueError(f"{t.nom} cite deux fois la meme anteriorite")
        for a in t.avant:
            if a not in p:
                raise ValueError(f"{t.nom} depend de {a}, qui n'existe pas")
    niveaux(p)  # leve une erreur s'il y a un cycle
    return p


def successeurs(p):
    succ = {n: [] for n in p}
    for t in p.values():
        for a in t.avant:
            succ[a].append(t.nom)
    return succ


def niveaux(p):
    """Niveau d'une tache = longueur du plus long enchainement d'anteriorites qui y mene.

    C'est la methode de la copie : niveau 0 = les taches sans anteriorite ; on les raye, et celles qui n'ont
    plus d'anteriorite forment le niveau suivant.
    """
    restantes = dict(p)
    rangs, niveau = {}, 0
    while restantes:
        libres = sorted(n for n, t in restantes.items() if all(a in rangs for a in t.avant))
        if not libres:
            raise ValueError(f"cycle dans les anteriorites : {sorted(restantes)}")
        for n in libres:
            rangs[n] = niveau
            del restantes[n]
        niveau += 1
    return rangs


def ordre(p):
    """Les taches niveau par niveau : l'ordre dans lequel on remplit le tableau."""
    r = niveaux(p)
    return sorted(p, key=lambda n: (r[n], n))


def dates(p):
    """Dates au plus tot (de gauche a droite, le MAX des predecesseurs) puis au plus tard (de droite a
    gauche, le MIN des successeurs), marges totale et libre.

    Renvoie un dict nom -> dict(tot, fin_tot, tard, fin_tard, mt, ml), et la duree du projet.
    """
    succ = successeurs(p)
    tot, fin_tot = {}, {}
    for n in ordre(p):
        tot[n] = max((fin_tot[a] for a in p[n].avant), default=0)
        fin_tot[n] = tot[n] + p[n].duree
    duree = max(fin_tot.values(), default=0)

    tard, fin_tard = {}, {}
    for n in reversed(ordre(p)):
        fin_tard[n] = min((tard[s] for s in succ[n]), default=duree)
        tard[n] = fin_tard[n] - p[n].duree

    res = {}
    for n in p:
        # marge libre : ce qu'on peut retarder sans decaler le debut au plus tot d'aucun successeur
        debut_succ = min((tot[s] for s in succ[n]), default=duree)
        res[n] = dict(tot=tot[n], fin_tot=fin_tot[n], tard=tard[n], fin_tard=fin_tard[n],
                      mt=tard[n] - tot[n], ml=debut_succ - fin_tot[n])
    return res, duree


def chemins_critiques(p):
    """Tous les chemins du debut a la fin formes de taches a marge totale nulle, enchainees sans trou."""
    d, _ = dates(p)
    succ = successeurs(p)
    crit = {n for n in p if d[n]["mt"] == 0}
    departs = sorted(n for n in crit if not p[n].avant)
    chemins = []

    def suivre(chemin):
        n = chemin[-1]
        suite = [s for s in succ[n] if s in crit and d[s]["tot"] == d[n]["fin_tot"]]
        if not succ[n]:
            chemins.append(chemin)
        for s in sorted(suite):
            suivre(chemin + [s])

    for n in departs:
        suivre([n])
    return chemins


def fin_avec_retards(p, retards):
    """Duree du projet si chaque tache demarre au plus tot puis prend `retards[nom]` jours de retard.

    Retarder une tache revient, pour la suite, a allonger sa duree : c'est ce que fait ce calcul.
    Renvoie (duree du projet, debuts au plus tot recalcules).
    """
    q = {n: Tache(t.nom, t.libelle, t.duree + retards.get(n, 0), t.avant) for n, t in p.items()}
    d, duree = dates(q)
    return duree, {n: d[n]["tot"] for n in p}


# --- Juge independant : on ecrit TOUS les chemins, puis on additionne ---------------------------------
# Rien ici ne reutilise successeurs() ni la formule du max : on liste les chemins comme sur une copie.

def tous_les_chemins(p):
    """Chaque chemin complet, d'une tache sans anteriorite a une tache que personne n'attend."""
    attendues = {a for t in p.values() for a in t.avant}
    fins = [n for n in p if n not in attendues]

    def vers(n):  # tous les chemins qui finissent par n
        if not p[n].avant:
            return [[n]]
        return [c + [n] for a in p[n].avant for c in vers(a)]

    return [c for n in fins for c in vers(n)]


def plus_long_chemin_brut(p):
    """Duree du projet = la somme des durees du plus long des chemins complets."""
    return max((sum(p[n].duree for n in c) for c in tous_les_chemins(p)), default=0)


def tot_brut(p, n):
    """Debut au plus tot de n = la duree du plus long chemin qui s'arrete juste avant n."""
    avant_n = [c[:c.index(n)] for c in tous_les_chemins(p) if n in c]
    return max((sum(p[m].duree for m in c) for c in avant_n), default=0)


# --- Reseau PERT : taches sur les fleches, etapes dans les cercles ---------------------------------------

def verifier_reseau(p, fleches):
    """Juge un reseau PERT dessine a la main.

    `fleches` : liste de (etape_depart, etape_arrivee, nom) ; nom = None pour une tache fictive (duree 0).
    Verifie que chaque tache apparait une fois, que deux fleches ne relient pas les memes etapes, que le
    reseau n'a pas de cycle, et qu'il impose EXACTEMENT les anteriorites de l'enonce (ni plus, ni moins).
    Renvoie la liste des defauts (vide si le reseau est juste).
    """
    defauts = []
    noms = [n for _, _, n in fleches if n is not None]
    for n in sorted(set(p) - set(noms)):
        defauts.append(f"la tache {n} manque")
    for n in sorted(set(noms) - set(p)):
        defauts.append(f"la tache {n} n'est pas dans l'enonce")
    for n, k in sorted(Counter(noms).items()):
        if k > 1:
            defauts.append(f"la tache {n} apparait deux fois")
    for ab, k in sorted(Counter((a, b) for a, b, _ in fleches).items()):
        if k > 1:
            defauts.append(f"deux fleches relient les etapes {ab[0]} et {ab[1]} : il faut une tache fictive")
    if defauts:
        return defauts

    etapes = sorted({e for a, b, _ in fleches for e in (a, b)})
    sortantes = {e: [b for a, b, _ in fleches if a == e] for e in etapes}
    debuts = [e for e in etapes if not any(b == e for _, b, _ in fleches)]
    fins = [e for e in etapes if not sortantes[e]]
    if len(debuts) != 1:
        defauts.append(f"le reseau doit avoir une seule etape de debut, il en a {len(debuts)} : {debuts}")
    if len(fins) != 1:
        defauts.append(f"le reseau doit avoir une seule etape de fin, il en a {len(fins)} : {fins}")
    if defauts:
        return defauts

    atteint = {}
    for e in etapes:  # parcours en largeur depuis chaque etape, une seule fois
        vus, file = set(), list(sortantes[e])
        while file:
            b = file.pop()
            if b not in vus:
                vus.add(b)
                file.extend(sortantes[b])
        atteint[e] = vus
    for e in etapes:
        if e in atteint[e]:
            return [f"le reseau a un cycle qui passe par l'etape {e}"]

    def atteignables(e):
        return atteint[e]

    fin_de = {n: b for a, b, n in fleches if n is not None}
    debut_de = {n: a for a, b, n in fleches if n is not None}

    def precede(x, y):  # dans le reseau, x doit etre finie avant que y commence
        return debut_de[y] == fin_de[x] or debut_de[y] in atteignables(fin_de[x])

    # anteriorites voulues, fermees par transitivite (si A avant B et B avant D, alors A avant D)
    voulu = {n: set() for n in p}
    for n in ordre(p):
        for a in p[n].avant:
            voulu[n] |= {a} | voulu[a]
    for x, y in product(sorted(p), repeat=2):
        if x == y:
            continue
        if precede(x, y) and x not in voulu[y]:
            defauts.append(f"le reseau impose {x} avant {y}, ce que l'enonce ne demande pas")
        if not precede(x, y) and x in voulu[y]:
            defauts.append(f"l'enonce impose {x} avant {y}, ce que le reseau oublie")
    return defauts


def dates_des_etapes(p, fleches):
    """Date au plus tot et au plus tard de chaque etape du reseau PERT (cercle coupe en deux sur la copie).

    Le reseau doit d'abord etre juste (`verifier_reseau`), sinon les dates n'ont pas de sens.
    """
    defauts = verifier_reseau(p, fleches) if fleches else ["le reseau est vide"]
    if defauts:
        raise ValueError("reseau faux : " + " ; ".join(defauts))
    duree = {n: (p[n].duree if n is not None else 0) for _, _, n in fleches}
    etapes = sorted({e for a, b, _ in fleches for e in (a, b)})
    tot = {e: 0 for e in etapes}
    for _ in etapes:  # relaxations successives : assez pour un reseau sans cycle
        for a, b, n in fleches:
            tot[b] = max(tot[b], tot[a] + duree[n])
    fin = max(tot.values())
    tard = {e: fin for e in etapes}
    for _ in etapes:
        for a, b, n in fleches:
            tard[a] = min(tard[a], tard[b] - duree[n])
    return tot, tard


# --- Affichage ------------------------------------------------------------------------------------------

def tableau(p):
    d, duree = dates(p)
    r = niveaux(p)
    lignes = ["tache  duree  avant    niveau  tot  fin_tot  tard  fin_tard  MT  ML"]
    for n in ordre(p):
        t, x = p[n], d[n]
        lignes.append(f"  {n:<4} {t.duree:>5}  {','.join(t.avant) or '-':<8} {r[n]:>5} {x['tot']:>5}"
                      f" {x['fin_tot']:>8} {x['tard']:>5} {x['fin_tard']:>9} {x['mt']:>3} {x['ml']:>3}")
    lignes.append(f"duree du projet : {duree} jours")
    return "\n".join(lignes)


def gantt(p, retards=None):
    """Gantt au plus tot, en texte : # critique, = tache, . marge libre, - reste de la marge totale."""
    retards = retards or {}
    duree, debuts = fin_avec_retards(p, retards)
    d, _ = dates(p)
    largeur = max(3, *(len(n) for n in p))
    marge = " " * (largeur + 3)
    dizaines = [" "] * (duree + 1)
    for j in range(0, duree + 1, 10):  # 10, 20... 100 : le nombre entier, s'il tient avant le repere suivant
        for k, c in enumerate(str(j // 10)):
            if j + k <= duree:
                dizaines[j + k] = c
    lignes = [marge + "".join(dizaines), marge + "".join(str(j % 10) for j in range(duree + 1))]
    for n in ordre(p):
        dur = p[n].duree + retards.get(n, 0)
        signe = "#" if d[n]["mt"] == 0 and not retards else "="
        barre = " " * debuts[n] + signe * dur
        if not retards:
            barre += "." * d[n]["ml"] + "-" * (d[n]["mt"] - d[n]["ml"])
        lignes.append(f"  {n:<{largeur}} {barre}")
    return "\n".join(lignes)
