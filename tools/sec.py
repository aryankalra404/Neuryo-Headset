def section(p0,p1,p2,n_samples=4000,start=None,via=None,end=None):
    n=np.cross(p1-p0,p2-p0); n/=np.linalg.norm(n)
    M=-np.dot(-p0,n)*n*0  # projection of origin (C) onto plane
    M=np.dot(p0,n)*n
    e1=start-M; e1-=np.dot(e1,n)*n; e1/=np.linalg.norm(e1); e2=np.cross(n,e1)
    if np.dot(via-M,e2)<0: e2=-e2
    def hit(t):
        u=np.cos(t)*e1+np.sin(t)*e2; lo_,hi_=0.0,400.0
        for _ in range(60):
            s=(lo_+hi_)/2; q=M+s*u; a,e=angles(q)
            if np.linalg.norm(q)<rad(a,e): lo_=s
            else: hi_=s
        return M+lo_*u
    ue=end-M; ue-=np.dot(ue,n)*n; t_end=np.arctan2(np.dot(ue,e2),np.dot(ue,e1)) % (2*np.pi)
    ts=np.linspace(0,t_end,n_samples); pts=np.array([hit(t) for t in ts])
    L=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))])
    return pts,L
def at(pts,L,f): return pts[np.searchsorted(L,f*L[-1])]
def frac_of(pts,L,p): i=np.argmin(np.linalg.norm(pts-p,axis=1)); return L[i]/L[-1]
