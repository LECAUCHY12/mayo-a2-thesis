"""Exemple jouet de MAYO (F16, v=2, o=1, m=2, k=2) selon les algorithmes 7 et 8 de la specification du 3e tour.
Signature : construction de A et y (avec le terme lineaire de Lambda), resolution, puis verification
independante P*(S)+L(Lambda,S)=t en evaluant directement la cle publique. Utilise : python3 -I exemple_jouet_mayo_tour3.py"""
def mul(a,b):
    r=0
    for i in range(4):
        if (b>>i)&1: r^=a<<i
    for i in range(7,3,-1):
        if (r>>i)&1: r^=0b10011<<(i-4)
    return r
def inv(a): return [b for b in range(1,16) if mul(a,b)==1][0]
h=lambda x:format(x,'X')

def X(l): return [h(a).lower() for a in l]
# field checks
print('roots z^2+z+8:',[a for a in range(16) if mul(a,a)^a^8==0])
O=[0xb,8]
P1=[[[8,9],[0,6]],[[8,0xa],[0,8]]]
P2=[[2,2],[0xb,0xc]]
def mv(A,x): return [ (lambda r: __import__('functools').reduce(lambda a,b:a^b,[mul(r[i],x[i]) for i in range(len(x))]))(A[j]) for j in range(len(A))]
# P3 = Upper(O^T(P1 O + P2))
P3=[]
for l in range(2):
    P1O=mv(P1[l],O); w=[P1O[i]^P2[l][i] for i in range(2)]
    P3.append(mul(O[0],w[0])^mul(O[1],w[1]))
print('P3',X(P3))
# full upper matrices 3x3
PF=[]
for l in range(2):
    M=[[0]*3 for _ in range(3)]
    for i in range(2):
        for j in range(2): M[i][j]=P1[l][i][j]
        M[i][2]=P2[l][i]
    M[2][2]=P3[l]; PF.append(M)
def p(l,y):
    r=0
    for i in range(3):
        for j in range(i,3): r^=mul(PF[l][i][j],mul(y[i],y[j]))
    return r
def P(y): return [p(0,y),p(1,y)]
def add(a,b): return [i^j for i,j in zip(a,b)]
def Pp(x,y): return add(add(P(add(x,y)),P(x)),P(y))
# check oil vanish
for x in range(1,16): assert P([mul(O[0],x),mul(O[1],x),x])==[0,0]
# E ops
def zm(a): return [mul(8,a[1]),a[0]^a[1]]
def Zpow(k,a):
    for _ in range(k): a=zm(a)
    return a
Zm=[[0,1],[1,2]]  # powers of z
def E(i,j,a): return Zpow(Zm[i][j],a)
LAM=[[3,1,2],[5,7,1]]
def Lin(s): # L(Lam,S)=sum_i E_i0 Lam s_i
    r=[0,0]
    for i in range(2):
        r=add(r,E(i,0,mv(LAM,s[i])))
    return r
def Pstar(S):
    r=add(E(0,0,P(S[0])),E(1,1,P(S[1])))
    return add(r,E(0,1,Pp(S[0],S[1])))
def verify_val(S): return add(Pstar(S),Lin(S))
# signing (spec alg 7)
t=[0xf,9]
V=[[2,3],[3,0xa]]
Lv=[[r[0],r[1]] for r in LAM]; Lo=[r[2] for r in LAM]
# L_l = (P1+P1^T)O + P2
Lmat=[]
for l in range(2):
    S_=[[P1[l][i][j]^P1[l][j][i] for j in range(2)] for i in range(2)]
    SO=mv(S_,O); Lmat.append([SO[i]^P2[l][i] for i in range(2)])
def vT_L(v): # row per equation l: scalar (o=1)
    return [mul(v[0],Lmat[l][0])^mul(v[1],Lmat[l][1]) for l in range(2)]
M=[vT_L(V[0]),vT_L(V[1])]  # M[i][l]
LamO=[mul(Lv[l][0],O[0])^mul(Lv[l][1],O[1])^Lo[l] for l in range(2)]
M[0]=[M[0][l]^LamO[l] for l in range(2)]
y=t[:]
for i in range(2):
    y=add(y,E(i,0,mv(Lv,V[i])))
def vPv(a,b):
    out=[]
    for l in range(2):
        r=0
        for i in range(2):
            for j in range(2): r^=mul(a[i],mul(P1[l][i][j],b[j]))
        out.append(r)
    return out
A=[[[0,0] for _ in range(2)] for _ in range(2)] # A[block][l]? store columns: A_col[i] = vector of length m
Acol=[[0,0],[0,0]]
for i in range(2):
    for j in range(i,2):
        u=vPv(V[i],V[i]) if i==j else add(vPv(V[i],V[j]),vPv(V[j],V[i]))
        y=add(y,E(i,j,u))
        Acol[i]=add(Acol[i],E(i,j,M[j]))
        if i!=j: Acol[j]=add(Acol[j],E(i,j,M[i]))
print('y',X(y),'Acol',[X(c) for c in Acol])
# solve 2x2: columns Acol[0],Acol[1]
a,c=Acol[0]; b,d=Acol[1]  # A=[[a,b],[c,d]] rows
det=mul(a,d)^mul(b,c); print('det',h(det))
x0=mul(inv(det),mul(d,y[0])^mul(b,y[1])); x1=mul(inv(det),mul(a,y[1])^mul(c,y[0]))
xs=[x0,x1]; print('x',X(xs))
S=[]
for i in range(2):
    S.append([V[i][0]^mul(O[0],xs[i]),V[i][1]^mul(O[1],xs[i]),xs[i]])
print('s',[X(s) for s in S])
print('Pstar',X(Pstar(S)),'Lin',X(Lin(S)),'sum',X(verify_val(S)),'t',X(t))
print('P(s1),P(s2),Pp',X(P(S[0])),X(P(S[1])),X(Pp(S[0],S[1])))
print('E terms',X(E(0,0,P(S[0]))),X(E(0,1,Pp(S[0],S[1]))),X(E(1,1,P(S[1]))))
print('Lam s',X(mv(LAM,S[0])),X(mv(LAM,S[1])),'E00 Lam s0',X(E(0,0,mv(LAM,S[0]))),'E10 Lam s1',X(E(1,0,mv(LAM,S[1]))))
print('LamO',X(LamO),'M',[X(m) for m in M],'L',[X(l) for l in Lmat], 'vPv', X(vPv(V[0],V[0])),X(vPv(V[1],V[1])),X(add(vPv(V[0],V[1]),vPv(V[1],V[0]))))
# tamper
S2=[s[:] for s in S]; S2[0][0]^=1; print('tamper',X(verify_val(S2)))
