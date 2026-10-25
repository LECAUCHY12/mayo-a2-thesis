# Note v3 — Interprétation de E1 : instructions supplémentaires en contexte, lien quantitatif avec l'écart de performance, contribution d'A2

ANGOAH Marcel — 25 octobre 2026. Suite à l'email de Dr Talé du 25 octobre (07:55). Complète la note v2 (22 oct.) ; sauf mention contraire, les chiffres de la note v2 restent valables. **Aucune mesure nouvelle, E2–E5 non lancées, aucun noyau modifié.** Compilateur : GCC 16.2.0 (Debian 16.2.0-3), options des mesures. Légende : **[F]** fait lu dans le code généré ou dans les mesures déposées ; **[I]** inférence que je tire des faits ; **[H]** hypothèse non testée.

## 1. Quelles sont les instructions supplémentaires du contexte de signature, et d'où viennent-elles ?

### 1.1 Les faits (nouvelle attribution, `scripts/e1_inline_attrib.py`)
Les boucles de travail sont comparées dans quatre constructions de `sign_signature_internal` pour MAYO-5 : contexte officiel seul, contexte avec A2 sans sondes (`ctx_ab`, `none`, `esk`, `mcalc` : **mêmes comptes d'instructions** dans les quatre), contexte avec toutes les sondes, et banc isolé.

- **[F] La différence entre « sans toutes les sondes » et « toutes les sondes » est exactement une écriture de 32 octets (`vmovdqa [rbp−…], ymm`) de plus par accumulateur et par entrée de P1.** Pour `P1t_times_Vt` officiel : 126 → 162 instructions, soit **+36** = 36 accumulateurs (36 `vpshufb`) ; pour A2 : 109 → 139 pour P1t et 105 → 135 pour P1, soit **+30** = 30 accumulateurs. Le reste de la boucle est identique, instruction pour instruction (mêmes 36 `vpshufb`, 36 `vpxor`, 6 `vpand`, 3 `vpsrlw`, 3 `vmovdqu`, mêmes `add/sub/cmp/jb`). Le nombre de lectures mémoire de 32 octets ne change pas (9 pour l'officiel, 8 pour A2).
- **[F] Ces écritures vont vers une seconde série d'emplacements consécutifs (pas de 0x20) distants de 0xbfc0 octets de la première**, par exemple `[rbp−0x377f0]` (lecture-modification-écriture de l'accumulateur : `vpxor ymm,ymm,[mem]` puis `vmovdqa [mem],ymm`) et `[rbp−0x36c70]` (écriture seule à l'intérieur de la boucle). Le même registre est donc stocké deux fois par mise à jour.
- **[F] L'adresse de cette seconde série est prise ailleurs dans la fonction** (`lea rsi,[rbp−0x36d30]`, `lea rax,[rbp−0x36d30]`…) et utilisée par des pointeurs dans les boucles qui suivent.
- **[F] Cinq boucles sont concernées dans la signature MAYO-5 sans sondes : `P1_times_Vt_xmm`, `P1t_times_Vt_xmm` (A2, +30 chacune), `P1t_times_Vt` (officiel, +36), et deux boucles de 160 instructions (`Ut_times_O`, `m_lambda_times_O`) dans les deux bras (+37 chacune).** Les boucles de 123 instructions n'ont pas de doublon.
- **[F] La boucle officielle `P1_times_Vt` n'a pas de doublon.** Réserve : l'information de débogage de GCC fusionne les corps identiques (la boucle apparaît sous le nom `P1_times_O`, qui n'est pas appelé dans la signature) ; j'identifie donc la boucle officielle de `P1_times_Vt` par sa **position** (première boucle de 36 `vpshufb` de la fonction, au même rang que la boucle A2) et son **décompte** (123 instructions, comme dans le banc). Cette identification est **[I]**. *Sensibilité* : si cette boucle avait aussi un doublon (+36), le coût par écriture calculé en §2.3 passerait de 0,358 à 0,179 pour l'officiel (contre 0,346 pour A2) et la cohérence entre bras disparaîtrait.
- **[F] Avec GCC 13.3 (VM), aucun doublon** : contexte et banc ont les mêmes comptes (P1t officiel 127 ; A2 115 ; écritures 29 et 26). Le phénomène est propre à la construction GCC 16.2.0 ; les mesures physiques analysées ici sont, elles, faites avec GCC 16.2.0.
- **[F] MAYO-1 (GCC 16.2.0)** : le doublon touche seulement `P1t_times_Vt` (officiel 71 → 91, **+20** ; A2 56 → 71, **+15**), pas `P1_times_Vt` (officiel 68 → 68 ; A2 51 → 52).

### 1.2 Inlining, allocation de registres, accès à la pile
- **Inlining [F]** : dans le contexte, les noyaux sont inlinés dans `sign_signature_internal` ; dans le banc, ce sont des fonctions séparées ou des boucles de `m_calculate_M_and_VPV`. Le code d'une boucle de travail dépend donc de la fonction englobante.
- **Allocation de registres [F]** : 36 (officiel) ou 30 (A2) accumulateurs dépassent les 16 registres ymm ; les accumulateurs résident en mémoire (`vpxor` avec opérande mémoire suivi d'une écriture) **dans toutes les constructions**, y compris le banc. Ce n'est pas la différence recherchée.
- **Accès à la pile [F]** : tous les accès du contexte se font à de grands décalages de `rbp` (cadre de plus de 220 Ko) ; le décalage ne distingue pas un débordement de registres d'un tableau local. J'emploie donc « écritures vers le cadre ».
- **Origine du doublon [H]** : dans la construction sans toutes les sondes, GCC 16.2.0 semble conserver le tableau `temp[]` de la macro en mémoire (son adresse est prise pour les boucles de désintrication qui suivent) **en plus** des emplacements scalaires de l'accumulateur ; l'ajout des sondes (qui change la taille et la structure de la fonction) modifie cette décision. Je n'ai pas identifié la passe de GCC responsable. Cette hypothèse se teste par compilation seule (sans mesure) avec les sorties `-fdump-tree-optimized`, `-fdump-tree-sra` et `-fopt-info-inline` ; voir §4.

## 2. Ces différences expliquent-elles quantitativement l'écart de performance ?

### 2.1 Les faits mesurés (déposés, MAYO-5, ticks TSC par signature)
- Toutes sondes (PH1) : `m_calculate` 805 136 → 705 398 (**−12,4 %**) ; P1 + P1t 635 681 → 535 497 (−15,8 %). Total de la signature : −7,2 %.
- Sans sondes (CT1, configuration `mcalc`, sonde unique sur `m_calculate`) : `m_calculate` 936 031 → 916 206 (**−2,1 %**). Total de la signature −1,2 % à −1,3 % (configurations `plain`, `none`, `esk`, `mcalc`).
- Entre « sans sondes » et « toutes sondes », `m_calculate` est plus lent de **130 895** ticks (officiel, +16 %) et de **210 808** ticks (A2, +30 %). Le reste de la signature ne change pas (`mcalc` : écart +406 ticks entre les deux bras).

### 2.2 Instructions statiques contre temps mesuré (P1 + P1t, par entrée)

| Construction | Instr. officiel | Instr. A2 | Gain statique | Gain mesuré |
|---|---|---|---|---|
| banc isolé | 124 + 126 = 250 | 106 + 110 = 216 | 13,6 % | ≈ 11,5 % (`m_calculate`, mesure isolée citée par Dr Talé) |
| contexte, toutes sondes | 123 + 126 = 249 | 105 + 109 = 214 | 14,1 % | 15,8 % (P1+P1t) ; 12,4 % (`m_calculate`) |
| contexte, sans sondes | 123 + 162 = 285 | 135 + 139 = 274 | **3,9 %** | **2,1 %** (`m_calculate`) |

**[F] Le nombre d'instructions statiques par entrée perd presque tout son avantage dans la construction sans sondes (14,1 % → 3,9 %), parce que A2 reçoit le doublon sur ses deux noyaux (+60 par entrée) alors que l'officiel ne le reçoit que sur P1t (+36).** Dans le banc et avec toutes les sondes, l'avantage statique et l'avantage mesuré sont du même ordre ; sans sondes, les deux s'effondrent ensemble.

### 2.3 Modèle à un paramètre (`scripts/e1_modele_quantitatif.py`)
Hypothèse du modèle : le temps d'une boucle est proportionnel à son nombre d'instructions par entrée, avec un coefficient c (ticks par instruction) commun aux deux bras. NENT = 10 153.
- Étalonnage sur « toutes sondes » : c = 635 681 / (249 × 10 153) = **0,251 tick/instruction**.
- Prédiction sans sondes : gain de P1 + P1t de **28 082** ticks ; **mesuré 19 825** (sur `m_calculate`). Écart : la prédiction surestime d'environ 40 %.
- Coût des écritures supplémentaires, calculé séparément pour chaque bras à partir de la différence « sans sondes » moins « toutes sondes » : officiel 130 895 ticks / 365 508 écritures = **0,358** ; A2 210 808 ticks / 609 180 écritures = **0,346**. **[I]** Les deux bras donnent le même coût par écriture supplémentaire (écart de 3 %) : c'est le seul test de cohérence indépendant du modèle (1 paramètre, 2 observations). `Ut_times_O` et `m_lambda_times_O` portent aussi un doublon dans les deux bras, mais leur nombre de tours n'est pas connu ici ; ils ajoutent le même terme aux deux bras et ne changent pas la différence de gain.
- Ordre de grandeur en cycles **[H]** : la fréquence cœur n'a pas été mesurée ; à une fréquence soutenue de 3,5–4,5 GHz pour un TSC de 2,4 GHz, 0,35 tick vaut environ 0,5–0,65 cycle par écriture de 32 octets, ordre de grandeur compatible avec un débit d'une écriture par cycle, sans que cela soit établi.

### 2.4 Ce qui est établi, ce qui ne l'est pas
- **Établi [F]** : (a) le code de plusieurs boucles de la signature MAYO-5 diffère selon la présence de toutes les sondes, par exactement une écriture supplémentaire par accumulateur ; (b) cette différence est asymétrique entre bras (+60 pour A2, +36 pour l'officiel sur P1 + P1t) ; (c) les temps mesurés varient de façon cohérente avec cette asymétrie (gain de `m_calculate` de 12,4 % à 2,1 %).
- **Inféré [I]** : l'asymétrie du doublon explique l'essentiel de la perte de gain de MAYO-5 en contexte ; le coût par écriture supplémentaire est le même dans les deux bras.
- **Non établi [H]** : que le coût passe par le débit des écritures (plutôt que, par exemple, la dépendance d'écriture–lecture mémoire sur les mêmes emplacements, ou des conflits d'adresses) ; la cause de la décision de GCC ; l'effet à d'autres versions de compilateur ; **la corrélation n'est pas une preuve de causalité** : seule une expérience qui supprime le doublon sans autre changement (§4) peut trancher.
- **MAYO-1 [I]** : le doublon touche P1t dans les deux bras à un rapport voisin (71/91 = 0,78 contre 56/71 = 0,79 dans le banc) et pas P1 ; l'avantage statique est donc conservé (0,770 banc, 0,774 contexte), en accord avec un gain de signature qui ne s'effondre pas (≈ 10 % mesuré).

## 3. Contribution technique d'A2 (comparaison finalisée)

### 3.1 Sources et vérifications supplémentaires
- **Article** : section 5.1 lue en entier ; code `avx2-newnibble/src/AVX2/shuffle_arithmetic_{64,96,128}.h` : recherche exhaustive de chargements 128 bits, de masques de chargement, de `_mm_*` : aucun résultat ; fichier 96 lu pour ses fonctions principales.
- **Code officiel, historique complet de `src/AVX2/shuffle_arithmetic.h`** (commits `3c9be9e` ajout, `d81b689` représentation en quartets, `11ff0f0` Round 2, `4b7cd94`, `fef05b5` Round 3, tête de `main` `74de637`) : aucune occurrence de `_mm_loadl_epi64`, `_mm_shuffle_epi8` ou de registre 128 bits dans les noyaux de multiplication jusqu'à `4b7cd94`. À partir de `fef05b5`, le fichier contient des `__m128i` aux lignes 548–606 : ce sont la transposition par décalage de bits de m-vecs (lignes 548–584) et le chargement d'une table 16 octets diffusée sur 256 bits (ligne 606) ; **aucun `vpshufb` xmm sur une queue**.
- Branche `nibbling-mayo` du dépôt officiel : `shuffle_arithmetic_{64,96,128}.h` de l'article, sans tel mécanisme.

### 3.2 Délimitation
- **Connu avant A2** : multiplication par `vpshufb` à t = 1 avec 2 produits par octet ; séparation impair/pair et désintrication tardive ; recouvrement de deux registres pour m non multiple de 64 (article, MAYO-3, m = 96) ; généralisation à tout m par chargements reculés (code officiel, Round 2).
- **Ce qu'A2 apporte de différent, dans le cadre des sources consultées** : (i) pour une queue d'au plus 16 éléments, regrouper les deux moitiés de quartets d'un chargement de 8 octets dans un seul registre 128 bits et le traiter par **un** `vpshufb` xmm sur la voie basse de la table (précondition : voies égales), au lieu d'un registre ymm recouvrant (deux `vpshufb`) ; (ii) la variante SAFE pour m = 142, qui charge [63,71) et décale, **sans lecture hors de l'entrée**, alors que le code officiel lit 1 octet au-delà (MAYO-5) ou 2 (MAYO-3) ; (iii) les propriétés vérifiées de la queue (annexe B).
- **Ce qu'A2 ne revendique pas** : le recouvrement, la séparation impair/pair, la désintrication tardive, le schéma `vpshufb` à t = 1, ni une nouveauté absolue. L'absence de la technique dans les sources lues ne prouve pas qu'elle n'existe pas ailleurs.
- **Portée** : gain en `vpshufb` possible seulement si 0 < (m mod 64) ≤ 32 (annexe A) ; implémenté pour 0 < r ≤ 16 (MAYO-1, MAYO-5) ; MAYO-2 (r = 0) et MAYO-3 (r = 44) sans gain possible dans la classe de la proposition 1 ; la variante 17–32 éléments n'est pas implémentée. Le gain de signature dépend du code généré par le compilateur (§1–2), établi ici pour GCC 16.2.0 sur une machine (i9-9880H).

## 4. Suite proposée (non lancée)
**E1b (statique, compilation seule, sans mesure)** — pour tester l'hypothèse de §1.2 : compiler la signature MAYO-5 avec GCC 16.2.0 en ajoutant `-fdump-tree-sra -fdump-tree-optimized -fopt-info-inline-optimized`, puis avec `-fno-tree-sra` ou `-fno-ipa-sra` à titre de contrôle de code, et vérifier par désassemblage si le doublon disparaît. Critère de rejet de l'hypothèse « tableau `temp[]` conservé en mémoire » : doublon présent même quand `temp[]` n'a plus de pointeur dans l'arbre optimisé. **Sur accord de Dr Talé uniquement.** Ensuite, et seulement si le doublon se supprime sans autre changement de code, une mesure avec et sans doublon (E5 réduit) trancherait la causalité du §2.4. Clang reste à examiner pour E1.

## 5. Données brutes et reproduction
Le dépôt contient maintenant `data/raw/` : les archives brutes de S1, S2, PH1, CT1 avec leurs SHA-256 et un script de contrôle. Reproduction : `sh scripts/reproduire_analyses.sh data/raw travail_neuf` refait les 9 analyses et compare byte à byte avec `analyses/`.
