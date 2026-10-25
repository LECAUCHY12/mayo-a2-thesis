import glob,os,numpy as np,sys
root=sys.argv[1]
# 1 equilibrage et aleatoire de la sequence
tot=0;n1=0;trans=np.zeros((2,2));maxrun=0
for f in glob.glob(f"{root}/*/*/csv_safe/m1_*_P1t_times_Vt.csv"):
    d=np.genfromtxt(f,delimiter=",",skip_header=1); x=d[:,1].astype(int)
    tot+=len(x);n1+=x.sum()
    for a,b in zip(x[:-1],x[1:]): trans[a,b]+=1
print("P1t m1: paires",tot,"A2 en premier",n1,f"({n1/tot:.4f})")
P=trans/trans.sum(1,keepdims=True);print("P(suivant | precedent):",P.round(4).tolist())
# 2 par campagne, par processus, ordre
for s in ["s1","s2","s3b","s4"]:
    D=[]
    for f in sorted(glob.glob(f"{root}/{s}/*/csv_safe/m1_*_P1t_times_Vt.csv")):
        d=np.genfromtxt(f,delimiter=",",skip_header=1);r=d[:,3]/d[:,2];m=d[:,1]==1
        D.append((np.median(r[m]),np.median(r[~m]),np.median(r)))
    D=np.array(D);print(s,"ratio A2-1er",D[:,0].round(4).tolist(),"off-1er",D[:,1].round(4).tolist(),"moyenne(deux ordres)",((D[:,0]+D[:,1])/2).mean().round(4),"mediane poolee",D[:,2].mean().round(4))
# 3 effet position: bras 2e vs 1er, relatif
for lv in ["P1t_times_Vt","P1_times_Vt"]:
  for m in ["m1","m5"]:
    b1=[];b2=[];x1=[];x2=[]
    for f in glob.glob(f"{root}/*/*/csv_safe/{m}_*_{lv}.csv"):
        d=np.genfromtxt(f,delimiter=",",skip_header=1);o=d[:,1]==1
        x1.append(np.median(d[o,3]));x2.append(np.median(d[~o,3]))   # A2: 1er / 2e
        b1.append(np.median(d[~o,2]));b2.append(np.median(d[o,2]))   # off: 1er / 2e
    print(f"{m} {lv}: officiel 1er={np.median(b1):.0f} 2e={np.median(b2):.0f} ({np.median(b2)/np.median(b1)-1:+.2%}) ; A2 1er={np.median(x1):.0f} 2e={np.median(x2):.0f} ({np.median(x2)/np.median(x1)-1:+.2%})")
