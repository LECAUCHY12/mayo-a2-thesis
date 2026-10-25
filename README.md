# Prototype A2 « queue xmm » pour MAYO-C — code, scripts et résultats (mémoire Master II, ENSPY)

Auteur : ANGOAH Marcel — encadrant : Dr Hervé Talé Kalachi. Statut : **étude en cours ; aucune décision d'intégration**.

A2 remplace, dans les noyaux AVX2 `P1_times_Vt` et `P1t_times_Vt` de MAYO-C, le dernier registre recouvrant (2 `vpshufb` ymm) par un `vpshufb` xmm sur la queue, pour MAYO-1 (m = 80) et MAYO-5 (m = 142) uniquement.

## Contenu
| Dossier | Contenu |
|---|---|
| `patches/` | quatre patchs `git am` sur `PQCMayo/MAYO-C` commit `74de637a7c4a7f9fafa888183bc05f5cf920cd2d` (0001 prototype A2 ; 0002 sondes de décomposition ; 0003 contrôle des sondes ; 0004 analyse statique E1) |
| `scripts/` | scripts d'analyse (Python), `run_session_independante.sh` (mesures S1/S2), `reproduire_analyses.sh`, `e1_pile_offsets.py` |
| `analyses/` | sorties d'analyse livrées (reproductibles à l'identique) |
| `docs/` | note technique v2 (22 oct. 2026), annexes A (comptage des shuffles), B (propriétés de sûreté), C (inventaire et reproduction), synthèse consolidée |
| `data/e1_gcc16/` | résultat E1 (GCC 16.2.0, machine physique) : archive, SHA-256, analyse, feuille de calcul |

Les données brutes de mesure (S1, S2, PH1, CT1 : ≈ 35 Mo) ne sont pas dans ce dépôt ; leurs SHA-256 sont dans `docs/ANNEXE_C_inventaire_et_reproduction.md`.

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
