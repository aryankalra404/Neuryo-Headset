import numpy as np
R=np.load('R_raw.npy'); C=np.load('C.npy')
def cr(p0,p1,p2,p3,t):
    return 0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
def rad(az,el,Rg=None):
    Rg=R if Rg is None else Rg
    az=np.mod(az,360.0); x=az; y=np.clip(el,-90,90)+90
    i=int(np.floor(x)); j=int(np.floor(y)); tx=x-i; ty=y-j
    def g(ii,jj): return Rg[min(max(jj,0),180), ii%360]
    rows=[cr(g(i-1,jj),g(i,jj),g(i+1,jj),g(i+2,jj),tx) for jj in (j-1,j,j+1,j+2)]
    return cr(*rows,ty)
def dvec(az,el):
    a=np.radians(az); e=np.radians(el); return np.array([np.sin(a)*np.cos(e),np.sin(e),np.cos(a)*np.cos(e)])
def surf(az,el,Rg=None): return dvec(az,el)*rad(az,el,Rg)   # relative to C
def angles(p):  # p relative to C
    r=np.linalg.norm(p); return float(np.degrees(np.arctan2(p[0],p[2]))%360), float(np.degrees(np.arcsin(p[1]/r)))
