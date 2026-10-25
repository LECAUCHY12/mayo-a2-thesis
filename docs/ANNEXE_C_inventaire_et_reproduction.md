# Annexe C — Inventaire des archives et instructions de reproduction

État au 22 octobre 2026. Toutes les empreintes sont des SHA-256.

## C.1 Inventaire : versions définitives (à citer)

| Fichier | SHA-256 | Taille | Contenu | Envoyé |
|---|---|---|---|---|
| `A2_partie1.tar.gz` | `cbc0cc297ee0a0790b3cb7513d0384c6c323cfe26b6180b93fc7bd1b115477a6` | 9,9 Mo | notes (synthèse, note scientifique du 22 oct.), code (patchs 0001–0003, sources), scripts d'analyse, sorties d'analyse, données brutes de S2 (`s5_…`, SHA `b1a69769…c723`) | courriel 1/3 |
| `A2_partie2.tar.gz` | `d8dbf1b169f249c720a6e74eb0b9c6e6c9fe44eae6087ef6fe188aa21ab0fcab` | 15,9 Mo | données brutes PH1 (`phases_cauchy_ph1_20261021_211304`, SHA `e1a88aec…98cc`) et CT1 (`controle_cauchy_ct1_20261021_212841`, SHA `0506c2b5…92de`) | courriel 2/3 |
| `A2_partie3.tar.gz` | `00d12e885de273e7851b270f8b53b780eb52fd5bbbe969b1dfe73402b687ac33` | 11,3 Mo | données brutes de S1 (4 campagnes, SHA de l'archive interne `ebc01dfe…`) et empreintes des archives d'origine | courriel 3/3 |
| `0001-Prototype-A2-…patch` | `e6c03362cbf974cf750f340453de874d667b5670a7e60eddafa54b35e29e0cea` | 60 Ko | prototype A2 sur la base amont `74de637` | antérieur |
| `0002-Decomposition-instrumentee-mayo_sign.patch` | `751ec21fbd059e51a4b54f193f3e346a889d4b361cfdf78a3ab77c3e891b6280` | 43 Ko | sondes de décomposition (inertes par défaut) | partie 1 |
| `0003-Controle-effet-des-sondes.patch` | `b590a81d479fd4a32883a60efe4bb5525fb9f45bf92a1acd70f60b265596112d` | 13 Ko | masque de sondes, build `plain`, `run_controle.sh` | partie 1 |
| `0004-E1-analyse-statique-normalisee.patch` | `9c460d0de2193805f3b0c1716f62bf1390ca543778ccfb0022d995ef254a10c6` | 16 Ko | `run_E1.sh`, `e1_analyze.py` (aucun noyau modifié) | nouveau |
| `MAYO-C-A2_source_e72d407.tar.gz` | `e2252a0b51ab827bd097e5a0df73dcbb7ca13539af82b1e728737c58800f6833` | 3,5 Mo | arbre des mesures S1 et S2 = base amont + patch 0001 | antérieur |
| `MAYO-C-A2-phases-v2_source.tar.gz` | `ecb0941b086affb7189151af4b58355acb39edd4de8d7089b34ac7328cf19ef3` | 3,5 Mo | arbre des mesures PH1 et CT1 = base amont + patchs 0001–0003 | partie 1 (code) |
| `E1_kit.tar.gz` | `efe0b71ca5dc1553b0c0a841dc59096216a214080d988ba32731cbe2fcde18f3` | 5,8 Ko | `run_E1.sh`, `e1_analyze.py` à extraire dans l'arbre `MAYO-C-A2-phases-v2` | 22 oct. |
| `e1_cauchy_e1_gcc16.tar.gz` | `7847187a4ce0514d352871d750990120af990f868130e089683dedf09abbea3b` | 1,2 Mo | résultat E1 : désassemblages, configurations, `machine.txt`, `checks.txt`, `SOURCES.sha256` | partie 4 |
| `A2_partie4.tar.gz` | (donné dans le courriel) | < 2 Mo | note v2, annexes A–C, E1 (archive + analyse + feuille de calcul), `reproduire_analyses.sh`, `e1_pile_offsets.py`, patch 0004 | courriel 4 |

## C.2 Archives remplacées ou redondantes (ne pas utiliser comme référence)
| Fichier | SHA-256 | État |
|---|---|---|
| `MAYO-C-A2-phases_source.tar.gz` | `18d23877439e182a3882c54edc4afffd662646663322b198074cf59ee245fa69` | **remplacée** par `…phases-v2` (v2 ajoute le masque de sondes et `run_controle.sh`) |
| `A2_validation_physique_S1_S2_donnees_et_scripts.tar.gz` | `c4acb0eb3db7c404a8491031b3d4f4f9c79f5a665573a796ecb2ec57a73e0ecf` | **redondante** : ses deux archives brutes (S1 `ebc01dfe…`, S2 `b1a69769…`) sont identiques à celles des parties 3 et 1 ; ses analyses sont reproduites à l'identique par `reproduire_analyses.sh` |
| `A2_resultats_machine_physique.tar.gz`, `A2_session2_*.tar.gz`, `rapport_*_S1_S2.md`, `resultats_session_independante_S2.md`, `note_effet_ordre_P1t_MAYO1.md` | — | documents intermédiaires, **remplacés** par la synthèse consolidée du 21 oct. (corrigée le 22 oct.) |
| `A2_donnees_et_journaux.tar.gz`, `prototype_A2_donnees.tar.gz`, `kit_validation_machine_physique.tar.gz`, `tail_aware_etude.tar.gz`, `archive_piste_batch_EF.tar.gz`, `paires_AB_brutes.tar.gz`, `sondes_sorties_brutes.tar.gz` | — | **historique de la phase VM** (Xeon virtualisé) : ne jamais présenter comme performances matérielles |

## C.3 Identification exacte du code
Le code est déterminé par l'**arbre git** (indépendant de l'horodatage des commits). Chaîne vérifiée le 22 oct. : base amont `PQCMayo/MAYO-C` commit `74de637a7c4a7f9fafa888183bc05f5cf920cd2d` (tête de `main` à cette date), puis `git am` des patchs dans l'ordre :

| Après le patch | Arbre git | Correspond à |
|---|---|---|
| 0001 | `87d1729c9343df15df476e5cb2add4d3617f02c6` | `MAYO-C-A2_source_e72d407.tar.gz` (identique octet pour octet) : mesures S1, S2 |
| 0002 | `c8c37c977cb18588187e67699e3ad139e4dd4532` | intermédiaire (sondes) |
| 0003 | `92bcede1bbcd263c9256fa627d94754927b646db` | `MAYO-C-A2-phases-v2_source.tar.gz` (identique octet pour octet) : mesures PH1, CT1 |
| 0004 | `bf6955dae657abb087b58e13e314b946e0d283fe` | arbre de l'analyse E1 |

Les identifiants de commits changent avec `git am` (date de validation) ; les arbres, non.
```
git clone https://github.com/PQCMayo/MAYO-C && cd MAYO-C && git checkout 74de637a7c4a7f9fafa888183bc05f5cf920cd2d
git am 0001-*.patch 0002-*.patch 0003-*.patch 0004-*.patch
git rev-parse HEAD^{tree}      # attendu : bf6955dae657abb087b58e13e314b946e0d283fe
```

## C.4 Reproduire les analyses chiffrées (une seule commande)
Prérequis : Linux, `python3` avec `numpy`, `tar`, `sha256sum`. Placer les trois archives dans un même dossier `D`.
```
sh reproduire_analyses.sh D travail_neuf
```
(`reproduire_analyses.sh` est dans la partie 4 de l'envoi et dans `A2_partie1/scripts` après mise à jour.) Il extrait les trois archives, vérifie leurs `SHA256SUMS.txt`, relance les neuf analyses et affiche `OK` si la sortie est identique à celle livrée (espaces de fin de ligne ignorés ; les lignes qui rappellent des chemins locaux sont ignorées). **Résultat obtenu le 22 oct. : 9 analyses sur 9 identiques.**

| Sortie livrée (`A2_partie1/analyses/`) | Script | Contenu |
|---|---|---|
| `synthese_safe.txt`, `synthese_default.txt` | `synthese_sessions.py` | tableau S1/S2 : dispersions à trois niveaux, entre sessions, effet d'ordre |
| `analyse_comparaison_S1_S2_{safe,default}.txt` | `compare_sessions.py` | comparaison S1/S2 |
| `phases_MAYO{5,1}_decomposition.txt`, `phases_MAYO2_temoin_nul.txt` | `phases_analyze.py` | décomposition instrumentée (PH1) |
| `phases_avec_vs_sans_sondes.txt` | `phases_vs_ref.py` | gain avec toutes les sondes contre sans sondes |
| `controle_sondes_resultats.txt` | `controle_analyze.py` | contrôle CT1 (cinq configurations) |

## C.5 Refaire les mesures (machine physique)
Conditions : Linux, AVX2, gcc ≥ 13 (mesures : gcc 16.2.0), cmake, `python3`+`numpy`, gouverneur `performance` (`sudo cpupower frequency-set -g performance`), cœur 1 dédié, aucun autre travail pendant l'exécution. Les scripts **refusent d'écraser** un résultat existant (une étiquette `SESSION` unique par exécution). Dans l'arbre correspondant du tableau C.3 :

| Étape | Commande (depuis la racine de l'arbre) | Résultat |
|---|---|---|
| S1, S2 (arbre 0001) | `SESSION=<étiquette> sh run_session_independante.sh` (dans `A2_partie1/scripts`, à placer à la racine) | archive datée + `.sha256` |
| PH1 (arbre 0003) | `SESSION=<étiquette> sh test/run_phases.sh` | `phases_<hôte>_<étiquette>_<date>.tar.gz` |
| CT1 (arbre 0003) | `SESSION=<étiquette> sh test/run_controle.sh` | `controle_<hôte>_<étiquette>_<date>.tar.gz` |
| E1 (arbre 0004) | `SESSION=<étiquette> sh test/run_E1.sh` | `e1_<hôte>_<étiquette>.tar.gz` |
Chaque `machine.txt` enregistre date UTC, noyau, compilateur, microcode, gouverneur, `boot_id` et alimentation. **La ligne `date` est en UTC ; l'horloge locale du portable était en UTC+2 pendant ces sessions** (correspondance dans la note, section « Traçabilité »).

## C.6 Limites de la reproductibilité
La reproduction des **analyses** est exacte (C.4). La reproduction des **mesures** donnera des valeurs voisines, non identiques : ticks TSC, fréquence, bruit système. Les rapports A2/officiel ont été reproduits à ≈0,001 près sur deux démarrages (S1, S2). Le code compilé dépend de la version de GCC : l'analyse E1 enregistre version, options et `compile_commands.json`.

## C.7 Refaire l'analyse E1 à partir de l'archive
```
mkdir e1_neuf && tar xzf e1_cauchy_e1_gcc16.tar.gz -C e1_neuf
python3 -I e1_analyze.py e1_neuf/e1_cauchy_e1_gcc16 --excerpts > e1_gcc16.txt     # tableaux et extraits d'assembleur
python3 -I e1_pile_offsets.py e1_neuf/e1_cauchy_e1_gcc16 > pile_offsets_gcc16.tsv  # écritures vers le cadre, proches/lointaines
```
`e1_analyze.py` figure dans le patch 0004 (`test/tail_study/`) ; `e1_pile_offsets.py` est joint à la partie 4. Pour refaire la compilation elle-même (autre compilateur) : `CC=clang SESSION=<étiquette> sh test/run_E1.sh` dans l'arbre du patch 0004 (non encore exécuté avec Clang).

## C.8 Données brutes dans le dépôt (mise à jour du 25 oct. 2026)
Les archives brutes sont dans `data/raw/` du dépôt https://github.com/LECAUCHY12/mayo-a2-thesis (SHA-256 identiques à ceux de C.1 : S1 `ebc01dfe…dabd`, S2 `b1a69769…c723`, PH1 `e1a88aec…98cc`, CT1 `0506c2b5…92de`). `sh scripts/reproduire_depuis_depot.sh <dossier_neuf>` refait les analyses (9 sur 9 identiques). L'archive E1 est dans `data/e1_gcc16/`.
