#!/usr/bin/env python3
"""E1 complement : attribue chaque boucle de travail a un noyau d'apres les marqueurs de fonctions inlinees
('nom():' emis par objdump -l) au lieu des numeros de ligne de la macro partagee. Compte, par entree, les instructions,
les vpshufb, les ecritures et lectures memoire de 32 octets (vmovdqa/vmovdqu).
Usage : python3 -I e1_inline_attrib.py <dossier_E1> [objet ...]"""
import sys, os, re, collections
d = sys.argv[1]
objs = sys.argv[2:] or ["ctx_official_M5","ctx_ab_M5","ctx_phases_M5","ctx_phases_none_M5","bench_ab_M5","ctx_official_M1","ctx_ab_M1"]
KERN = ["P1_times_Vt_xmm","P1t_times_Vt_xmm","P1_times_Vt","P1t_times_Vt","Vt_times_Pv","Ut_times_O","Vt_times_L","P1_times_O","Ot_times_P1O_P2","P1P1t_times_O","m_lambda_times_O"]
def parse(path):
    fn=None; cur=None; out=collections.OrderedDict(); inl=None
    for l in open(path, errors="replace"):
        l=l.rstrip("\n")
        m=re.match(r"^[0-9a-f]+ <([^>]+)>:$", l)
        if m: fn=m.group(1); out[fn]=[]; inl=None; continue
        m=re.match(r"^([A-Za-z_][A-Za-z0-9_.]*)\(\):$", l)
        if m: inl=m.group(1); continue
        m=re.match(r"^\s*([0-9a-f]+):\t(.*)$", l)
        if m and fn: out[fn].append((int(m.group(1),16), m.group(2).strip(), inl))
    return out
def loops(f):
    addr={a:i for i,(a,_,_) in enumerate(f)}; r=[]
    for i,(a,t,_) in enumerate(f):
        m=re.match(r"j\w+\s+([0-9a-f]+)\b",t)
        if m:
            tg=int(m.group(1),16)
            if tg<=a and tg in addr: r.append((addr[tg],i))
    return r
print("objet\tfonction\tadresse\tnoyau(inline)\tinstr\tvpshufb_ymm\tvpshufb_xmm\tmov32_ecritures\tmov32_lectures")
for o in objs:
    p=os.path.join(d,"dumps",o+".dis")
    if not os.path.exists(p): continue
    for fn,f in parse(p).items():
        L=[(s,e) for s,e in loops(f)]
        for s,e in L:
            b=f[s:e+1]
            ny=sum(1 for _,t,_ in b if re.match(r"vpshufb\s+ymm",t)); nx=sum(1 for _,t,_ in b if re.match(r"vpshufb\s+xmm",t))
            if (ny+nx) not in (15,20,24+6,36,30): continue
            if any(s2>=s and e2<=e and (s2,e2)!=(s,e) and sum(1 for _,t,_ in f[s2:e2+1] if t.startswith("vpshufb")) for s2,e2 in L): continue
            c=collections.Counter(i for _,_,i in b if i)
            k=next((c2 for c2,_ in c.most_common() if c2 in KERN), "?")
            st=sum(1 for _,t,_ in b if re.match(r"v?movdq[au]\s+(YMM|XMM)WORD PTR \[",t))
            ld=sum(1 for _,t,_ in b if re.match(r"v?movdq[au]\s+[xy]mm\d+,\s*(YMM|XMM)WORD PTR \[",t))
            print("\t".join(map(str,[o,fn[:24],hex(b[0][0]),k,len(b),ny,nx,st,ld])))
