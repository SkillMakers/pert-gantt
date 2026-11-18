"""Tests : chaque chiffre cite dans la video, puis le calcul compare a un juge qui ecrit tous les chemins
complets, sur des projets tires au hasard.

    python -m unittest -v
"""
import random
import unittest

from enonces import COURS, EXERCICE, RESEAU_COURS, RESEAU_EXERCICE, RESEAU_EXERCICE_FAUX
from pert import (Tache, chemins_critiques, dates, dates_des_etapes, fin_avec_retards, gantt, niveaux,
                  plus_long_chemin_brut, projet, successeurs, tot_brut, verifier_reseau)


def projet_au_hasard(graine, n=9):
    """Un projet de n taches : chaque tache depend de 0 a 3 taches tirees parmi les precedentes."""
    rnd = random.Random(graine)
    taches = []
    for i in range(n):
        nom = f"T{i}"
        avant = tuple(rnd.sample([t.nom for t in taches], k=min(len(taches), rnd.randint(0, 3))))
        taches.append(Tache(nom, nom, rnd.randint(1, 9), avant))
    return projet(*taches)


class TestCours(unittest.TestCase):

    def test_dates_et_marges_du_cours(self):
        """Petit exemple : 8 jours, C a 2 jours de marge, chemin critique A - B - D - E."""
        # GIVEN
        p = COURS
        # WHEN
        d, duree = dates(p)
        # THEN
        self.assertEqual(duree, 8)
        self.assertEqual((d["C"]["tot"], d["C"]["fin_tot"], d["C"]["tard"], d["C"]["fin_tard"]), (2, 5, 4, 7))
        self.assertEqual((d["C"]["mt"], d["C"]["ml"]), (2, 2))
        self.assertEqual(d["E"]["tot"], 7)  # le MAX de 5 (C) et 7 (D)
        self.assertEqual(chemins_critiques(p), [["A", "B", "D", "E"]])

    def test_reseau_du_cours(self):
        """Le reseau PERT du cours est juste et ses etapes portent les memes dates."""
        # GIVEN
        p, reseau = COURS, RESEAU_COURS
        # WHEN
        defauts = verifier_reseau(p, reseau)
        tot, tard = dates_des_etapes(p, reseau)
        # THEN
        self.assertEqual(defauts, [])
        self.assertEqual(tot, {1: 0, 2: 2, 3: 6, 4: 7, 5: 8})
        self.assertEqual(tard, tot)  # toutes les etapes du cours sont sur le chemin critique


class TestExercice(unittest.TestCase):

    def test_niveaux(self):
        """Niveaux 0 : A ; 1 : B C F G ; 2 : D E ; 3 : H ; 4 : I."""
        # GIVEN
        p = EXERCICE
        # WHEN
        r = niveaux(p)
        # THEN
        self.assertEqual(r, dict(A=0, B=1, C=1, F=1, G=1, D=2, E=2, H=3, I=4))

    def test_tableau_complet(self):
        """Les dates et marges du corrige, ligne par ligne."""
        # GIVEN
        attendu = {  # tot, fin_tot, tard, fin_tard, MT, ML
            "A": (0, 3, 0, 3, 0, 0), "B": (3, 7, 3, 7, 0, 0), "C": (3, 6, 8, 11, 5, 0),
            "D": (7, 17, 7, 17, 0, 0), "E": (6, 12, 11, 17, 5, 5), "F": (3, 5, 19, 21, 16, 16),
            "G": (3, 10, 14, 21, 11, 11), "H": (17, 21, 17, 21, 0, 0), "I": (21, 22, 21, 22, 0, 0),
        }
        # WHEN
        d, duree = dates(EXERCICE)
        # THEN
        self.assertEqual(duree, 22)
        for n, valeurs in attendu.items():
            x = d[n]
            self.assertEqual((x["tot"], x["fin_tot"], x["tard"], x["fin_tard"], x["mt"], x["ml"]), valeurs, n)

    def test_chemin_critique(self):
        """Un seul chemin critique : A - B - D - H - I = 3 + 4 + 10 + 4 + 1 = 22."""
        # GIVEN
        p = EXERCICE
        # WHEN
        chemins = chemins_critiques(p)
        # THEN
        self.assertEqual(chemins, [["A", "B", "D", "H", "I"]])
        self.assertEqual(sum(p[n].duree for n in chemins[0]), 22)

    def test_reseau_juste_avec_tache_fictive(self):
        """Le reseau du corrige est juste ; l'etape 4 (fin de C) : au plus tot 6, au plus tard 11."""
        # GIVEN
        p, reseau = EXERCICE, RESEAU_EXERCICE
        # WHEN
        defauts = verifier_reseau(p, reseau)
        tot, tard = dates_des_etapes(p, reseau)
        # THEN
        self.assertEqual(defauts, [])
        self.assertEqual((tot[4], tard[4]), (6, 11))
        self.assertEqual((tot[8], tard[8]), (22, 22))

    def test_reseau_sans_tache_fictive_est_refuse(self):
        """F et G de 2 a 7 sur deux fleches identiques : le juge reclame une tache fictive, et refuse de dater."""
        # GIVEN
        p, reseau = EXERCICE, RESEAU_EXERCICE_FAUX
        # WHEN
        defauts = verifier_reseau(p, reseau)
        # THEN
        self.assertEqual(defauts, ["deux fleches relient les etapes 2 et 7 : il faut une tache fictive"])
        with self.assertRaises(ValueError):
            dates_des_etapes(p, reseau)

    def test_reseau_qui_ajoute_une_anteriorite_est_refuse(self):
        """Une tache fictive de la fin de C vers le debut de D impose C avant D : l'enonce ne le demande pas."""
        # GIVEN
        faux = [(1, 2, "A"), (2, 3, "B"), (2, 4, "C"), (4, 3, None), (2, 6, "F"), (2, 7, "G"),
                (3, 5, "D"), (4, 5, "E"), (5, 7, "H"), (6, 7, None), (7, 8, "I")]
        # WHEN
        defauts = verifier_reseau(EXERCICE, faux)
        # THEN
        self.assertEqual(defauts, ["le reseau impose C avant D, ce que l'enonce ne demande pas"])

    def test_reseau_avec_une_tache_inconnue_est_refuse(self):
        """Une fleche Z ajoutee au bout du reseau : Z n'est pas dans l'enonce."""
        # GIVEN
        faux = RESEAU_EXERCICE + [(8, 9, "Z")]
        # WHEN
        defauts = verifier_reseau(EXERCICE, faux)
        # THEN
        self.assertEqual(defauts, ["la tache Z n'est pas dans l'enonce"])

    def test_reseau_avec_deux_debuts_ou_deux_fins_est_refuse(self):
        """Une etape 0 qui ne mene qu'a l'etape 2, ou une etape 6 qui ne mene nulle part : erreurs classiques."""
        # GIVEN
        deux_debuts = RESEAU_COURS + [(0, 2, None)]
        deux_fins = RESEAU_COURS + [(4, 6, None)]
        # WHEN
        defauts_debut = verifier_reseau(COURS, deux_debuts)
        defauts_fin = verifier_reseau(COURS, deux_fins)
        # THEN
        self.assertEqual(defauts_debut, ["le reseau doit avoir une seule etape de debut, il en a 2 : [0, 1]"])
        self.assertEqual(defauts_fin, ["le reseau doit avoir une seule etape de fin, il en a 2 : [5, 6]"])


class TestLePiege(unittest.TestCase):

    def test_retard_dans_la_marge_libre_ne_decale_rien(self):
        """E prend 5 jours (sa marge libre) : aucune autre tache ne bouge, le projet fait toujours 22 jours."""
        # GIVEN
        d, _ = dates(EXERCICE)
        # WHEN
        fin, debuts = fin_avec_retards(EXERCICE, {"E": 5})
        # THEN
        self.assertEqual(fin, 22)
        self.assertEqual(debuts, {n: d[n]["tot"] for n in EXERCICE})

    def test_un_jour_de_retard_sur_c_decale_e(self):
        """C n'a aucune marge libre : 1 jour de retard decale le debut de E de 6 a 7, pas la fin du projet."""
        # GIVEN
        retards = {"C": 1}
        # WHEN
        fin, debuts = fin_avec_retards(EXERCICE, retards)
        # THEN
        self.assertEqual((fin, debuts["E"]), (22, 7))

    def test_deux_taches_dans_leur_marge_totale_retardent_le_projet(self):
        """C + 5 et E + 5, chacune dans sa marge totale de 5 jours : 27 jours au lieu de 22."""
        # GIVEN
        d, duree = dates(EXERCICE)
        # WHEN
        seule_c, _ = fin_avec_retards(EXERCICE, {"C": 5})
        les_deux, _ = fin_avec_retards(EXERCICE, {"C": 5, "E": 5})
        # THEN
        self.assertEqual((d["C"]["mt"], d["E"]["mt"]), (5, 5))  # chacune reste dans sa marge totale
        self.assertEqual(seule_c, duree)
        self.assertEqual(les_deux, 27)


class TestContreLeJuge(unittest.TestCase):

    def test_duree_et_dates_au_plus_tot_contre_tous_les_chemins(self):
        """Sur 300 projets au hasard, les dates calculees = le plus long chemin, chemins ecrits un par un."""
        for graine in range(300):
            # GIVEN
            p = projet_au_hasard(graine)
            # WHEN
            d, duree = dates(p)
            # THEN
            self.assertEqual(duree, plus_long_chemin_brut(p), graine)
            for n in p:
                self.assertEqual(d[n]["tot"], tot_brut(p, n), (graine, n))

    def test_definition_des_marges(self):
        """Pour chaque tache : retarder de ML ne decale personne, de ML + 1 decale un successeur (ou la fin) ;
        retarder de MT ne retarde pas le projet, de MT + 1, si. Les deux marges sont donc les plus grandes possibles."""
        for graine in range(150):
            # GIVEN
            p = projet_au_hasard(graine)
            d, duree = dates(p)
            succ = successeurs(p)
            for n in p:
                mt, ml = d[n]["mt"], d[n]["ml"]
                # WHEN
                _, debuts_ml = fin_avec_retards(p, {n: ml})
                fin_ml1, debuts_ml1 = fin_avec_retards(p, {n: ml + 1})
                fin_mt, _ = fin_avec_retards(p, {n: mt})
                fin_mt1, _ = fin_avec_retards(p, {n: mt + 1})
                # THEN
                self.assertTrue(0 <= ml <= mt, (graine, n))
                self.assertEqual(debuts_ml, {m: d[m]["tot"] for m in p}, (graine, n))
                if succ[n]:
                    self.assertTrue(any(debuts_ml1[s] > d[s]["tot"] for s in succ[n]), (graine, n))
                else:
                    self.assertEqual(fin_ml1, duree + 1, (graine, n))
                self.assertEqual(fin_mt, duree, (graine, n))
                self.assertEqual(fin_mt1, duree + 1, (graine, n))

    def test_le_chemin_critique_a_la_duree_du_projet(self):
        """Chaque chemin critique trouve dure exactement la duree du projet."""
        for graine in range(300):
            # GIVEN
            p = projet_au_hasard(graine)
            _, duree = dates(p)
            # WHEN
            chemins = chemins_critiques(p)
            # THEN
            self.assertTrue(chemins, graine)
            for c in chemins:
                self.assertEqual(sum(p[n].duree for n in c), duree, (graine, c))


class TestEnonceFaux(unittest.TestCase):

    def test_un_cycle_est_refuse(self):
        """A avant B et B avant A : l'enonce est impossible."""
        # GIVEN
        taches = (Tache("A", "A", 1, ("B",)), Tache("B", "B", 1, ("A",)))
        # WHEN / THEN
        with self.assertRaises(ValueError):
            projet(*taches)

    def test_deux_taches_du_meme_nom_sont_refusees(self):
        """Deux taches A : la premiere serait ecrasee sans rien dire."""
        # GIVEN
        taches = (Tache("A", "a", 2), Tache("A", "a2", 5))
        # WHEN / THEN
        with self.assertRaisesRegex(ValueError, "meme nom"):
            projet(*taches)

    def test_une_anteriorite_repetee_est_refusee(self):
        """B apres A, A : le chemin critique sortirait deux fois."""
        # GIVEN
        taches = (Tache("A", "a", 2), Tache("B", "b", 3, ("A", "A")))
        # WHEN / THEN
        with self.assertRaisesRegex(ValueError, "deux fois"):
            projet(*taches)


class TestGantt(unittest.TestCase):

    def test_regle_alignee_au_dela_de_100_jours_et_noms_longs(self):
        """Projet de 120 jours, tache au nom de 6 lettres : la barre commence sous son repere."""
        # GIVEN
        p = projet(Tache("DEBUT", "d", 100), Tache("SUITE1", "s", 20, ("DEBUT",)))
        # WHEN
        dizaines, unites, _, suite = gantt(p).splitlines()
        # THEN
        colonne = suite.index("#")  # debut de SUITE1 : jour 100
        self.assertEqual(dizaines[colonne:colonne + 2], "10")
        self.assertEqual(unites[colonne], "0")
        self.assertEqual(dizaines[colonne + 10:colonne + 12], "11")


if __name__ == "__main__":
    unittest.main()
