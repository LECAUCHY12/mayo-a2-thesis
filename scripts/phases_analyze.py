# Analyse de la decomposition instrumentee de mayo_sign (A/B apparie). Unite statistique : le PROCESSUS.
# Usage : python3 -I phases_analyze.py <dossier_ou_prefixe_csv...>   (fichiers phases_m<k>_s<graine>.csv)
import sys,glob,re,numpy as np
rng=np.random.default_rng(5)
files=[]
for a in sys.argv[1:]: files+=sorted(glob.glob(a)) if any(c in a for c in '*?') else [a]
def load(f):
    names={}
    for line in open(f):
        if line.startswith('# '):
            for kv in line[2:].strip().split(';'):
                if '=' in kv: k,v=kv.split('=',1); names[int(k)]=v
            break
    d=np.genfromtxt(f,delimiter=',',names=True,comments='#')
    return names,d
TOP=[0,1,2,3,4,5,6,7,8,9,10,11]
def ci(v):
    v=np.asarray(v); i=rng.integers(0,len(v),(4000,len(v))); return np.percentile(np.median(v[i],axis=1),[2.5,97.5])
def run(files,label,mask_fn=None):
    rows=[]
    for f in files:
        names,d=load(f)
        if mask_fn is not None: m=mask_fn(d)
        else: m=np.ones(len(d),bool)
        if m.sum()<30: continue
        r={'n':int(m.sum()),'att':float(np.mean(d['att_b'][m])),'ratio':float(np.median(d['tot_x'][m]/d['tot_b'][m])),'tb':float(np.median(d['tot_b'][m])),'tx':float(np.median(d['tot_x'][m]))}
        for k in names:
            cb=d[f'cb_{k}'][m];cx=d[f'cx_{k}'][m];nb=d[f'nb_{k}'][m];nx=d[f'nx_{k}'][m]
            r[k]=(np.median(cb),np.median(cx),np.median(cx-cb),np.mean(cx-cb),np.mean(nb),np.mean(nx))
        top_b=sum(d[f'cb_{k}'][m] for k in TOP if k in names); top_x=sum(d[f'cx_{k}'][m] for k in TOP if k in names)
        r['res']=(np.median(d['tot_b'][m]-top_b),np.median(d['tot_x'][m]-top_x),np.mean((d['tot_x'][m]-top_x)-(d['tot_b'][m]-top_b)))
        r['dtot']=np.mean(d['tot_x'][m]-d['tot_b'][m])
        rows.append(r)
    if not rows: print(label,'aucun processus'); return
    print(f'\n=== {label} : {len(rows)} processus, {sum(r["n"] for r in rows)} signatures ===')
    rb=[r['ratio'] for r in rows];lo,hi=ci(rb)
    print(f'total mayo_sign (avec sondes) : officiel {np.median([r["tb"] for r in rows]):.0f}  A2 {np.median([r["tx"] for r in rows]):.0f}  rapport {np.median(rb):.4f} [{min(rb):.4f}-{max(rb):.4f}] IC95 entre processus [{lo:.4f};{hi:.4f}] ; tentatives/signature {np.mean([r["att"] for r in rows]):.3f}')
    print(f'{"phase":42s} {"appels/sig":>10s} {"officiel":>10s} {"A2":>10s} {"med(x-b)":>10s} {"moy(x-b)":>10s} {"part de la moy(x-b) totale":>26s}')
    names=load(files[0])[0]
    dt=np.median([r['dtot'] for r in rows])
    for k in sorted(names):
        v=np.array([r[k] for r in rows]); 
        print(f'{names[k][:42]:42s} {np.median(v[:,4]):10.2f} {np.median(v[:,0]):10.0f} {np.median(v[:,1]):10.0f} {np.median(v[:,2]):10.0f} {np.median(v[:,3]):10.0f} {100*np.median(v[:,3])/dt:25.1f}%')
    v=np.array([r['res'] for r in rows])
    print(f'{"[reste non attribue = total - somme des 12 sondes de niveau 1]":42s} {"":>10s} {np.median(v[:,0]):10.0f} {np.median(v[:,1]):10.0f} {"":>10s} {np.median(v[:,2]):10.0f} {100*np.median(v[:,2])/dt:25.1f}%')
    print(f'{"[total mayo_sign : moyenne de (x-b)]":42s} {"":>10s} {"":>10s} {"":>10s} {"":>10s} {dt:10.0f}')
run(files,'toutes signatures')
run(files,'tentatives == 1',lambda d:(d['att_b']==1))
run(files,'tentatives >= 2',lambda d:(d['att_b']>=2))
run(files,'A2 execute en premier',lambda d:(d['xmm_first']==1))
run(files,'officiel execute en premier',lambda d:(d['xmm_first']==0))
