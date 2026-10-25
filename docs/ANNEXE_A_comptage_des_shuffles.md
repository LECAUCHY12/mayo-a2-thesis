# Annexe A — Comptage des instructions `vpshufb` : borne, réalisation, performance

Cette annexe répond à la demande de Dr Tale de séparer **(1) la borne de comptage, (2) sa réalisation par un algorithme, (3) les performances observées**, dans un modèle défini. Les sections 1 et 2 sont des énoncés mathématiques dans le modèle ; la section 3 est expérimentale ; aucune conclusion de la section 3 n'est déduite des sections 1 et 2.

## A.1 Modèle

**Données.** Un *m-vec* est un vecteur v = (v_0, …, v_{m−1}) ∈ GF(16)^m, m pair, stocké empaqueté en b = m/2 octets : l'élément v_{2i} est le quartet de poids faible de l'octet i, v_{2i+1} le quartet de poids fort. Pour un entier K, les K scalaires c_0, …, c_{K−1} ∈ GF(16) sont regroupés en P = ⌈K/2⌉ paires (c_{2p}, c_{2p+1}) (si K impair, la dernière paire est complétée par 0). On calcule, pour chaque k < K, l'accumulation acc_k ← acc_k ⊕ c_k·v (addition = XOR).

**Table de paire.** Pour la paire p, T_p est une table de 16 octets : T_p[x] = (c_{2p}·x) ⊕ ((c_{2p+1}·x) ≪ 4), x ∈ {0,…,15}. Dans le code, `mayo_V_multabs` stocke T_p dans un registre 256 bits dont les deux voies de 128 bits sont égales (Lemme S3 de l'annexe B).

**Instruction.** `vpshufb` de largeur W ∈ {16, 32} octets : pour chaque octet i < W du registre d'index, `out[i] = T[idx[i] mod 16]` si le bit 7 de `idx[i]` est nul, 0 sinon, T étant la table de la voie 128 bits contenant i. Elle effectue donc **W recherches indépendantes**, une par octet d'index ; chaque recherche livre, pour **un** élément de v, **les deux produits** de la paire.

**Classe de traitements 𝒞.** Algorithmes qui (i) obtiennent chaque produit c_k·v_j par une recherche dans une table de 16 octets (méthode des quatre Russes avec t = 1), (ii) fournissent à chaque recherche un index qui est un quartet isolé dans un octet (bit 7 nul), (iii) n'effectuent pas deux recherches pour le même couple (élément, paire) hors du recouvrement éventuel entre registres, (iv) utilisent les autres instructions (XOR, ET, décalages, permutations, chargements) sans restriction. Sont **hors** de la classe : GFNI (`vgf2p8affineqb`), représentations bitsliced, tables de 256 octets.

**Quantité comptée.** N(algo, m) = nombre d'instructions `vpshufb` exécutées **par paire de scalaires et par m-vec** (c'est le nombre par entrée de P1 divisé par P).

## A.2 Énoncés (dans le modèle)

**Proposition 1 (borne).** Tout algorithme de 𝒞 vérifie N ≥ ⌈m/32⌉.
*Preuve.* Chaque élément v_j, j < m, exige au moins une recherche par paire (hypothèse (i)) ; une instruction fournit au plus W ≤ 32 recherches. Donc N·32 ≥ m. ∎

**Proposition 2 (schéma avec recouvrement, code officiel pour m ≤ 192).** Le schéma consistant à couvrir les b octets par ⌈b/32⌉ chargements de 32 octets, le dernier étant reculé pour finir à l'octet b (recouvrement), et à traiter chaque registre par deux `vpshufb` (quartets impairs, quartets pairs), a N_off(m) = 2·⌈m/64⌉.
*Preuve.* ⌈b/32⌉ = ⌈m/64⌉ chargements ; chacun fournit 32 indices impairs et 32 pairs, soit deux `vpshufb`. ∎ (Code : `MULTIPLY_ACCUMULATE_M_VEC`, branches `M_MAX <= 64 / <= 128 / <= 192`, dernier chargement à `vec + M_VEC_LIMBS_MAX − 4`.)

**Proposition 3 (réalisation de la borne si 0 < r ≤ 32).** Écrivons m = 64q + r avec 0 ≤ r < 64 et notons t = r/2 le nombre d'octets de la queue. Si 0 < r ≤ 32 (donc t ≤ 16), l'algorithme suivant est dans 𝒞 et a N = 2q + 1 = ⌈m/32⌉ :
1. pour g < q : charger l'octet-intervalle [32g, 32g+32), le traiter par deux `vpshufb` ymm (2q instructions) ;
2. pour la queue : charger les t octets de [32q, 32q+t) dans un registre, construire X = [quartets de poids faible des t octets ∣ quartets de poids fort des t octets], soit r indices dans r ≤ 32 octets d'un seul registre, et appliquer **un** `vpshufb` ;
3. réassembler les sorties de la queue (même formule que pour un registre complet, restreinte aux r positions).
*Preuve du comptage.* 2q + 1 ; et ⌈m/32⌉ = 2q + ⌈r/32⌉ = 2q + 1 pour 0 < r ≤ 32. ∎
*Conditions de réalisation (à satisfaire par le code, non par le modèle)* : (a) le chargement de la queue ne lit que des octets de l'entrée si l'on veut une lecture sans dépassement (voir B.1) ; (b) si r ≤ 16 (t ≤ 8), X tient dans un registre 128 bits et la table utilisée est la **voie basse** de T_p ; si 16 < r ≤ 32, X occupe un registre 256 bits (voie basse = impairs, voie haute = pairs, ce qui exige l'égalité des deux voies de T_p) ; (c) le surcoût de préparation et de réassemblage de la queue est payé une fois par entrée (préparation) et une fois par paire (réassemblage).

**Corollaire.** Pour m ≤ 192, Δ(m) := N_off(m) − ⌈m/32⌉ = 2⌈m/64⌉ − ⌈m/32⌉ vaut 1 si 0 < (m mod 64) ≤ 32, et 0 sinon. Dans ce second cas, N_off(m) atteint déjà la borne de la Proposition 1 : **aucun algorithme de 𝒞 ne peut faire mieux en nombre de `vpshufb`**. C'est la formulation exacte de la limite : le gain en shuffles est impossible pour r = 0 et pour 32 < r < 64, dans la classe 𝒞.

**Application aux paramètres actuels.**

| Paramètre | m | q | r | N_off | borne ⌈m/32⌉ | Δ | statut de la réalisation |
|---|---|---|---|---|---|---|---|
| MAYO-1 | 80 | 1 | 16 | 4 | 3 | 1 | **implémentée** (A2) ; queue de 8 octets |
| MAYO-2 | 64 | 1 | 0 | 2 | 2 | 0 | sans objet |
| MAYO-3 | 108 | 1 | 44 | 4 | 4 | 0 | impossible dans 𝒞 |
| MAYO-5 | 142 | 2 | 14 | 6 | 5 | 1 | **implémentée** (A2) ; queue de 7 octets + 1 octet de bourrage |

**Ce qui est implémenté et ce qui ne l'est pas.** Le prototype A2 traite les queues d'au plus 16 éléments (t ≤ 8 octets, r ≤ 16). L'extension aux queues de 17 à 32 éléments (cas 16 < r ≤ 32 de la Proposition 3) **n'est ni implémentée ni testée** ; elle n'est pas un résultat acquis. Aucun des quatre paramètres actuels n'a r dans (16, 32]. Pour les paramètres hors de la famille actuelle (par exemple m = 78, valeur de MAYO-1 dans une version antérieure, r = 14), la Proposition 3 s'applique avec r ≤ 16.

## A.3 Vérification du comptage dans le code généré
Le comptage N·P = nombre de `vpshufb` par entrée peut être vérifié dans l'assembleur : officiel 2⌈m/64⌉·P (MAYO-1 : 4·5 = 20 ; MAYO-5 : 6·6 = 36) ; A2 (2q+1)·P (MAYO-1 : 3·5 = 15 = 10 ymm + 5 xmm ; MAYO-5 : 5·6 = 30 = 24 ymm + 6 xmm). L'étape E1 (annexe D) le contrôle sur le code généré par GCC 16.2.0, après normalisation par le facteur de déroulage.

## A.4 Performance : la borne n'implique pas l'accélération
Une réduction de `vpshufb` ne garantit pas une réduction du temps. Les autres termes sont : coût de préparation de la queue (≈ 4 instructions par entrée, 5 en SAFE), dépendances entre instructions, rechargements de pile, chargements non alignés, et débit des unités d'exécution. Sur une microarchitecture Skylake, l'article *Nibbling MAYO* (section 5.1) indique un `vpshufb` par cycle (et deux sur Ice Lake). Si la boucle n'était limitée que par ce débit, le rapport de temps attendu serait N_A2/N_off : 15/20 = 0,75 (MAYO-1) et 30/36 = 0,833 (MAYO-5). Les rapports mesurés (S1, ticks TSC, A2/officiel) sont :

| Noyau | rapport borne « débit shuffle seul » | rapport mesuré S1 | écart |
|---|---|---|---|
| MAYO-1 P1_times_Vt | 0,750 | 0,780 | mesuré moins bon que la borne : cohérent |
| MAYO-1 P1t_times_Vt | 0,750 | 0,710 | **mesuré meilleur** que la borne |
| MAYO-5 P1_times_Vt | 0,833 | 0,807 | **mesuré meilleur** que la borne |
| MAYO-5 P1t_times_Vt | 0,833 | 0,880 | mesuré moins bon : cohérent |

Deux cas sur quatre sont plus rapides que ce que le seul comptage de shuffles permet : d'autres mécanismes contribuent (par exemple moins de rechargements de pile : −6 sur P1 MAYO-1, −6 sur P1 MAYO-5 d'après l'assembleur de la machine physique), sans que cela soit établi. Le modèle de débit n'explique donc pas à lui seul les gains observés ; l'écart est un objet d'étude, pas une anomalie du comptage.

## A.5 Critères de rejet révisés
- **Proposition 1–3 (mathématiques)** : on ne les « réfute » pas par une mesure. Elles sont fausses seulement si une preuve est erronée, ou si le **modèle ne décrit pas le code** : par exemple si l'assembleur d'A2 contenait un nombre de `vpshufb` par entrée différent de (2q+1)·P. Critère de rejet du modèle : un écart de comptage statique dans E1 non expliqué par le déroulage.
- **Une accélération de MAYO-3 par une autre technique, ou l'absence d'accélération sur une autre microarchitecture, ne réfute ni la borne ni sa réalisation** : elles concernent la performance, hors du comptage.
- **Hypothèse de performance H-P** (séparée) : « sur une microarchitecture où le débit des shuffles est le goulot, le temps du noyau est borné inférieurement par N·P cycles par entrée ». Rejet si un noyau officiel mesuré tourne sous N_off·P cycles/entrée en cycles cœur (par construction impossible sur Skylake), ce qui indiquerait une erreur de mesure ou de comptage. Cette hypothèse ne se teste qu'avec des cycles cœur, pas avec des ticks TSC ; elle est postérieure à E1.
