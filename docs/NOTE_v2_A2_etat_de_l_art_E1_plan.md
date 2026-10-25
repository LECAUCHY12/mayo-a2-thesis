# Note technique v2 — A2 SAFE : état de l'art corrigé, comptage des shuffles, résultats E1 (GCC 16.2.0), plan révisé

Auteur : ANGOAH Marcel — Master II, ENSPY — encadrant : Dr Hervé Talé Kalachi — 22 octobre 2026.
Cette note répond à l'email de Dr Talé du 22 octobre. Elle remplace la note scientifique du 22 octobre (matin) et la section « état de l'art » de la synthèse consolidée. **Aucun noyau n'a été modifié ; E2–E5 n'ont pas été lancées ; aucune extension à MAYO-3 ou à d'autres paramètres n'a été entreprise.** La décision d'intégration est différée.

## 0. Corrections par rapport aux envois précédents
1. **« 36 vpshufb pour l'officiel contre 60 pour A2 » (GCC 13.3) est retiré.** Ce n'est pas une comparaison à travail égal (§3.2). Le détecteur de boucles que j'utilisais alors fusionnait des régions.
2. **« 247 contre 315 instructions »** : même origine, même retrait.
3. L'état de l'art était établi à partir de résumés ; il est refait ici à partir du texte de l'article (section 5.1, pages 10–11 du PDF) et du code de l'artefact (§1).
4. La formule Δ(m) est une identité arithmétique ; elle n'est plus présentée comme une démonstration (annexe A).

## 1. Comparaison technique : article, code officiel actuel, A2 SAFE

### 1.1 Sources lues directement
- **Article** : Beullens, Campos, Celi, Hess, Kannwischer, *Nibbling MAYO: Optimized Implementations for AVX2 and Cortex-M4*, ePrint 2023/1683 (fichier `2023-1683.pdf`, 24 pages). Lu : section 5.1 « AVX2 » (pages 10–11 du PDF).
- **Artefact** : `tches-2024-a14.tgz`, dossiers `avx2-newnibble` (représentation en quartets) et `avx2-oldbitsliced`. Lu : `src/AVX2/shuffle_arithmetic_{64,96,128}.h` (le fichier 96 en entier pour les premières fonctions : `mayo_3_P1_times_O_avx2`, `mayo_3_Ot_times_P1O_P2_avx2`, début de `mayo_3_P1P1t_times_O`).
- **Code officiel actuel** : dépôt `PQCMayo/MAYO-C`, tête de `main` au commit `74de637` (8 sept. 2026) ; fichiers `src/AVX2/shuffle_arithmetic.h`, `arithmetic_common.h`, `src/arithmetic.h`, `src/AVX2/gfni_arithmetic.h`. Historique : le recouvrement généralisé apparaît au commit `11ff0f0` (Round 2) ; `fef05b5` (Round 3) fixe MAYO-1 à m = 80.
- Je n'ai pas lu les 24 pages en entier (sections 1–4 et 6–8 : Cortex-M4, évaluation) : elles ne concernent pas la comparaison AVX2 ci-dessous.

### 1.2 Ce que dit l'article (section 5.1)
- Un `vpshufb` = 32 recherches dans une table de 16 octets ; avec la méthode des quatre Russes à t = 1 et un octet de table contenant deux produits, **64 multiplications par `vpshufb`**.
- Les 32 indices doivent être dans les quartets bas d'un registre : on traite les éléments « impairs » après masquage des quartets hauts, les « pairs » après masquage des quartets bas et décalage de 4 bits. **Les produits impairs et pairs sont accumulés séparément et entrelacés une seule fois à la fin.**
- Tables de multiplication : méthode rapide de [BCH+23], appliquée deux fois puis entrelacée.
- Débit : Skylake 1 `vpshufb`/cycle, Ice Lake 2/cycle, latence 1 ; `vpxor` 3/cycle ; limites annoncées 64 puis 96 multiplications-accumulations par cycle.
- **Paramètres de l'article : m = 64 (MAYO-1, MAYO-2), m = 96 (MAYO-3), m = 128 (MAYO-5).** (Ce ne sont pas les paramètres actuels : m = 80, 64, 108, 142.)
- Page 11 : « In the case of MAYO3, we overlap two vectors, which duplicates 32 operations and allows to easily extend the method to values of m that are not a multiple of 64. »

### 1.3 Ce que fait le code de l'artefact (m = 96)
Pour une entrée de P1 de 6 limbes de 64 bits (48 octets = 96 éléments, **sans bourrage**), `mayo_3_P1_times_O_avx2` fait deux chargements non alignés de 32 octets, aux limbes 0 et 2 (octets [0,32) et [16,48)) : **les deux registres se chevauchent sur 16 octets**. Pour chacun : un quartet impair (ET `0x0f`), un quartet pair (décalage 4 bits puis ET), et pour chaque paire de scalaires **4 `vpshufb`** par entrée (2 registres × impair/pair). Les accumulateurs `temp[]` sont séparés impairs/pairs ; la désintrication (`srli`, `slli`, ET, XOR) est faite une fois par ligne, puis ajoutée à `acc`. Je n'ai trouvé dans les fichiers lus ni chargement 128 bits, ni masque de chargement, ni regroupement des deux moitiés de quartets dans un registre.

### 1.4 Ce que fait le code officiel actuel
- Le recouvrement est **généralisé à tout m** : ⌈m/64⌉ chargements ymm, le dernier reculé (à `vec + M_VEC_LIMBS_MAX − 4` limbes) ; **2⌈m/64⌉ `vpshufb`** par entrée et par paire de scalaires. MAYO-1 (m = 80) : 4 ; MAYO-5 (m = 142) : 6 ; MAYO-3 (m = 108) : 4.
- Les accumulateurs impairs/pairs séparés et la désintrication tardive viennent de l'article.
- Les m-vec ne sont plus de 48 octets sans bourrage : m = 142 donne 9 limbes (144 positions, 2 de bourrage) ; le dernier chargement du code officiel lit 1 octet au-delà de l'entrée (MAYO-5) ou 2 (MAYO-3) : c'est la contrepartie du recouvrement.
- Le backend GFNI utilise des chargements pleine largeur avec une marge (`MAYO_MVEC_SLACK`) et des stockages masqués.

### 1.5 Ce que fait A2 SAFE (MAYO-1 et MAYO-5 seulement)
- Pour q = ⌊m/64⌋ registres complets : comme l'officiel, sans recouvrement. Pour la queue (m mod 64 = 16 ou 14 éléments, soit 8 ou 7 octets) : un chargement de 8 octets (`_mm_loadl_epi64`), construction dans **un seul registre 128 bits** de [quartets bas | quartets hauts], **un seul `vpshufb` xmm** sur la voie basse de la table, réassemblage vers l'accumulateur. Précondition : les deux voies de la table sont égales (annexe B).
- Résultat : (2q + 1) `vpshufb` au lieu de 2(q + 1) : MAYO-1 3 contre 4 ; MAYO-5 5 contre 6 (par paire de scalaires).
- Variante SAFE (MAYO-5) : charge les octets [63, 71) et décale de 8 bits, donc aucune lecture hors de l'entrée ; la variante par défaut lit [64, 72) (1 octet au-delà, comme l'officiel).

### 1.6 Tableau comparatif

| Aspect | Article (artefact, m = 96) | Officiel actuel (74de637) | A2 SAFE |
|---|---|---|---|
| Représentation GF(16) | 2 éléments/octet, quartet bas d'abord | idem | idem |
| Table | 16 octets, 2 produits/octet, deux voies égales | idem | idem ; **la voie basse seule est utilisée pour la queue** |
| Indices | quartets impairs/pairs séparés par masque et décalage | idem | queue : [bas \| hauts] d'un même 8 octets dans un xmm |
| Chargements | 2 ymm non alignés, **recouvrement** de 16 octets | ⌈m/64⌉ ymm, dernier reculé (recouvrement généralisé, Round 2) | q ymm sans recouvrement + 1 chargement de 8 octets |
| Queue | recouvrement (32 opérations dupliquées) | recouvrement | `vpshufb` xmm sur la queue (≤ 16 éléments implémenté) |
| Accumulateurs | impairs/pairs séparés ; désintrication à chaque ligne | idem | idem + réassemblage de la queue dans le dernier limbe |
| `vpshufb` / entrée / paire | 4 (m = 96) | 2⌈m/64⌉ | 2⌊m/64⌋ + 1 |
| Accès mémoire | dans l'entrée (48 octets exacts) | 0, 1 ou 2 octets au-delà selon m | SAFE : aucun ; défaut : 1 octet (MAYO-5) |
| Paramètres traités | 64, 96, 128 | quelconques | 80 et 142 seulement |

### 1.7 Classification
- **Déjà connu (article)** : le schéma shuffle à t = 1 avec 2 produits par octet ; la séparation impair/pair avec désintrication tardive ; le recouvrement de deux registres pour une longueur non multiple de 64, y compris l'idée d'étendre à tout m.
- **Introduit dans le code officiel après l'article** : la généralisation du recouvrement à des m arbitraires (commit `11ff0f0`, Round 2) et les paramètres actuels (m = 80, 108, 142).
- **Ce qu'A2 fait différemment** : remplacer, pour une queue d'au plus 16 éléments, le registre recouvrant (2 `vpshufb` ymm) par **un `vpshufb` xmm** sur une queue dont les deux moitiés de quartets sont rassemblées dans un registre 128 bits, et la variante SAFE sans lecture hors entrée.
- **Réserve** : je n'ai trouvé cette technique ni dans l'article ni dans l'artefact, ni dans les fichiers officiels lus. **Cela ne prouve pas sa nouveauté** ; d'autres implémentations (autres dépôts, ou mises en œuvre non publiées) peuvent l'employer. Je ne revendique aucune nouveauté.
- **Remarque** : pour m = 96 (cas de l'article), r = 32 : la borne ⌈96/32⌉ = 3 serait atteignable par la proposition 3 de l'annexe A (variante 17–32 éléments, **non implémentée ici**), alors que l'article en utilise 4. Je ne tire de cela aucune conclusion de performance.

## 2. Comptage des shuffles
Voir **annexe A** : modèle (classe 𝒞, représentation, travail par `vpshufb`, contraintes de chargement), proposition 1 (borne ⌈m/32⌉), proposition 2 (schéma officiel, 2⌈m/64⌉), proposition 3 (réalisation de la borne si 0 < r ≤ 32), corollaire, **séparation entre borne, réalisation et performance**, critères de rejet révisés. Le prototype traite les queues d'au plus 16 éléments ; **l'extension à 17–32 éléments n'est ni implémentée ni testée**.

## 3. Résultats E1 (analyse statique, GCC 16.2.0, machine physique)

### 3.1 Configuration et intégrité
Archive `e1_cauchy_e1_gcc16.tar.gz`, SHA-256 `7847187a4ce0514d352871d750990120af990f868130e089683dedf09abbea3b`. gcc (Debian 16.2.0-3) 16.2.0 ; binutils 2.47 ; cmake 4.3.4 ; noyau 7.1.5+kali-amd64 ; options `-O3 -funroll-loops -march=haswell -maes`, `MAYO_TAIL_SAFE=ON` (celles des mesures). Date : 22 oct. 2026 17:21:24 UTC (19:21:24 locale, UTC+2). Arbre de code : `bf6955da…` (base 74de637 + patchs 0001–0004). Les 12 objets compilés avec et sans `-g` ont un code machine identique. Désassemblage : `objdump -d -l -M intel`. Compilateur : GCC 16.2.0 d'abord ; **Clang n'a pas encore été examiné** (demande de Dr Talé : après GCC).

### 3.2 Résolution de l'ambiguïté « 36 contre 60 »
Méthode : boucles minimales contenant des `vpshufb` (saut arrière), facteur de déroulage u = nombre de `vpshufb` de la boucle / nombre attendu par entrée, comptes ramenés à une entrée de P1.
- **GCC 16.2.0** : u = 1 pour toutes les boucles de travail (pas de déroulage). `vpshufb` par entrée, identiques dans les quatre contextes (banc, contexte, contexte sans sondes, contexte avec toutes les sondes) : **officiel 20 (MAYO-1) et 36 (MAYO-5) ; A2 15 (10 ymm + 5 xmm) et 30 (24 ymm + 6 xmm)**, conformes au modèle (écart 0 ; feuille de calcul `E1_GCC16_resultats.xlsx`).
- **GCC 13.3 (VM)**, réexamen du dump : une boucle interne officielle MAYO-5 a 36 `vpshufb` et une boucle interne A2 en a 30 (24 ymm + 6 xmm) ; les régions de **72** (officiel : 2 boucles internes) et de **60** (A2 : 48 ymm + 12 xmm = 2 × 30) ont des décomptes égaux à exactement deux boucles internes (2 × 36 ; 2 × (24 + 6)) : ce sont des régions externes (boucle englobante), pas des boucles d'une entrée. Le « 36 contre 60 » comparait donc une boucle interne officielle (36) à une région externe A2 (60) : **périmètres différents** ; à périmètre égal, c'est 36 contre 30 (boucle interne) ou 72 contre 60 (deux boucles internes).
- Conclusion : **à travail égal, A2 contient moins de `vpshufb` que l'officiel, sur GCC 13.3 comme sur GCC 16.2.0.**

### 3.3 Instructions statiques par entrée de P1 (GCC 16.2.0)

| Configuration | Param. | Noyau | Instr. officiel | Instr. A2 | A2/off. |
|---|---|---|---|---|---|
| banc isolé | MAYO-1 | P1 | 68 | 51 | 0,750 |
| banc isolé | MAYO-1 | P1t | 71 | 56 | 0,789 |
| banc isolé | MAYO-5 | P1 | 124 | 106 | 0,855 |
| banc isolé | MAYO-5 | P1t | 126 | 110 | 0,873 |
| contexte | MAYO-1 | P1 | 68 | 52 | 0,765 |
| contexte | MAYO-1 | P1t | 91 | 71 | 0,780 |
| contexte | MAYO-5 | P1t | 162 | 139 | 0,858 |
| contexte, toutes sondes | MAYO-5 | P1t | 126 | 109 | 0,865 |

À MAYO-5 en contexte, la boucle officielle de `P1_times_Vt` n'a pas pu être attribuée avec certitude (la macro de multiplication est partagée entre plusieurs noyaux : `P1_times_O`, `Ot_times_P1O_P2`, etc., et mon attribution repose sur les numéros de ligne) ; seul le rapport de `P1t_times_Vt` est donné.

### 3.4 Écritures vers le cadre de pile
Compte par entrée d'écritures vers `[rsp±…]`/`[rbp−…]` (spills ou tableaux locaux, non distingués par ce compte) :

| Noyau | Banc | Contexte (sans toutes les sondes) | Contexte, toutes sondes |
|---|---|---|---|
| MAYO-5 P1t officiel | 29 | 65 | 29 |
| MAYO-5 P1t A2 | 23 | 52 | 22 |
| MAYO-5 P1 A2 | 23 | 52 | 22 |
| MAYO-1 P1t officiel / A2 | 11 / 6 | 31 / 21 | non étudié |
| MAYO-1 P1 officiel / A2 | 11 / 4 | 11 / 5 | non étudié |

Constats (statiques) :
1. Pour MAYO-5, les contextes `none`, `esk`, `mcalc` ont **exactement le même code** que le contexte sans sondes (`ctx_ab`) ; seul le contexte avec **toutes** les sondes diffère et ressemble au banc isolé (instructions et écritures par entrée proches).
2. Dans le contexte sans toutes les sondes, le même registre (ex. `ymm15`) est écrit **deux fois**, à deux emplacements fixes du cadre distants de `0xbfc0` octets (`[rbp-0x2b4b0]` puis `[rbp-0x37470]`, etc.), soit ≈ 30 écritures de plus par entrée dans les deux bras. Je n'ai pas identifié à quoi correspondent ces deux séries d'emplacements.
3. Le cadre de `sign_signature_internal` est très grand : tous les accès sont à de grands décalages de `rbp`, donc **le décalage à la base ne distingue pas un débordement de registres d'un tableau local**. Le terme « rechargement de pile » est trop fort ; je parle d'« écritures vers le cadre ».

### 3.5 Ce que E1 permet et ne permet pas de conclure
- **Établi (statique)** : à travail égal, A2 contient moins de `vpshufb` (conforme au modèle) et moins d'instructions par entrée, à un rapport voisin dans les quatre configurations ; le code du noyau MAYO-5 dans la signature **change** selon que toutes les sondes sont actives ou non, dans les deux bras.
- **Non établi** : le nombre d'instructions **exécutées** (il faut multiplier par le nombre de tours de boucle : V(V+1)/2 entrées × tours internes, non mesuré ici) ; le coût de ces instructions (**une micro-opération n'est pas une instruction** : `vpshufb ymm` et `vpshufb xmm` ne sont pas forcément des µops équivalentes ; je n'ai fait aucune hypothèse de ce genre) ; l'effet des écritures supplémentaires sur le temps ; **la cause de l'écart de gain de MAYO-5 entre le noyau isolé (≈ 11,5 %) et la signature complète (≈ 1,3 %)**.
- L'hypothèse **H3 (code différent en contexte)** devient plausible pour MAYO-5 (le code diffère selon les sondes), alors qu'elle était jugée faible sur la VM ; elle n'explique pas encore le sens ni l'ampleur de l'effet, puisque la différence concerne les deux bras.

## 4. Plan expérimental révisé (rien n'est lancé)

Aucune expérience n'est exécutée avant la décision de Dr Talé. Pour chacune : hypothèse précise, grandeur mesurée, critère de rejet.

**Grandeurs à ne pas confondre** : *ticks TSC* (horloge constante : temps), *cycles cœur* (`CPU_CLK_UNHALTED.THREAD` : dépend de la fréquence effective), *instructions retirées* (`INST_RETIRED.ANY`), *événements de blocage mémoire* (p. ex. `CYCLE_ACTIVITY.STALLS_MEM_ANY`, `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`) ; chacune répond à une question différente et aucune ne remplace les autres.

**E2 — attribution des événements matériels à `m_calculate`.** Un `perf stat` sur tout le programme mélange toutes les phases. Méthode proposée : lecture des compteurs **dans le processus, autour de la seule région** (`perf_event_open` + `rdpmc`, mêmes bornes que les sondes TSC), avec contrôle « région vide » pour mesurer le coût de la lecture elle-même, une région à la fois, appariée officiel/A2, sur les compteurs ci-dessus. *Rejet de H1 (plafond mémoire)* : si les événements de blocage mémoire par entrée sont équivalents entre le noyau isolé et le contexte pour les deux bras, alors H1 n'explique pas la différence.

**E3 — réécriture de P1.** Le protocole « réécrire P1 avant chaque appel » ajoute lui-même du trafic cache. Trois bras : (a) sans réécriture ; (b) réécriture de P1 puis appel du noyau ; (c) réécriture de P1 puis appel d'un noyau nul (même séquence, pas de calcul). L'effet du noyau est (b) − (c) ; l'effet de la réécriture est (c) − (a). *Rejet* : si (b) − (c) ne diffère pas de (a) à l'incertitude des mesures appariées, la réécriture n'explique pas l'écart.

**E4 — conflit d'adresses.** Hypothèse précise : des chargements de P1 dont les 12 bits bas d'adresse coïncident avec ceux d'écritures en attente vers les emplacements du cadre (observés en E1 : paires distantes de `0xbfc0`) provoquent des blocages de chargement (4K aliasing). On ne balaye pas de décalages de pile : on lit `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS` par entrée, officiel et A2, noyau isolé et contexte. *Rejet* : compte d'alias négligeable (< 1 % des chargements) dans les deux bras du contexte, ou identique entre les bras.

**E5 — instrumentation.** Trois facteurs séparés : instruction de lecture d'horloge (`rdtsc` contre `rdtscp`), barrière `lfence` (présente ou non), code généré (identique ou non, vérifié par désassemblage comme dans E1). *Rejet* : si, à code généré identique, ni la lecture d'horloge ni `lfence` ne modifient le gain dans la région, l'artefact « toutes les sondes » est dû au code généré (H3), pas à la sérialisation (H4).

**Ordre suggéré (à décider par Dr Talé)** : d'abord Clang pour E1 (statique) ; puis E5 et E2 seulement si E1 confirme que le code diffère ; E3 et E4 selon E2.

## 5. Annexes
- **Annexe A** — comptage des `vpshufb` : borne, réalisation, performance (fichier `ANNEXE_A_comptage_des_shuffles.md`).
- **Annexe B** — propriétés de sûreté d'A2 SAFE (fichier `ANNEXE_B_proprietes_de_surete.md`).
- **Annexe C** — inventaire des archives et instructions de reproduction (fichier `ANNEXE_C_inventaire_et_reproduction.md`).
