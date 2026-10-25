import sys,glob,os,numpy as np,csv
root=sys.argv[1]; var=sys.argv[2]
rows={}
for f in sorted(glob.glob(f"{root}/*/*/csv_{var}/*.csv")):
    b=os.path.basename(f)[:-4]; m,s,*lv=b.split("_"); lv="_".join(lv)
    d=np.genfromtxt(f,delimiter=",",skip_header=1)
    first=d[:,1]; tb=d[:,2]; tx=d[:,3]
    r=tx/tb
    for k,msk in (("A2_1er",first==1),("off_1er",first==0)):
        rows.setdefault((m,lv,k),[]).append((np.median(r[msk]),np.median(tb[msk]),np.median(tx[msk]),msk.sum()))
    rows.setdefault((m,lv,"frac"),[]).append(first.mean())
for (m,lv),_ in sorted({(k[0],k[1]):0 for k in rows}.items()):
    a=np.array(rows[(m,lv,"A2_1er")]); o=np.array(rows[(m,lv,"off_1er")]); fr=np.mean(rows[(m,lv,"frac")])
    print(f"{m} {lv:14s} n_proc={len(a)} frac_A2_1er={fr:.3f} | ratio A2 1er={np.median(a[:,0]):.4f} off 1er={np.median(o[:,0]):.4f} diff={np.median(a[:,0])-np.median(o[:,0]):+.4f} | base: A2-1er={np.median(a[:,1]):.0f} off-1er={np.median(o[:,1]):.0f} | A2: A2-1er={np.median(a[:,2]):.0f} off-1er={np.median(o[:,2]):.0f} | procs diff>0: {(a[:,0]>o[:,0]).sum()}/{len(a)}")
