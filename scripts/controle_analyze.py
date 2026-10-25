# Analyse du controle des sondes. Unite statistique : le PROCESSUS. Usage : python3 -I controle_analyze.py <dossier_controle>
import sys,glob,re,numpy as np
rng=np.random.default_rng(9)
D=sys.argv[1]
def ci(v):
    v=np.asarray(v); i=rng.integers(0,len(v),(4000,len(v))); return np.percentile(np.median(v[i],axis=1),[2.5,97.5])
def load(f): return np.genfromtxt(f,delimiter=',',names=True,comments='#')
print('configuration | n_proc | total officiel | total A2 | rapport A2/officiel [min-max] IC95 entre processus | gain | reste(=total-sonde) officiel/A2 si sonde unique')
for c in ('plain','none','esk','mcalc','all'):
    fs=sorted(glob.glob(f'{D}/csv_ctrl/cfg_{c}_m5_s*.csv'))
    if not fs: continue
    R=[];TB=[];TX=[];RB=[];RX=[]
    for f in fs:
        a=load(f); R.append(np.median(a['tot_x']/a['tot_b'])); TB.append(np.median(a['tot_b'])); TX.append(np.median(a['tot_x']))
        names=a.dtype.names
        if c=='esk' and 'cb_11' in names: RB.append(np.median(a['tot_b']-a['cb_11'])); RX.append(np.median(a['tot_x']-a['cx_11']))
        if c=='mcalc' and 'cb_6' in names: RB.append(np.median(a['tot_b']-a['cb_6'])); RX.append(np.median(a['tot_x']-a['cx_6']))
    lo,hi=ci(R); rest=f'{np.median(RB):.0f} / {np.median(RX):.0f}  (ecart {np.median(RX)-np.median(RB):+.0f})' if RB else ''
    print(f'{c:6s} | {len(R):2d} | {np.median(TB):.0f} | {np.median(TX):.0f} | {np.median(R):.4f} [{min(R):.4f}-{max(R):.4f}] [{lo:.4f};{hi:.4f}] | {100*(1-np.median(R)):.2f} % | {rest}')
fr=sorted(glob.glob(f'{D}/csv_ref/m5_s*_mayo_sign.csv'))
if fr:
    R=[np.median(load(f)['t_xmm']/load(f)['t_base']) for f in fr]; lo,hi=ci(R)
    print(f'ref(mayo_tail_ab) | {len(R)} | | | {np.median(R):.4f} [{min(R):.4f}-{max(R):.4f}] [{lo:.4f};{hi:.4f}] | {100*(1-np.median(R)):.2f} %')
