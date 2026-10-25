# Optimisation A2 « queue xmm » — synthèse consolidée (validation sur machine physique) — version corrigée des horodatages du 22 oct. 2026

Marcel Eric Angoah — 21 octobre 2026. Réponse au courriel de Dr Tale du 21 octobre. Cette synthèse remplace les documents précédents pour tout ce qui concerne les mesures sur machine physique.
Périmètre inchangé : `P1_times_Vt` et `P1t_times_Vt`, MAYO-1 et MAYO-5 uniquement. Candidate à l'intégration : **A2 SAFE seule**. Aucune optimisation nouvelle, aucune extension à MAYO-3 ou à d'autres noyaux. Code d'optimisation, correctif et résultats antérieurs inchangés.

## 0. Résumé
1. **Gains validés (A2 SAFE, rapport A2 / officiel de `mayo_sign`, médiane de processus)** : MAYO-1 **0,8975 (gain 10,3 %)** en S1 et **0,8974** en S2 ; MAYO-5 **0,9873 (1,3 %)** en S1 et **0,9871** en S2. Reproduits sur un démarrage distinct, mêmes machine, compilateur et code. Zéro sortie différente.
2. **Effet d'ordre** : réel sur `P1t_times_Vt` de MAYO-1 (+0,015 en S1, 20 processus sur 20 ; +0,009 en S2), 15 fois plus grand que l'effet générique du protocole (≈ +0,001, visible aussi sur le témoin MAYO-2). Il n'affecte pas `mayo_sign` de MAYO-1 (écart d'ordre −0,0001). Sur MAYO-5, l'écart d'ordre de `mayo_sign` est −0,0006 en S1 (0/20 processus dans l'autre sens) et 0,0000 en S2 : négligeable devant le gain de 0,0127.
3. **Anomalie MAYO-5 : localisée, pas expliquée.** La décomposition directe montre que le reste de la signature est **identique** dans les deux versions (566 917 contre 567 323 ticks). La différence est entièrement dans `m_calculate` *à l'intérieur de la signature* : il y gagne 18 000 ticks (2,0 %), contre 94 000 (11,7 %) isolé, et 101 000 lorsque toutes les sondes sont actives. Mon interprétation précédente (« le reste de la signature ralentit avec A2 ») résultait d'une soustraction de médianes issues de niveaux de mesure différents : **elle est retirée**. La cause de la perte de gain en contexte n'est pas identifiée (§4).
4. **Limites** : une machine, un compilateur (gcc 16.2.0), trois démarrages ; gain MAYO-5 de 1,3 %, proche du critère de ≈ 1 % ; sondes complètes qui modifient le comportement de MAYO-5 (§4.3).

## 1. Unité statistique et sources de variabilité
**Unité statistique : le processus.** Pour chaque niveau et chaque processus (3 001 paires A/B), on calcule la médiane du rapport A2/officiel. Les 3 001 paires d'un même processus ne sont pas des répétitions indépendantes (même état de la machine, même fréquence) : l'IC95 « naïf » calculé sur les paires est de l'ordre de ±0,0001 pour `mayo_sign`, alors que la dispersion entre processus est 5 à 15 fois plus grande. Les IC95 de ce document sont des bootstrap **sur les processus** de chaque session. Une seule différence entre sessions est testée (S2−S1) : avec deux démarrages seulement, la variance « entre sessions » n'est pas estimable comme composante ; je donne l'écart et son IC bootstrap.

| Niveau de variabilité | Définition | MAYO-1 `mayo_sign` | MAYO-5 `mayo_sign` |
|---|---|---|---|
| entre paires (dans un processus) | écart-type robuste (MAD) des rapports par paire | 0,0015 (S1), 0,0013 (S2) | 0,0114 (S1), 0,0039 (S2) |
| entre processus (dans une session) | écart-type des médianes de processus | 0,0009 (20 proc.), 0,0010 (5 proc.) | 0,0008 (20), 0,0005 (5) |
| entre campagnes (S1 seulement) | écart-type des 4 moyennes de campagne | 0,0001 | 0,0002 |
| entre sessions | S2 − S1 [IC95 bootstrap] | −0,0001 [−0,0009 ; +0,0016] | −0,0003 [−0,0011 ; +0,0003] |

Le tableau complet (les quatre niveaux, MAYO-1, 2, 3, 5, S1 et S2) est dans `analyses/synthese_safe.txt` ; la version « variante par défaut » est dans `analyses/synthese_default.txt`.

## 2. Conditions d'exécution
| | S1 | S2 | Décomposition (PH1) et contrôle (CT1) |
|---|---|---|---|
| Date (UTC, ligne `date` de `machine.txt` ; l'horloge du portable est en UTC+2, Yaoundé UTC+1) | 19 oct. 21:58 → 22:43 UTC (23:58 → 00:43 horloge du portable) | 20 oct. 12:10 UTC (14:10 horloge du portable) | 21 oct. 19:13 UTC (PH1) et 19:28 UTC (CT1) (21:13 et 21:28 horloge du portable) |
| Démarrage | un seul (uptime 2 h 56 → 3 h 40 sur les 4 campagnes) ; `boot_id` non enregistré | nouveau, `boot_id` 1c3f62c8… ; lancement à uptime 13 min (démarrage 13:57:01 horloge du portable = 11:57:01 UTC) | nouveau, `boot_id` 2106ca05… (PH1 et CT1 sur le même démarrage) ; uptime 20 min (PH1) et 35 min (CT1) au lancement |
| Plan | 4 × 5 processus × 3 001 paires (graines 1–20) | 1 × 5 × 3 001 (graines 21–25) | PH1 : MAYO-5 10 processus, MAYO-1 et MAYO-2 5 processus ; CT1 : 5 configurations × 10 processus, graines 41–50 |
| Machine | Intel Core i9-9880H (8 cœurs/16 threads, microcode 0x104), `systemd-detect-virt` = none, hypervisor = 0 | identique | identique |
| Logiciels | Kali 7.1.5, gcc 16.2.0, cmake 4.3.4, Python 3.14.8, numpy 2.4.6 | identique | identique |
| Réglages | `performance`, turbo actif (`no_turbo`=0), SMT actif | identique | identique ; secteur branché (AC en ligne, enregistré) |
| Fréquence du cœur 1 au lancement | 4 540 / 4 791 / 4 099 / 3 900 MHz | 800 MHz (repos) | PH1 800 MHz (repos) ; CT1 4 216 MHz (relevé instantané au lancement, non une fréquence soutenue) |
| Options de compilation | `-O3 -funroll-loops -march=haswell -maes`, identiques pour les deux versions | identique | identique |
Temps absolus : S2 est environ 7 % plus lent que S1 pour tous les niveaux, témoins compris (`mayo_sign` MAYO-5 officiel 1 568 532 contre 1 468 127 ticks) ; PH1/CT1 sont à ≈ 1 502 000. Les rapports ne sont pas affectés. Seule la fréquence instantanée au lancement est enregistrée ; elle n'explique pas à elle seule ces écarts (cause non mesurée).
Le niveau P1/P1t/`m_calculate`/`mayo_sign` est détaillé dans `analyses/` ; tous les journaux machine sont dans les archives (`machine.txt`).

## 3. Gains validés (A2 SAFE ; médiane des processus ; IC95 entre processus)
| | officiel | A2 | rapport S1 (20 proc.) | rapport S2 (5 proc.) | gain S1 / S2 |
|---|---|---|---|---|---|
| MAYO-1 `P1_times_Vt` | 41 799 / 44 548 | 32 637 / 35 062 | 0,7803 [0,7793 ; 0,7817] | 0,7814 [0,7794 ; 0,7832] | 22,0 % / 21,9 % |
| MAYO-1 `P1t_times_Vt` | 51 024 / 55 280 | 36 020 / 38 804 | 0,7099 [0,7060 ; 0,7124] | 0,7080 [0,7024 ; 0,7126] | 29,0 % / 29,2 % |
| MAYO-1 `m_calculate` | 131 445 / 140 908 | 106 742 / 114 400 | 0,8110 [0,8096 ; 0,8118] | 0,8102 [0,8080 ; 0,8123] | 18,9 % / 19,0 % |
| **MAYO-1 `mayo_sign`** | 287 044 / 306 230 | 257 292 / 274 904 | **0,8975 [0,8970 ; 0,8979]** | **0,8974 [0,8968 ; 0,8990]** | **10,3 % / 10,3 %** |
| MAYO-5 `P1_times_Vt` | 266 941 / 286 468 | 214 771 / 230 628 | 0,8067 [0,8060 ; 0,8071] | 0,8049 [0,8043 ; 0,8076] | 19,3 % / 19,5 % |
| MAYO-5 `P1t_times_Vt` | 354 402 / 377 540 | 310 723 / 333 170 | 0,8798 [0,8783 ; 0,8818] | 0,8792 [0,8770 ; 0,8858] | 12,0 % / 12,1 % |
| MAYO-5 `m_calculate` | 791 643 / 835 606 | 700 308 / 741 686 | 0,8851 [0,8845 ; 0,8863] | 0,8869 [0,8847 ; 0,8874] | 11,5 % / 11,3 % |
| **MAYO-5 `mayo_sign`** | 1 468 127 / 1 568 532 | 1 449 727 / 1 549 226 | **0,9873 [0,9871 ; 0,9876]** | **0,9871 [0,9863 ; 0,9876]** | **1,3 % / 1,3 %** |
Témoins nuls (aucun noyau A2) : MAYO-2 `mayo_sign` 1,0000 / 1,0000, `m_calculate` 1,0001 / 0,9996 ; MAYO-3 `mayo_sign` 1,0000 / 1,0001. Différences S2−S1 sur les 8 lignes : au plus 0,0019 en valeur absolue, IC95 contenant 0 (`analyses/analyse_comparaison_S1_S2_safe.txt`). La variante par défaut (information, non retenue) donne MAYO-1 `mayo_sign` 0,8976 et MAYO-5 0,9834 en S1.

## 4. Effet d'ordre — méthode et résultats
**Méthode.** Chaque CSV contient pour chaque paire l'ordre d'exécution (`xmm_first`). (1) Équilibrage : proportion de paires « A2 en premier » et probabilité de l'ordre suivant conditionnellement à l'ordre précédent. (2) Pour chaque processus et chaque niveau : médiane du rapport A2/officiel séparément sur les paires « A2 en premier » et « officiel en premier ». (3) L'effet d'ordre d'un processus est la différence des deux médianes ; l'IC95 est un bootstrap sur les processus (unité statistique). (4) Le niveau `mayo_sign` est jugé par l'effet d'ordre rapporté au gain.

**Équilibrage.** A2 en premier dans 29 993 paires sur 60 020 (49,97 %) pour `P1t_times_Vt` de MAYO-1 en S1 ; 50,5 % en S2 ; P(A2 premier | précédent A2 premier) = 0,5003, P(… | précédent officiel premier) = 0,4991. Pas de défaut d'équilibrage.

| Niveau (A2 SAFE) | Session | A2 en 1er | officiel en 1er | écart par processus [IC95] | processus avec écart > 0 | moyenne des deux ordres |
|---|---|---|---|---|---|---|
| MAYO-1 `P1t_times_Vt` | S1 | 0,7142 | 0,6985 | +0,0151 [+0,0101 ; +0,0206] | 20/20 | 0,7063 |
| MAYO-1 `P1t_times_Vt` | S2 | 0,7095 | 0,7009 | +0,0043 [−0,0070 ; +0,0161] | 4/5 | 0,7052 |
| MAYO-1 `mayo_sign` | S1 | 0,8975 | 0,8975 | −0,0001 [−0,0002 ; 0,0000] | 8/20 | 0,8975 |
| MAYO-1 `mayo_sign` | S2 | 0,8974 | 0,8975 | −0,0001 [−0,0002 ; +0,0002] | 1/5 | 0,8974 |
| MAYO-5 `mayo_sign` | S1 | 0,9870 | 0,9876 | −0,0006 [−0,0008 ; −0,0005] | 0/20 | 0,9873 |
| MAYO-5 `mayo_sign` | S2 | 0,9871 | 0,9871 | 0,0000 [−0,0002 ; 0,0000] | 2/5 | 0,9871 |
| MAYO-5 `P1_times_Vt` | S1 / S2 | 0,8071 / 0,8053 | 0,8059 / 0,8043 | +0,0010 / +0,0010 | 20/20 ; 5/5 | 0,8065 / 0,8048 |
| MAYO-2 `m_calculate` (témoin) | S1 / S2 | 1,0005 / 1,0004 | 0,9997 / 0,9994 | +0,0010 [+0,0007 ; +0,0014] / +0,0006 | 20/20 ; 4/5 | 1,0001 / 0,9999 |
(Tableau complet : `analyses/synthese_safe.txt`, section « effet d'ordre ».)

**Temps absolus.** Le bras exécuté en second est plus rapide : MAYO-1 `P1t_times_Vt`, S1 : officiel 51 360 → 50 898 (−0,9 %), A2 36 334 → 35 764 (−1,6 %) ; S2 : officiel −0,7 %, A2 −1,5 %. L'effet est plus fort sur A2, d'où l'asymétrie du rapport. Cause non démontrée.

**Correction d'une affirmation précédente.** J'avais écrit que les témoins MAYO-2/3 ne montraient pas d'effet d'ordre. Ce n'est pas exact : sur `m_calculate` de MAYO-2, où les deux bras sont le même code, l'écart d'ordre vaut +0,0010 (20/20 en S1). Il existe donc un effet générique du protocole d'environ 0,1 %. L'effet de MAYO-1 `P1t_times_Vt` est environ 15 fois plus grand et propre à ce noyau.

**Conclusion.** `mayo_sign` n'est pas affecté de façon significative : MAYO-1 ≤ 0,0001 ; MAYO-5 ≤ 0,0006, soit moins de 5 % du gain de 0,0127. Il s'agit d'une limite expérimentale documentée. Pour `P1t_times_Vt` de MAYO-1, je recommande de citer la moyenne des deux ordres (0,706) en plus de la médiane poolée (0,710) ; le gain d'environ 29 % est inchangé. Aucune expérience dédiée à la cause de l'effet (par exemple un appel à blanc avant chaque bras) n'a été réalisée.

## 5. Anomalie MAYO-5 : décomposition instrumentée et contrôle
**5.1 Dispositif.** Des sondes (`rdtscp` avec `lfence`) mesurent, pour **chaque signature et chaque bras**, le temps total, le nombre de tentatives de la boucle de signature, et pour chaque phase le temps et le nombre d'appels. Les sondes sont inertes par défaut ; sans la macro, le code objet de `mayo.c` et `arithmetic.c` est identique à l'original (vérifié par `cmp` et `objdump`). Même graine et même message dans les deux bras ; ordre aléatoire. Les signatures des deux bras sont identiques dans les 30 010 paires de MAYO-5 (et 15 005 pour MAYO-1 et MAYO-2). Unité statistique : le processus (10 processus de 3 001 paires pour MAYO-5).

**5.2 Fréquences d'appel.** MAYO-5 : 1,000 tentative par signature (identique dans les deux bras) ; chaque phase est appelée une fois par signature, dont `P1_times_Vt` et `P1t_times_Vt` une fois par tentative. MAYO-1 : 1,07 tentative par signature.

**5.3 Toutes sondes actives (MAYO-5).** Temps total 1 374 501 (officiel) et 1 274 140 (A2) : rapport 0,9270 [0,9253 ; 0,9283], soit 7,3 %. La différence moyenne de −100 967 ticks se répartit ainsi : `m_calculate` −100 529 (99,6 %), dont `P1_times_Vt` −54 584 et `P1t_times_Vt` −46 166 ; toutes les autres phases, y compris `expand_sk_internal`, `sample_solution`, `compute_A`, entre −2,6 % et +1,4 % en valeur absolue de la différence moyenne. Les phases hors `m_calculate` sont identiques à ±0,1 % entre les deux bras (reste non attribué 58 587 contre 58 588 ticks). MAYO-1 : 0,8983 ; MAYO-2 (témoin nul) : 0,9999 ; leurs `m_calculate` expliquent 99,3 % de la différence pour MAYO-1.

**5.4 Mais le gain observé avec toutes les sondes n'est pas celui du fonctionnement sans sonde.** Sans sonde, dans la même session, le rapport de `mayo_sign` est 0,9871–0,9873. J'ai donc mesuré cinq configurations du **même** programme de test, alternées dans le temps (10 processus chacune, graines 41–50, un même démarrage) :

| Configuration | Total officiel | Total A2 | Rapport A2/officiel [min–max] IC95 entre processus | Gain |
|---|---|---|---|---|
| `plain` : aucune sonde, bibliothèque d'origine | 1 504 741 | 1 484 504 | 0,9871 [0,9862–0,9879] [0,9866 ; 0,9874] | 1,29 % |
| `none` : sondes compilées, toutes désactivées | 1 504 802 | 1 484 611 | 0,9868 [0,9860–0,9880] [0,9864 ; 0,9874] | 1,32 % |
| `esk` : sonde sur `expand_sk_internal` seule | 1 504 167 | 1 484 146 | 0,9871 [0,9861–0,9879] [0,9866 ; 0,9875] | 1,29 % |
| `mcalc` : sonde sur `m_calculate_M_and_VPV` seule | 1 502 948 | 1 483 529 | 0,9877 [0,9865–0,9885] [0,9869 ; 0,9882] | 1,23 % |
| `all` : toutes les sondes | 1 372 740 | 1 273 970 | 0,9276 [0,9261–0,9291] [0,9269 ; 0,9284] | 7,24 % |
| référence `mayo_tail_ab` (5 proc.) | | | 0,9873 [0,9862–0,9877] | 1,27 % |
Les quatre premières configurations et la référence sont indiscernables (≈ 1,3 %) ; seule la configuration `all` change le résultat.

**5.5 Mesure directe, sans soustraction de médianes (config `mcalc`).** Une sonde unique encadre `m_calculate_M_and_VPV` dans la signature :
| | officiel | A2 | différence |
|---|---|---|---|
| `m_calculate` **dans la signature** | 931 453 [IC95 924 768 ; 939 328] | 912 476 [904 914 ; 920 089] | **−18 406** [−19 396 ; −17 558] (paire à paire) |
| hors `m_calculate` (total − sonde) | 566 917 [559 630 ; 570 230] | 567 323 [559 718 ; 570 232] | **+406** (0,07 %) |
| `expand_sk_internal` (config `esk`) | 322 655 | 322 661 | +6 |
Pour comparaison, `m_calculate` **isolé** (banc habituel, mêmes tampons réutilisés) : 801 324 (officiel) et 707 314 (A2), soit −94 000 (11,7 %) ; `m_calculate` **dans la signature avec toutes les sondes** : 801 073 et 699 775, soit −101 000.

**5.6 Lecture et limite.**
- Le reste de la signature (tout sauf `m_calculate`) est identique dans les deux versions. L'idée précédente d'un « reste ralenti de ≈ 73 000–78 000 ticks » est donc **abandonnée** : elle venait d'une soustraction entre `mayo_sign` et un `m_calculate` isolé, ce qui comparait des contextes différents.
- L'écart est dans `m_calculate` *en contexte de signature sans sondes internes* : il coûte 931 000 (officiel) et 912 000 (A2) ticks, contre 801 000 et 707 000 isolé ou sondé. Le surcoût de contexte est d'environ 130 000 ticks pour l'officiel et 205 000 pour A2 ; la différence de 75 000 ticks entre les deux absorbe l'essentiel du gain isolé.
- Il disparaît lorsque toutes les sondes (donc des `lfence` entre les sous-étapes de `m_calculate`) sont actives, mais pas avec une sonde unique autour de `m_calculate`. La cause n'est **pas identifiée**. Je n'ai pas testé d'hypothèse (par exemple un effet de la hiérarchie mémoire sur la lecture de P1 juste après sa génération, ou un recouvrement d'instructions entre sous-étapes) et n'en retiens aucune.
- Le gain de `mayo_sign` pour MAYO-5 à retenir est celui **sans sondes complètes** : 1,3 % (S1, S2, PH1/CT1, référence). Le 7,3 % mesuré avec toutes les sondes est un résultat de l'instrumentation, pas une performance de l'implémentation.
- Une étape de bissection supplémentaire (sondes actives sur une seule sous-étape de `m_calculate` à la fois) est possible, d'environ 10 minutes de mesure ; je ne l'ai pas lancée, conformément à votre consigne de ne pas poursuivre indéfiniment. À vous de décider.

## 6. Mécanisme de l'optimisation
Les entrées de P1 empaquetées font 40 octets (MAYO-1) et 71 octets (MAYO-5). Le noyau officiel traite le dernier fragment avec un chargement complet de 32 octets. A2 traite les 32·⌊m/64⌋ premiers octets avec des registres ymm et la queue de 8 octets avec un seul `_mm_loadl_epi64` et un `vpshufb` xmm sur la voie basse de la table de multiplication. Sur l'assembleur (gcc 16.2.0, boucle interne) : MAYO-5 `P1_times_Vt` 124 → 106 instructions, `vpshufb` 36 → 30, rechargements de pile 30 → 24 ; `P1t_times_Vt` 126 → 110 ; MAYO-1 `P1_times_Vt` 68 → 51 (rechargements 11 → 5), `P1t_times_Vt` 71 → 56. La boucle est plus courte et utilise moins de registres vectoriels ; c'est une explication appuyée sur l'assembleur, pas une preuve que ces instructions expliquent à elles seules le gain.

## 7. Correction fonctionnelle, accès mémoire et limites des garanties
- **Correction** (S1, S2, PH1, CT1) : KAT officiels MAYO-1, 2, 3, 5 réussis ; tests de schéma réussis ; tests unitaires de 20 000 cas par taille (8 familles d'entrées) sans écart sur les limbes complets, les octets utiles et les octets après la fin de P1 ; zéro signature différente dans toutes les paires A/B ; nombre de tentatives identique.
- **Précondition (multabs)** : A2 n'utilise que la voie basse des tables de multiplication. Les deux voies sont identiques (constantes `__gf16_mulbase` à moitiés égales ; 272 tables, 0 à voies différentes ; contrôle à l'exécution avec `MAYO_TAIL_CHECK`).
- **Accès mémoire.** La variante par défaut lit pour MAYO-5 1 octet au-delà de la fin de P1 empaqueté, comme le noyau officiel (premier octet du flux AES-CTR de P2, donnée publique ; marge de 10 152 octets dans la zone réservée). **A2 SAFE ne lit rien au-delà de P1** : elle charge les octets [63, 71) puis décale de 8 bits. Test « garde-page » (fin de P1 contre une page interdite) : l'officiel et A2 par défaut plantent à marge 0 pour MAYO-5, A2 SAFE ne plante pas. Les octets de bourrage (quartets 142/143) n'influencent pas les positions utiles (opérations quartet par quartet).
- **Garanties de sécurité (temps constant).** Les tests Valgrind (données secrètes marquées indéfinies) et l'inspection de l'assembleur (aucun usage non conforme de registres alimentés par des registres vectoriels) sont des **indicateurs**, pas une preuve. Aucune preuve formelle de temps constant n'est fournie. Ces tests ont été faits dans la VM (Valgrind absent sur la machine physique).
- **Limites de la validation** : une seule machine ; un seul compilateur sur la machine physique (gcc 16.2.0), contre gcc 13.3.0 dans la VM où le gain de MAYO-5 sur `mayo_sign` était de 7,1 % : l'écart entre VM et machine physique mêle machine et compilateur et n'est pas expliqué ; trois démarrages seulement ; S2 sur 5 processus ; le gain de MAYO-5 sur `mayo_sign` (≈ 1,3 %) est proche du critère de ≈ 1 % ; la première exécution de s3 (S1) n'a pas ses CSV bruts archivés (seule la seconde exécution l'est).

## 8. Reproduction et traçabilité
Archive jointe `A2_synthese_et_donnees_brutes.tar.gz` (empreintes dans `SHA256SUMS.txt`) :
- `code/` : correctif A2 (`0001`, commit `e72d407` sur la base amont `74de637`), correctif d'instrumentation (`0002`), correctif de contrôle (`0003`), source de l'archive A2 (SHA-256 `e2252a0b…f6833`) et source instrumenté.
- `donnees_brutes/` : S1 (4 campagnes, 480 CSV appariés), S2 (120 CSV), PH1 (décomposition, CSV par signature), CT1 (contrôle, un CSV par configuration et par processus), avec leurs `machine.txt` et empreintes SHA-256 (S2 `b1a69769…c723`, PH1 `e1a88aec…98cc`, CT1 `0506c2b5…92de`).
- `scripts/` : `compare_sessions.py`, `synthese_sessions.py` (variabilité et effet d'ordre), `order_effect.py`, `order_checks.py`, `phys_pool.py`, `phases_analyze.py`, `phases_vs_ref.py`, `controle_analyze.py`, `run_session_independante.sh`.
- `analyses/` : toutes les sorties citées dans ce document.
Aucune campagne n'écrase la précédente : les scripts de lancement refusent un dossier ou une archive existants. Commandes : `sh test/run_physical_tail.sh 1 3001 "<graines>"` (puis `run_session_independante.sh`), `sh test/run_phases.sh`, `sh test/run_controle.sh`, après `sudo cpupower frequency-set -g performance`.

## 9. Décision demandée
1. Statuer sur l'intégration d'A2 SAFE, avec les limites de la section 7 et le gain de MAYO-5 de 1,3 % sur `mayo_sign`.
2. Décider si l'étape de bissection supplémentaire du §5.6 doit être faite, ou si l'anomalie est consignée comme une limite du travail.
3. Décider si une seconde machine ou un second compilateur est nécessaire pour trancher la différence entre la VM et la machine physique.
