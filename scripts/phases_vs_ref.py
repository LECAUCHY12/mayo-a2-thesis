# Compare le rapport A2/officiel de mayo_sign MESURE AVEC sondes (phases_m5_s*.csv) et SANS sondes (csv_ref/m5_s*_mayo_sign.csv).
# Unite statistique : le processus. Usage : python3 -I phases_vs_ref.py <dossier_phases_...>
import sys,glob,numpy as np
rng=np.random.default_rng(3)
d=sys.argv[1]
def ratios(files,col_b,col_x):
    out=[]
    for f in files:
        a=np.genfromtxt(f,delimiter=',',names=True,comments='#')
        out.append(float(np.median(a[col_x]/a[col_b])))
    return np.array(out)
def ci(v):
    i=rng.integers(0,len(v),(4000,len(v))); return np.percentile(np.median(v[i],axis=1),[2.5,97.5])
for m in ('5','1','2'):
    fp=sorted(glob.glob(f'{d}/csv_phases/phases_m{m}_s*.csv'))
    if fp:
        r=ratios(fp,'tot_b','tot_x'); lo,hi=ci(r)
        print(f'MAYO-{m} AVEC sondes : {len(r)} processus, rapport mayo_sign {np.median(r):.4f} [{r.min():.4f}-{r.max():.4f}] IC95 entre processus [{lo:.4f};{hi:.4f}]')
fr=sorted(glob.glob(f'{d}/csv_ref/m5_s*_mayo_sign.csv'))
if fr:
    r=ratios(fr,'t_base','t_xmm'); lo,hi=ci(r)
    print(f'MAYO-5 SANS sondes (reference) : {len(r)} processus, rapport mayo_sign {np.median(r):.4f} [{r.min():.4f}-{r.max():.4f}] IC95 entre processus [{lo:.4f};{hi:.4f}]')
for lv in ('m_calculate','P1_times_Vt','P1t_times_Vt'):
    fr=sorted(glob.glob(f'{d}/csv_ref/m5_s*_{lv}.csv'))
    if fr:
        r=ratios(fr,'t_base','t_xmm'); print(f'MAYO-5 SANS sondes, niveau {lv} : rapport {np.median(r):.4f} [{r.min():.4f}-{r.max():.4f}] ({len(r)} processus)')
