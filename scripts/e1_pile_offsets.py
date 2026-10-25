#!/usr/bin/env python3
"""E1 complement : separe, dans chaque boucle de travail extraite (excerpts/*.asm), les ecritures vers le cadre de pile
selon la distance a la base (rsp/rbp) : proches (< 4 Ko : emplacements de sauvegarde ou petits tableaux) ou lointaines
(>= 4 Ko : grands tableaux locaux). Ne distingue PAS un debordement de registres d'un tableau local : seulement l'adresse.
Usage : python3 -I e1_pile_offsets.py <dossier_E1>"""
import sys, os, re, glob, collections
d = sys.argv[1]
print("fichier d'extrait\tecritures proches\tecritures lointaines\tlectures proches\tlectures lointaines")
for f in sorted(glob.glob(os.path.join(d, "excerpts", "*.asm"))):
    w = collections.Counter()
    for l in open(f, errors="replace"):
        if not re.search(r"\bv?mov", l):
            continue
        m = re.search(r"\[(rbp|rsp)([-+]0x[0-9a-f]+)?\]", l)
        if not m:
            continue
        off = abs(int(m.group(2), 16)) if m.group(2) else 0
        # destination = premier operande
        ops = l.split("\t")[-1].split(None, 1)
        dest_mem = len(ops) > 1 and ops[1].strip().startswith(("YMMWORD", "XMMWORD", "QWORD", "DWORD", "BYTE", "WORD"))
        kind = ("ecriture" if dest_mem else "lecture", "proche" if off < 4096 else "lointain")
        w[kind] += 1
    print("%s\t%d\t%d\t%d\t%d" % (os.path.basename(f)[:-4], w[("ecriture", "proche")], w[("ecriture", "lointain")],
          w[("lecture", "proche")], w[("lecture", "lointain")]))
