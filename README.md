# Prototype A2 « queue xmm » pour MAYO-C — code, scripts et résultats (mémoire Master II, ENSPY)

Auteur : ANGOAH Marcel — encadrant : Dr Hervé Talé Kalachi. Statut : **étude en cours ; aucune décision d'intégration**.

A2 remplace, dans les noyaux AVX2 `P1_times_Vt` et `P1t_times_Vt` de MAYO-C, le dernier registre recouvrant (2 `vpshufb` ymm) par un `vpshufb` xmm sur la queue, pour MAYO-1 (m = 80) et MAYO-5 (m = 142) uniquement.

## Contenu
| Dossier | Contenu |
|---|---|
| `patches/` | quatre patchs `git am` sur `PQCMayo/MAYO-C` commit `74de637a7c4a7f9fafa888183bc05f5cf920cd2d` (0001 prototype A2 ; 0002 sondes de décomposition ; 0003 contrôle des sondes ; 0004 analyse statique E1) |
| `scripts/` | scripts d'analyse (Python), `run_session_independante.sh` (mesures S1/S2), `reproduire_depuis_depot.sh`, `e1_inline_attrib.py`, `e1_modele_quantitatif.py`, `e1_pile_offsets.py` |
| `analyses/` | sorties d'analyse livrées (reproductibles à l'identique) |
| `docs/` | note technique v2 (22 oct. 2026), annexes A (comptage des shuffles), B (propriétés de sûreté), C (inventaire et reproduction), synthèse consolidée |
| `data/e1_gcc16/` | résultat E1 (GCC 16.2.0, machine physique) : archive, SHA-256, analyse, feuille de calcul |

`data/raw/` contient les **données brutes** (≈ 29 Mo) de S1 (4 campagnes), S2, PH1 et CT1, avec `SHA256SUMS.txt`.

## Reproduire les analyses chiffrées à partir des données brutes (une commande)
Depuis la racine du dépôt (python3 + numpy requis, < 1 minute) :
```
sh scripts/reproduire_depuis_depot.sh ../travail_neuf
```
Le script vérifie les empreintes des archives brutes, refait les 9 analyses de `analyses/` et affiche `OK` pour chaque sortie identique (9 sur 9 le 25 oct. 2026).

## Documents
- `docs/NOTE_v2_…` (22 oct.) : état de l'art, résultats E1, plan. 
- `docs/NOTE_v3_interpretation_E1.md` (25 oct.) : instructions supplémentaires du contexte (origine), lien quantitatif avec l'écart de performance, contribution d'A2. **La note v3 remplace les §3.3–3.5 de la note v2 là où elles diffèrent** (notamment l'identification des boucles officielles de MAYO-5).

## Reconstituer le code exact
```
git clone https://github.com/PQCMayo/MAYO-C && cd MAYO-C
git checkout 74de637a7c4a7f9fafa888183bc05f5cf920cd2d
git am ../patches/0001-*.patch ../patches/0002-*.patch ../patches/0003-*.patch ../patches/0004-*.patch
git rev-parse HEAD^{tree}   # attendu : bf6955dae657abb087b58e13e314b946e0d283fe
```

## Refaire l'analyse E1 (statique, aucune mesure de temps)
Dans l'arbre obtenu ci-dessus (GCC ≥ 13, cmake, binutils, python3) :
```
SESSION=<etiquette_unique> sh test/run_E1.sh        # produit e1_<hote>_<etiquette>.tar.gz
python3 -I test/tail_study/e1_analyze.py e1_<hote>_<etiquette> --excerpts
python3 -I ../scripts/e1_pile_offsets.py e1_<hote>_<etiquette>
```
## Licence
Les patchs modifient `PQCMayo/MAYO-C` (Apache-2.0) ; ils sont publiés sous la même licence. Les scripts d'analyse sont publiés sous Apache-2.0.

## Mémoire

**Lire le mémoire (PDF, 48 pages, format ENSPY) : [`memoire/memoire_v2.pdf`](https://github.com/LECAUCHY12/mayo-a2-thesis/blob/main/memoire/memoire_v2.pdf)**

Sources LaTeX dans `memoire/` (compiler `main.tex` avec xelatex, ou pdflatex sur Overleaf). Les logos sont dans `memoire/logos/`.

## Analyse statique E1b (GCC 16.2.0, exécutée le 25 oct. 2026)
- `scripts/e1b.py` : compilation seule, aucune mesure de temps.
- `data/e1b_gcc16/` : archive des sorties (dumps GCC, désassemblages) et SHA-256.
- `scripts/e1b_dumps_analyse.py` → `analyses/analyse_e1b_dumps.txt` ; `analyses/rapport_E1b.txt`.
- `analyses/identification_noyaux_gcc16.txt` : identification des noyaux par le pas d'adresse.
