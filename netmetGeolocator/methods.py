import numpy as np
from . import shapes as gx
from scipy.optimize import minimize, fmin_cobyla




def error(x, y):
    return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2 + (x[2] - y[2]) ** 2) ** .5




def sum_error(x, c, r):
    l = len(c)
    e = 0
    for i in range(l):
        e = e + (error(x, c[i].xyz()) - r[i]) ** 2
    return e



def target_matrixLse(cA):
    R=6371
    A=[]
    b = []
    for cc in cA:
        c=cc.c
        d=cc.r
        x=c.x
        y=c.y
        z=c.z
        Am = 2*x
        Bm = 2*y
        Cm = 2*z
        Dm = R*R + (pow(x,2)+pow(y,2)+pow(z,2)) - pow(d,2)
        A += [[Am,Bm,Cm]]
        b += [[Dm]]
    A = np.array(A)
    b = np.array(b)
    AT = A.T
    ATA = np.matmul(AT,A)
    ATA_inv = np.linalg.inv(ATA)
    Aplus = np.matmul(ATA_inv,AT)
    x = np.matmul(Aplus,b)
    print("x= "+str(x[0])+" y= "+str(x[1])+" z= "+str(x[2]))
    return gx.cartesianPoint(x[0][0],x[1][0],x[2][0])
    # (_,_,v) = num.linalg.svd(A)
    # w = v[3,:]
    # w /= w[3]
    # return gx.cartesianPoint(w[0],w[1],w[2])
    # print (w)


def target_svd(cA):
    R=6371
    A=[]
    for cc in cA:
        c=cc.c
        d=cc.r
        x=c.x
        y=c.y
        z=c.z
        Am = -2*x
        Bm = -2*y
        Cm = -2*z
        Dm = R*R + (pow(x,2)+pow(y,2)+pow(z,2)) - pow(d,2)
        A += [[Am,Bm,Cm,Dm]]
    A = np.array(A)
    (_,_,v) = np.linalg.svd(A)
    w = v[3,:]
    w /= w[3]
    return gx.cartesianPoint(w[0],w[1],w[2])


def target_lse(cA):
    l = len(cA)
    r = [w.r for w in cA]
    c = [w.c for w in cA]
    S = sum(r)
    # W = [(S - w) / ((l - 1) * S) for w in r]
    p0 = gx.cartesianPoint(0, 0, 0)  # Initialized point
    # print("abc")
    # for i in range(l):
    #     # print("abc1")
    #     p0 = p0 + W[i] * c[i]

    x0 = np.array([p0.x, p0.y, p0.z])
    # print('LSE Geolocating...')
    res = minimize(sum_error, x0, args=(c, r), method='BFGS')
    ans = res.x
    print(ans[0],ans[1],ans[2])
    return gx.cartesianPoint(ans[0],ans[1],ans[2])
