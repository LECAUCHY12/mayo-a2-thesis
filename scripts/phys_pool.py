import csv, glob, sys, numpy as np
rng=np.random.default_rng(7)
levels=['P1_times_Vt','P1t_times_Vt','m_calculate','mayo_sign']
root=sys.argv[1]
def load(f):
    d=list(csv.DictReader(open(f))); return np.array([float(x['t_base']) for x in d]),np.array([float(x['t_xmm']) for x in d])
for var in ['safe','default']:
    print('#####',var)
    for v in [1,5,2,3]:
        for lv in levels:
            fs=sorted(glob.glob(f'{root}/*/*/csv_{var}/m{v}_s*_{lv}.csv'))
            if not fs: continue
            B=[];X=[];R=[]
            for f in fs:
                b,x=load(f); B.append(np.median(b));X.append(np.median(x));R.append(np.median(x/b))
            B,X,R=map(np.array,(B,X,R))
            idx=rng.integers(0,len(R),(5000,len(R))); m=np.median(R[idx],axis=1); lo,hi=np.percentile(m,[2.5,97.5])
            print(f"MAYO-{v} {lv:13s} n_proc={len(R)} base_med={np.median(B):.0f} [{B.min():.0f}-{B.max():.0f}] a2_med={np.median(X):.0f} [{X.min():.0f}-{X.max():.0f}] ratio_med={np.median(R):.4f} [{R.min():.4f}-{R.max():.4f}] IC95_entre_proc=[{lo:.4f};{hi:.4f}] gain={(1-np.median(R))*100:.2f}%")
