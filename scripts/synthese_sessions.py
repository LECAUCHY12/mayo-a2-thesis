# Synthese S1/S2 : decomposition de la variabilite (entre paires / entre processus / entre campagnes / entre sessions)
# et effet d'ordre, avec le PROCESSUS comme unite statistique. Usage : python3 -I synthese_sessions.py <racine_S1> <racine_S2> [variante=safe]
import sys,glob,os,re,numpy as np
rng=np.random.default_rng(2026)
R1,R2=sys.argv[1],sys.argv[2]; VAR=sys.argv[3] if len(sys.argv)>3 else 'safe'
LV=['P1_times_Vt','P1t_times_Vt','m_calculate','mayo_sign']
def mad_sd(x): return 1.4826*np.median(np.abs(x-np.median(x)))
def load(root,m,lv):
    out=[]
    for f in sorted(glob.glob(f'{root}/**/csv_{VAR}/m{m}_s*_{lv}.csv',recursive=True)):
        d=np.genfromtxt(f,delimiter=',',skip_header=1); o=d[:,1]==1; r=d[:,3]/d[:,2]
        camp=re.search(r'/(s1|s2|s3b|s4|s5)/',f); camp=camp.group(1) if camp else '?'
        out.append(dict(camp=camp,med=np.median(r),sd_pairs=mad_sd(r),n=len(r),ra=np.median(r[o]),rb=np.median(r[~o]),
                        ci_pairs=np.percentile([np.median(r[rng.integers(0,len(r),len(r))]) for _ in range(300)],[2.5,97.5])))
    return out
def ci_med(v):
    v=np.asarray(v); i=rng.integers(0,len(v),(5000,len(v))); return np.percentile(np.median(v[i],axis=1),[2.5,97.5])
print(f'##### variante {VAR}  (unite statistique = processus ; 3 001 paires par processus)')
print('niveau | session | n_proc | rapport (mediane des processus) | ecart-type ROBUSTE entre paires (dans un processus, median.) | ecart-type entre processus | IC95 entre processus | IC95 "naif" sur les paires d un processus (median.) | ecart-type entre campagnes (S1)')
res={}
for m in (1,5,2,3):
    for lv in LV:
        if m in (2,3) and lv not in ('m_calculate','mayo_sign'): continue
        for name,root in (('S1',R1),('S2',R2)):
            P=load(root,m,lv)
            if not P: continue
            med=np.array([p['med'] for p in P]); lo,hi=ci_med(med)
            naif=np.median([p['ci_pairs'][1]-p['ci_pairs'][0] for p in P])/2
            camp=''
            if name=='S1':
                cm=[np.mean([p['med'] for p in P if p['camp']==c]) for c in sorted({p['camp'] for p in P})]
                camp=f'{np.std(cm,ddof=1):.5f} ({len(cm)} campagnes)'
            res[(m,lv,name)]=P
            print(f'MAYO-{m} {lv:13s} | {name} | {len(P):2d} | {np.median(med):.4f} | {np.median([p["sd_pairs"] for p in P]):.4f} | {np.std(med,ddof=1):.5f} | [{lo:.4f};{hi:.4f}] | +-{naif:.5f} | {camp}')
print('\n##### entre sessions : S2 - S1 (difference des rapports, bootstrap sur les processus de chaque session)')
for (m,lv,name) in list(res):
    if name!='S1' or (m,lv,'S2') not in res: continue
    a=np.array([p['med'] for p in res[(m,lv,'S1')]]); b=np.array([p['med'] for p in res[(m,lv,'S2')]])
    ia=rng.integers(0,len(a),(5000,len(a))); ib=rng.integers(0,len(b),(5000,len(b)))
    dd=np.median(b[ib],axis=1)-np.median(a[ia],axis=1); lo,hi=np.percentile(dd,[2.5,97.5])
    se_s1=np.std(a,ddof=1)/np.sqrt(len(a)); se_s2=np.std(b,ddof=1)/np.sqrt(len(b))
    print(f'MAYO-{m} {lv:13s} S1={np.median(a):.4f} S2={np.median(b):.4f} diff={np.median(b)-np.median(a):+.4f} IC95=[{lo:+.4f};{hi:+.4f}]  erreur-type S1={se_s1:.5f} S2={se_s2:.5f}')
print('\n##### effet d ordre : rapport A2/officiel selon l ordre d execution ; par processus : (A2 en 1er) - (officiel en 1er)')
print('niveau | session | rapport A2 1er | rapport officiel 1er | ecart median par processus [IC95 entre processus] | processus avec ecart>0 | moyenne des deux ordres | rapport global')
for (m,lv,name),P in res.items():
    if m in (2,3) and lv=='mayo_sign' and False: continue
    ra=np.array([p['ra'] for p in P]); rb=np.array([p['rb'] for p in P]); dd=ra-rb; lo,hi=ci_med(dd)
    print(f'MAYO-{m} {lv:13s} | {name} | {np.median(ra):.4f} | {np.median(rb):.4f} | {np.median(dd):+.4f} [{lo:+.4f};{hi:+.4f}] | {(dd>0).sum()}/{len(dd)} | {(np.median(ra)+np.median(rb))/2:.4f} | {np.median([p["med"] for p in P]):.4f}')
