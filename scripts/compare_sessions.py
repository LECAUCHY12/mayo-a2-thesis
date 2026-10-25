# Usage: python3 -I compare_sessions.py <racine_session1> <racine_session2> [variante=safe]
# racine = dossier contenant un ou plusieurs physical_tail_*/csv_<variante>/ (S1 : s1,s2,s3b,s4 ; S2 : la nouvelle session)
import csv,glob,sys,numpy as np
rng=np.random.default_rng(11)
LV=['P1_times_Vt','P1t_times_Vt','m_calculate','mayo_sign']
def load(f):
    d=np.genfromtxt(f,delimiter=',',skip_header=1); return d[:,1],d[:,2],d[:,3]
def procs(root,var,m,lv):
    out=[]
    for f in sorted(glob.glob(f'{root}/**/csv_{var}/m{m}_s*_{lv}.csv',recursive=True)):
        o,b,x=load(f); r=x/b
        out.append((np.median(b),np.median(x),np.median(r),np.median(r[o==1]),np.median(r[o==0])))
    return np.array(out)
def ci(v):
    i=rng.integers(0,len(v),(5000,len(v))); return np.percentile(np.median(v[i],axis=1),[2.5,97.5])
A,B=sys.argv[1],sys.argv[2]; var=sys.argv[3] if len(sys.argv)>3 else 'safe'
print(f'##### variante {var} : PARTIE 1 - chaque session separement')
res={}
for name,root in (('S1',A),('S2',B)):
    print(f'--- {name} ({root})')
    for m in (1,5,2,3):
        for lv in LV:
            P=procs(root,var,m,lv)
            if not len(P): continue
            res[(name,m,lv)]=P; lo,hi=ci(P[:,2])
            print(f'MAYO-{m} {lv:13s} n_proc={len(P)} base={np.median(P[:,0]):.0f} a2={np.median(P[:,1]):.0f} ratio={np.median(P[:,2]):.4f} [{P[:,2].min():.4f}-{P[:,2].max():.4f}] IC95_entre_proc=[{lo:.4f};{hi:.4f}] gain={(1-np.median(P[:,2]))*100:.2f}% | ratio A2 1er={np.median(P[:,3]):.4f} off 1er={np.median(P[:,4]):.4f} moy 2 ordres={(np.median(P[:,3])+np.median(P[:,4]))/2:.4f}')
print('\n##### PARTIE 2 - comparaison S2 vs S1 (difference des rapports ; bootstrap sur les processus de chaque session)')
for m in (1,5,2,3):
    for lv in LV:
        if ('S1',m,lv) not in res or ('S2',m,lv) not in res: continue
        a=res[('S1',m,lv)][:,2]; b=res[('S2',m,lv)][:,2]
        ia=rng.integers(0,len(a),(5000,len(a))); ib=rng.integers(0,len(b),(5000,len(b)))
        d=np.median(b[ib],axis=1)-np.median(a[ia],axis=1); lo,hi=np.percentile(d,[2.5,97.5])
        print(f'MAYO-{m} {lv:13s} ratio S1={np.median(a):.4f} S2={np.median(b):.4f} diff(S2-S1)={np.median(b)-np.median(a):+.4f} IC95=[{lo:+.4f};{hi:+.4f}]')
print('\n##### PARTIE 3 - mayo_sign - m_calculate (MESURE DIRECTE NON VALIDE comme cout du reste : niveaux mesures dans des appariements distincts ; indication seulement)')
for name in ('S1','S2'):
    for m in (1,5):
        try:
            s=res[(name,m,'mayo_sign')];c=res[(name,m,'m_calculate')]
        except KeyError: continue
        print(f'{name} MAYO-{m}: officiel {np.median(s[:,0])-np.median(c[:,0]):.0f} | A2 {np.median(s[:,1])-np.median(c[:,1]):.0f} | variation {(np.median(s[:,1])-np.median(c[:,1]))-(np.median(s[:,0])-np.median(c[:,0])):+.0f} ticks ; gain m_calculate {np.median(c[:,0])-np.median(c[:,1]):.0f}, gain mayo_sign {np.median(s[:,0])-np.median(s[:,1]):.0f}')
