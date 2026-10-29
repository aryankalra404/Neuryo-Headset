import numpy as np, trimesh, json, base64
b=trimesh.load('body_sub1.ply',process=False); eyes=trimesh.load('eyes_sub1.ply',process=False)
both=trimesh.util.concatenate([b,eyes])
pin=np.load('pin.npy'); PL=b.vertices[pin&(b.vertices[:,0]>0)]
lo,hi=PL.min(0),PL.max(0)
EARBOX=(lo-np.array([4,4,4]), hi+np.array([10,4,6]))   # extra room toward the skull side and front (tragus/concha)
EARBOX[0][0]=58
C=np.array([0.0, 728.0, 69.0])
AZ=np.arange(0,361,1.0); EL=np.arange(-90,91,1.0)
def dirs(az,el):
    a=np.radians(az); e=np.radians(el)
    return np.stack([np.sin(a)*np.cos(e), np.sin(e), np.cos(a)*np.cos(e)],-1)
A,E=np.meshgrid(AZ,EL)           # shape (181,361)
D=dirs(A,E).reshape(-1,3)
R=np.full(len(D),np.nan)
from trimesh.ray.ray_triangle import RayMeshIntersector
rmi=RayMeshIntersector(both)
for k in range(0,len(D),1500):
    d=D[k:k+1500]; O=np.repeat(C[None],len(d),0)
    loc,ri,_=rmi.intersects_location(O,d,multiple_hits=True)
    if len(ri):
        dist=np.linalg.norm(loc-C,axis=1); sub=np.full(len(d),np.nan); np.fmax.at(sub,ri,dist); R[k:k+1500]=sub
    if k%15000==0: print(k,flush=True)
hitp=C+D*R[:,None]
def inbox(p,box,mirror=False):
    q=p.copy()
    if mirror: q[:,0]=-q[:,0]
    return np.all((q>=box[0])&(q<=box[1]),axis=1)
ear=inbox(hitp,EARBOX)|inbox(hitp,EARBOX,True)
R[ear]=np.nan
R=R.reshape(E.shape)
nan0=np.isnan(R).sum(); print('ear cells masked',ear.sum(),'nan total',nan0)
# Laplace fill (wrap in az)
mask=np.isnan(R); Rf=np.where(mask,np.nanmean(R),R)
for it in range(4000):
    up=np.roll(Rf,1,0); dn=np.roll(Rf,-1,0); lf=np.roll(Rf,1,1); rt=np.roll(Rf,-1,1)
    up[0]=Rf[0]; dn[-1]=Rf[-1]
    avg=(up+dn+lf+rt)/4; Rf[mask]=avg[mask]
Rf[:,360]=Rf[:,0]
np.save('R_raw.npy',Rf); np.save('C.npy',C)
json.dump({'earbox':[EARBOX[0].tolist(),EARBOX[1].tolist()],'pinna_lo':lo.tolist(),'pinna_hi':hi.tolist()},open('ear.json','w'))
print('R range',np.nanmin(Rf),np.nanmax(Rf))
