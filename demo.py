"""Le cours et l'exercice de la video, executes.

    python demo.py
"""
from enonces import COURS, EXERCICE, RESEAU_COURS, RESEAU_EXERCICE, RESEAU_EXERCICE_FAUX
from pert import (chemins_critiques, dates, dates_des_etapes, fin_avec_retards, gantt, niveaux,
                  plus_long_chemin_brut, tableau, verifier_reseau)


def titre(t):
    print()
    print("=" * 76)
    print(t)
    print("=" * 76)


def resoudre(nom, p, reseau):
    titre(f"{nom} - enonce")
    for t in p.values():
        print(f"  {t.nom}  {t.libelle:<32} {t.duree:>2} j   avant : {', '.join(t.avant) or '-'}")

    titre(f"{nom} - niveaux")
    r = niveaux(p)
    for k in sorted(set(r.values())):
        print(f"  niveau {k} : {', '.join(n for n in sorted(p) if r[n] == k)}")

    titre(f"{nom} - dates, marges (MT = marge totale, ML = marge libre)")
    print(tableau(p))
    print(f"  chemin critique : {' - '.join(chemins_critiques(p)[0])}")
    print(f"  juge (plus long chemin, en essayant tous les chemins) : {plus_long_chemin_brut(p)} jours")

    titre(f"{nom} - reseau PERT (taches sur les fleches)")
    defauts = verifier_reseau(p, reseau)
    print("  reseau juste" if not defauts else "\n".join("  " + x for x in defauts))
    tot, tard = dates_des_etapes(p, reseau)
    for e in sorted(tot):
        print(f"  etape {e} : au plus tot {tot[e]:>2}, au plus tard {tard[e]:>2}")
    for a, b, n in reseau:
        print(f"    {a} -> {b}  {n or 'tache fictive (duree 0)'}")

    titre(f"{nom} - Gantt au plus tot (# critique, = tache, . marge libre, - reste de la marge totale)")
    print(gantt(p))


def piege():
    p = EXERCICE
    d, duree = dates(p)
    titre("Le piege - chaque tache reste dans sa marge totale")
    print(f"  C : marge totale {d['C']['mt']}, marge libre {d['C']['ml']}")
    print(f"  E : marge totale {d['E']['mt']}, marge libre {d['E']['ml']}")
    cas = [({"C": 1}, "C prend 1 jour de retard"),
           ({"E": 5}, "E prend 5 jours de retard (sa marge libre)"),
           ({"C": 5}, "C prend 5 jours de retard (sa marge totale)"),
           ({"C": 5, "E": 5}, "C ET E prennent chacune 5 jours (chacune dans sa marge totale)")]
    for retards, phrase in cas:
        fin, debuts = fin_avec_retards(p, retards)
        bouge = [f"{n} {d[n]['tot']} -> {debuts[n]}" for n in sorted(p)
                 if debuts[n] != d[n]["tot"]]
        print(f"  {phrase} : projet {duree} -> {fin} jours ; debuts decales : {', '.join(bouge) or 'aucun'}")
    print()
    print(gantt(p, {"C": 5, "E": 5}))

    titre("L'erreur classique du reseau PERT - F et G sur la meme fleche de 2 a 7")
    for x in verifier_reseau(p, RESEAU_EXERCICE_FAUX):
        print("  " + x)


if __name__ == "__main__":
    resoudre("COURS", COURS, RESEAU_COURS)
    resoudre("EXERCICE", EXERCICE, RESEAU_EXERCICE)
    piege()
