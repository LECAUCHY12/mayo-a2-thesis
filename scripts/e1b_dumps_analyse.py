#!/usr/bin/env python3
"""Analyse STATIQUE des sorties de E1b (aucune mesure de temps).
Usage : python3 -I e1b_dumps_analyse.py <dossier e1b_gcc16> > analyse.txt
Pour P_none et P_all : (1) declarations de tableaux `temp`/`tt` dans le GIMPLE optimise de sign_signature_internal ;
(2) blocs de travail (>=20 pshufb256 ou >=5 pshufb128) : stores `temp[..] =` dans le bloc, references `temp_I_lsm` ;
(3) diagnostics SRA sur `temp` ; (4) boucle A2 P1 en assembleur : bases/decalages des ecritures de 16/32 octets."""
import sys, os, re, gzip, collections
d = sys.argv[1]
def rd(p): return gzip.open(p, "rt", errors="replace").read()
def func_lines(txt, name):
    L = txt.split("\n")
    s = [i for i, l in enumerate(L) if l.startswith(";; Function %s " % name)][0]
    e = next((i for i in range(s + 1, len(L)) if L[i].startswith(";; Function ")), len(L))
    return L[s:e]
for c in ["P_none", "P_all"]:
    print("=" * 20, c)
    B = func_lines(rd(f"{d}/{c}_dump/mayo.c.273t.optimized.gz"), "sign_signature_internal")
    bi = [i for i, l in enumerate(B) if l == "{"][0]
    decl = []
    for l in B[bi + 1:]:
        if re.match(r"^\s*<bb ", l): break
        decl.append(l.strip())
    arr = collections.Counter(re.sub(r";$", "", x) for x in decl if re.match(r"^__m(256|128)i (temp|tt)\[\d+\];", x))
    print("(1) tableaux temp/tt declares :", dict(arr))
    print("    variables temp_I_lsm declarees :", sum(1 for x in decl if x.startswith("__m256i temp_I_lsm") or "temp_I_lsm" in x and x.endswith(";")))
    bbs = []; cur = None
    for l in B:
        m = re.match(r"^\s*<bb (\d+)>", l)
        if m: cur = [int(m.group(1)), []]; bbs.append(cur)
        elif cur is not None: cur[1].append(l)
    print("(2) blocs de travail (bb : pshufb256/pshufb128 ; stores temp[]= ; stores tt[]= ; refs _lsm)")
    n_arr = n_lsm = 0
    for n, ls in bbs:
        t = "\n".join(ls)
        a, b = len(re.findall(r"pshufb256", t)), len(re.findall(r"pshufb128", t))
        if a >= 20 or b >= 5:
            st = len(re.findall(r"^\s*temp\[[^\]]+\]\s*=", t, re.M)); stt = len(re.findall(r"^\s*tt\[[^\]]+\]\s*=", t, re.M)); lsm = len(re.findall(r"temp_I_lsm", t))
            print("    bb %3d : %2d/%d ; temp[]= %2d ; tt[]= %d ; _lsm %d" % (n, a, b, st, stt, lsm))
            n_arr += (st + stt > 0); n_lsm += (lsm > 0 and st + stt == 0)
    print("    blocs avec stores de tableau dans le bloc : %d ; blocs a scalaires _lsm sans store de tableau : %d" % (n_arr, n_lsm))
    for p in ["143t.sra", "041t.esra"]:
        t = rd(f"{d}/{c}_dump/mayo.c.{p}.gz"); b = "\n".join(func_lines(t, "sign_signature_internal"))
        dq = collections.Counter(l.strip() for l in b.split("\n") if "Disqualifying temp" in l)
        print("(3) %s : 'Disqualifying temp' = %d  %s" % (p, sum(dq.values()), dict(dq)))
    t = rd(f"{d}/{c}_base/disasm.txt.gz"); on = False; ins = []
    for l in t.split("\n"):
        m = re.match(r"^[0-9a-f]+ <([^>]+)>:$", l)
        if m: on = m.group(1) == "sign_signature_internal"; continue
        m = re.match(r"^\s*([0-9a-f]+):\t(.*)$", l)
        if on and m: ins.append((int(m.group(1), 16), m.group(2).strip()))
    loops = []
    addr = {a: i for i, (a, _) in enumerate(ins)}
    for i, (a, tx) in enumerate(ins):
        m = re.match(r"j\w+\s+([0-9a-f]+)\b", tx)
        if m and int(m.group(1), 16) <= a and int(m.group(1), 16) in addr: loops.append((addr[int(m.group(1), 16)], i))
    for s, e in loops:
        body = ins[s:e + 1]
        x = sum(1 for _, tx in body if re.match(r"vpshufb\s+xmm", tx)); y = sum(1 for _, tx in body if re.match(r"vpshufb\s+ymm", tx))
        if (y, x) == (24, 6) and any(re.match(r"add\s+\w+,0x47$", tx) for _, tx in body):
            st = [tx for _, tx in body if re.match(r"v?movdq[au]\s+[XY]MMWORD PTR \[", tx)]
            c32 = [int(re.search(r"\[\w+([+-]0x[0-9a-f]+)\]", tx).group(1), 16) for tx in st if tx.split()[1].startswith("YMM")] if False else None
            y32 = sorted(int(re.search(r"\[\w+([+-]0x[0-9a-f]+)\]", tx).group(1), 16) for tx in st if re.search(r"YMMWORD", tx))
            x16 = sorted(int(re.search(r"\[\w+([+-]0x[0-9a-f]+)\]", tx).group(1), 16) for tx in st if re.search(r"XMMWORD", tx))
            reg = collections.Counter(("%s%s" % ("-" if o < 0 else "+", hex(abs(o) // 0x10000 * 0x10000))) for o in y32)
            print("(4) boucle A2 P1 @%#x : %d instr, %d ecritures (%d de 32 octets, %d de 16 octets)" % (ins[s][0], len(body), len(st), len(y32), len(x16)))
            print("    ecritures de 32 octets par region de pile (arrondi 64 Kio) :", dict(reg))
            print("    ecritures de 16 octets : %d, decalages %s .. %s" % (len(x16), hex(x16[0]) if x16 else "-", hex(x16[-1]) if x16 else "-"))
            break
