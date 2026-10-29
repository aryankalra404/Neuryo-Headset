import numpy as np, trimesh, json
b=trimesh.load('body_sub1.ply',process=False); eyes=trimesh.load('eyes_sub1.ply',process=False)
V=b.vertices; N=b.vertex_normals
# ---- pinna: thin flap test inside an ear box ----
box=(np.abs(V[:,0])>55)&(V[:,1]>660)&(V[:,1]<775)&(V[:,2]>5)&(V[:,2]<85)
idx=np.where(box)[0]
org=V[idx]-N[idx]*0.05; dirs=-N[idx]
loc,ri,_=b.ray.intersects_location(org,dirs,multiple_hits=False)
dist=np.full(len(idx),np.inf); dist[ri]=np.linalg.norm(loc-org[ri],axis=1)
thin=idx[dist<14]
pin=np.zeros(len(V),bool); pin[thin]=True
# grow by one ring to include rim
for _ in range(2):
    fm=pin[b.faces].any(1); pin[np.unique(b.faces[fm])]=True; pin&=box|pin
print('pinna verts',pin.sum(),'L',(pin&(V[:,0]>0)).sum(),'R',(pin&(V[:,0]<0)).sum())
L=pin&(V[:,0]>0); PL=V[L]
print('left pinna bbox',PL.min(0).round(1),PL.max(0).round(1))
np.save('pin.npy',pin)
