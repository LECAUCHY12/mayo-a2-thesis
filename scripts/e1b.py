#!/usr/bin/env python3
"""E1b : analyse STATIQUE de l'origine des ecritures supplementaires de MAYO-5 en contexte de signature.
Aucune mesure de temps, aucun noyau modifie. Pour chaque (construction, variante) : recompilation de src/mayo.c avec la commande
exacte de E1 (compile_commands_nog.json) + UNE option supplementaire, puis desassemblage et comptage des boucles de travail.

Constructions (cibles de E1) : P_none = mayo_5_phases_none (sans sondes ; doublon observe), P_all = mayo_5_phases (toutes sondes),
                                TAB = mayo_5_tailab (construction des mesures S1/S2).
Variantes : base (controle : doit redonner exactement le code de E1) ; dump (options de sortie seulement, controle : code identique) ;
nosra (-fno-tree-sra) ; noipasra (-fno-ipa-sra) ; nodse (-fno-tree-dse) ; nopre (-fno-tree-pre) ; nofre (-fno-tree-fre).
Pour chaque variante, le rapport donne (i) les boucles de travail (36 vpshufb ymm = officiel ; 24 ymm + 6 xmm = A2) avec nombre
d'instructions, d'ecritures de 32 octets et noyau identifie par le pas d'adresse sur P1 (add ...,0x47 : P1_times_Vt ; imul ...,0x47 : P1t_times_Vt),
(ii) la mesure des AUTRES modifications : instructions de sign_signature_internal hors boucles de travail, et distance entre histogrammes
de mnemoniques hors boucles de travail par rapport a la variante base. Une disparition des ecritures n'est donc jamais lue seule.

Usage : python3 -I e1b.py <dossier_E1> <dossier_sortie_NEUF> [--variantes base,dump,nosra,...]\n        python3 -I e1b.py --dumps-e1 <dossier_E1>      # identification des noyaux sans recompiler
<dossier_E1> = dossier produit par run_E1.sh (contient logs/compile_commands_nog.json et dumps/*.dis), arbre de sources toujours en place.
"""
import sys, os, re, json, shlex, subprocess, collections, gzip, shutil, hashlib

CONSTRUCTIONS = {"P_none": ("mayo_5_phases_none", "ctx_phases_none_M5"),
                 "P_all": ("mayo_5_phases", "ctx_phases_M5"),
                 "TAB": ("mayo_5_tailab", "ctx_ab_M5")}
VARIANTES = collections.OrderedDict([
    ("base", []),
    ("dump", ["-fdump-tree-optimized", "-fdump-tree-sra-details", "-fdump-tree-esra-details", "-fdump-rtl-expand", "-fdump-rtl-ira"]),
    ("nosra", ["-fno-tree-sra"]), ("noipasra", ["-fno-ipa-sra"]), ("nodse", ["-fno-tree-dse"]),
    ("nopre", ["-fno-tree-pre"]), ("nofre", ["-fno-tree-fre"]),
])
FUNC = "sign_signature_internal"


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def compile_cmd(ccj, target):
    for e in ccj:
        if ("%s.dir/" % target) in e.get("output", "") and e["file"].endswith("src/mayo.c"):
            return e
    raise SystemExit("commande de compilation introuvable pour " + target)


def build_object(entry, extra, out_o, workdir):
    args = shlex.split(entry["command"])
    i = args.index("-o")
    args[i + 1] = out_o
    args = args[:i] + extra + args[i:]
    r = sh(args, cwd=entry["directory"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return args, r.stderr.decode(errors="replace")


def disasm(o):
    return subprocess.run(["objdump", "-d", "-M", "intel", "--no-show-raw-insn", o], check=True, capture_output=True, text=True).stdout


def insns_of(text, func):
    on, out = False, []
    for l in text.split("\n"):
        m = re.match(r"^[0-9a-f]+ <([^>]+)>:$", l)
        if m:
            on = (m.group(1) == func)
            continue
        m = re.match(r"^\s*([0-9a-f]+):\t(.*)$", l)
        if on and m:
            out.append((int(m.group(1), 16), m.group(2).strip()))
    return out


def loops_of(f):
    addr = {a: i for i, (a, _) in enumerate(f)}
    r = []
    for i, (a, t) in enumerate(f):
        m = re.match(r"j\w+\s+([0-9a-f]+)\b", t)
        if m:
            tg = int(m.group(1), 16)
            if tg <= a and tg in addr:
                r.append((addr[tg], i))
    return r


def work_loops(f):
    L = loops_of(f)
    cnt = lambda s, e: (sum(1 for _, t in f[s:e + 1] if re.match(r"vpshufb\s+ymm", t)),
                        sum(1 for _, t in f[s:e + 1] if re.match(r"vpshufb\s+xmm", t)))
    cand = [(s, e) + cnt(s, e) for s, e in L]
    cand = [c for c in cand if (c[2], c[3]) in ((36, 0), (24, 6))]
    mins = [c for c in cand if not any((o[0] >= c[0] and o[1] <= c[1] and o[:2] != c[:2]) for o in cand)]
    res = []
    for s, e, ny, nx in mins:
        body = f[s:e + 1]
        has_add47 = any(re.match(r"add\s+\w+,0x47$", t) for _, t in body)
        has_imul47 = any(re.match(r"imul\s+\w+,\w+,0x47$", t) for _, t in f[max(0, s - 12):s + 4])
        kern = "P1t" if has_imul47 else ("P1" if has_add47 else "autre")
        st = sum(1 for _, t in body if re.match(r"v?movdq[au]\s+[XY]MMWORD PTR \[", t))
        res.append(dict(s=s, e=e, addr=body[0][0], kern=kern, arm="A2" if nx else "officiel", n=len(body), stores=st))
    return res


def mnem_hist(f, excluded):
    h = collections.Counter()
    for i, (_, t) in enumerate(f):
        if i in excluded:
            continue
        h[t.split()[0]] += 1
    return h


def l1(a, b):
    return sum(abs(a[k] - b[k]) for k in set(a) | set(b)) // 2


def dumps_e1(e1):
    """Identification des noyaux par le pas d'adresse sur P1 dans les desassemblages DEJA produits par E1 (sans recompiler)."""
    for tag in ["ctx_official_M5", "ctx_ab_M5", "ctx_phases_M5", "ctx_phases_none_M5", "ctx_phases_esk_M5", "ctx_phases_mcalc_M5", "ctx_official_M1", "ctx_ab_M1"]:
        p = os.path.join(e1, "dumps", tag + ".dis")
        if not os.path.exists(p):
            continue
        ins = insns_of(open(p, errors="replace").read(), FUNC)
        print("==", tag)
        for w in sorted(work_loops(ins), key=lambda x: x["addr"]):
            if w["kern"] != "autre":
                print("   %-4s %-8s adresse %#x : %3d instr, %3d ecritures de 32 octets" % (w["kern"], w["arm"], w["addr"], w["n"], w["stores"]))


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--dumps-e1":
        return dumps_e1(os.path.abspath(sys.argv[2]))
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    e1, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    vs = list(VARIANTES)
    if "--variantes" in sys.argv:
        vs = sys.argv[sys.argv.index("--variantes") + 1].split(",")
    if os.path.exists(out):
        raise SystemExit("REFUS : %s existe deja" % out)
    os.makedirs(out)
    ccj = json.load(open(os.path.join(e1, "logs", "compile_commands_nog.json")))
    with open(os.path.join(out, "machine.txt"), "w") as f:
        f.write(subprocess.run("date -u; uname -a; gcc --version | head -1; objdump --version | head -1", shell=True, capture_output=True, text=True).stdout)
    rapport = []
    ref = {}
    for cname, (target, e1tag) in CONSTRUCTIONS.items():
        entry = compile_cmd(ccj, target)
        e1txt = open(os.path.join(e1, "dumps", e1tag + ".dis"), errors="replace").read()
        e1ins = [(a, t) for a, t in insns_of(e1txt, FUNC)]
        for v in vs:
            d = os.path.join(out, cname + "_" + v)
            os.makedirs(d)
            o = os.path.join(d, "mayo.o")
            extra = list(VARIANTES[v])
            if v == "dump":
                extra = [x for x in extra]
            args, err = build_object(entry, extra + (["-fopt-info-inline-optimized"] if v == "dump" else []), o, d)
            if err.strip():
                open(os.path.join(d, "messages_compilateur.txt.gz"), "wb").write(gzip.compress(err.encode()))
            # sorties de dump (nommees d'apres la sortie) : compressees, puis resumees
            for fn in sorted(os.listdir(d)):
                if fn != "mayo.o" and fn.startswith("mayo") and not fn.endswith(".gz"):
                    fp = os.path.join(d, fn)
                    data = open(fp, "rb").read()
                    open(fp + ".gz", "wb").write(gzip.compress(data))
                    os.remove(fp)
                    if ".optimized" in fn:
                        txt_g = data.decode(errors="replace")
                        m = re.search(r";; Function %s .*?\n(.*?)(?=\n;; Function |\Z)" % FUNC, txt_g, re.S)
                        body = m.group(1) if m else ""
                        rapport.append("          GIMPLE optimise (%s) : lignes mentionnant 'temp' = %d, dont references memoire (MEM/tableau) = %d" % (
                            cname, sum(1 for l in body.split("\n") if "temp" in l), sum(1 for l in body.split("\n") if "temp" in l and ("MEM" in l or "[" in l))))
            open(os.path.join(d, "commande.txt"), "w").write(" ".join(shlex.quote(a) for a in args) + "\n")
            txt = disasm(o)
            ins = insns_of(txt, FUNC)
            wl = work_loops(ins)
            excl = set()
            for w in wl:
                excl.update(range(w["s"], w["e"] + 1))
            hist = mnem_hist(ins, excl)
            if v == "base":
                ref[cname] = hist
                same_e1 = ([t for _, t in ins] == [t for _, t in e1ins])
                rapport.append("# CONTROLE %s : code de %s identique a celui de E1 (%s) : %s" % (cname, FUNC, e1tag, "OUI" if same_e1 else "NON (E1 non reproduit : arreter l'interpretation)"))
            dist = l1(hist, ref[cname]) if cname in ref else -1
            tot = len(ins)
            rapport.append("%-7s %-9s instr(%s)=%d  hors boucles de travail=%d  distance mnemoniques hors boucles vs base=%d" % (cname, v, FUNC, tot, tot - len(excl), dist))
            for w in sorted(wl, key=lambda x: x["addr"]):
                rapport.append("          boucle %-8s %-8s adresse %#x : %3d instr, %3d ecritures de 32 octets" % (w["kern"], w["arm"], w["addr"], w["n"], w["stores"]))
            open(os.path.join(d, "disasm.txt.gz"), "wb").write(gzip.compress(txt.encode()))
    open(os.path.join(out, "rapport_E1b.txt"), "w").write("\n".join(rapport) + "\n")
    print("\n".join(rapport))


if __name__ == "__main__":
    main()
