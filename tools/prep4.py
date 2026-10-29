import numpy as np, json, trimesh
from field import *
b=trimesh.load('body_sub1.ply',process=False); eyes=trimesh.load('eyes_sub1.ply',process=False)
ear=json.load(open('ear.json'))
P=lambda az,el: surf(az,el)
# ---------- nasion: sagittal front profile ----------
els=np.arange(-40,60,0.25); prof=np.array([P(0,e) for e in els])
z=prof[:,2]
nose_i=np.argmax(np.where(els<5,z,-1e9)); nose_el=els[nose_i]
i=nose_i
while i+1<len(els) and z[i+1]<=z[i]+0.02: i+=1
nz_i=i; brow_i=i
Nz=prof[nz_i]; print('nose el',nose_el,'brow el',els[brow_i],'nasion el',els[nz_i], (Nz+C).round(1))
# ---------- inion: back profile at nasion height + 5 mm ----------
best=None
for e in np.arange(-60,60,0.05):
    q=P(180,e)
    if best is None or abs(q[1]-(Nz[1]+5))<abs(best[1]-(Nz[1]+5)): best=q
Iz=best
# ---------- preauricular: skull point just in front of the tragus at ear-canal height ----------
lo,hi=np.array(ear['pinna_lo']),np.array(ear['pinna_hi'])
canal_y=(lo[1]+hi[1])/2-2; tragus_z=hi[2]+3
tgt=np.array([75.0,canal_y,tragus_z])-C; az,el=angles(tgt); LPA=P(az,el)
az2,el2=angles(tgt*np.array([-1,1,1])); RPA=P(az2,el2)
print('LPA',(LPA+C).round(1),'RPA',(RPA+C).round(1),'Iz',(Iz+C).round(1))
# ---------- plane-section arcs on the field ----------
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
sag,Ls=section(Nz,Iz,np.array([0,200.0,0]),start=Nz,via=np.array([0,200.0,0]),end=Iz)
S={'Fpz':at(sag,Ls,.1),'Fz':at(sag,Ls,.3),'Cz':at(sag,Ls,.5),'Pz':at(sag,Ls,.7),'Oz':at(sag,Ls,.9)}
cor,Lc=section(LPA,RPA,S['Cz'],start=LPA,via=S['Cz'],end=RPA)
S['T7']=at(cor,Lc,.1); S['C3']=at(cor,Lc,.3); S['T8']=at(cor,Lc,.9); S['C4']=at(cor,Lc,.7)
ringL,Lr=section(S['Fpz'],S['Oz'],S['T7'],start=S['Fpz'],via=S['T7'],end=S['Oz'])
ringR,Lr2=section(S['Fpz'],S['Oz'],S['T8'],start=S['Fpz'],via=S['T8'],end=S['Oz'])
S['Fp1']=at(ringL,Lr,.1); S['AF7']=at(ringL,Lr,.2); S['F7']=at(ringL,Lr,.3); S['P7']=at(ringL,Lr,.7); S['O1']=at(ringL,Lr,.9)
S['Fp2']=at(ringR,Lr2,.1); S['AF8']=at(ringR,Lr2,.2); S['F8']=at(ringR,Lr2,.3)
circ=Lr[-1]+Lr2[-1]
infL,Li=section(Nz,Iz,LPA,start=Nz,via=LPA,end=Iz); infR,Li2=section(Nz,Iz,RPA,start=Nz,via=RPA,end=Iz)
fL=frac_of(infL,Li,LPA); fR=frac_of(infR,Li2,RPA); S['P9']=at(infL,Li,.7)
S['TP9_std']=at(infL,Li,(fL+0.7)/2); S['TP10_std']=at(infR,Li2,(fR+0.7)/2)
# This mannequin's ear overhangs the standard TP9/TP10 spot, so slide back along the same ring until a 9 mm pad clears the back of the ear by 4 mm.
clear_z=lo[2]-9-4-C[2]
f=(fL+0.7)/2
while at(infL,Li,f)[2]>clear_z and f<0.8: f+=0.002
S['TP9']=at(infL,Li,f); S['TP10']=at(infR,Li2,(fR-fL)+f); tp_shift=f-(fL+0.7)/2
print('TP9 slid back by %.1f%% of the ring (%.1f mm)'%(tp_shift*100, tp_shift*Li[-1]))
print('circumference (Fpz-T7-Oz-T8) mm',round(circ,1),'nasion-inion arc',round(Ls[-1],1),'LPA-RPA arc',round(Lc[-1],1),'LPA frac on inferior ring',round(fL,3))
# eye-channel site: about 20 mm below the left eye centre
le=eyes.vertices[eyes.vertices[:,0]>0].mean(0)
S['EOG']=P(*angles(np.array([le[0],le[1]-20,le[2]+4])-C))
S['Nz']=Nz; S['Iz']=Iz; S['LPA']=LPA; S['RPA']=RPA
# earlobe and ear top from the mesh itself
V=b.vertices; pin=np.load('pin.npy'); pl=V[pin&(V[:,0]>0)]; nl=b.vertex_normals[pin&(V[:,0]>0)]
low=pl[:,1]<pl[:,1].min()+7; lobe=pl[low].mean(0); lobe_n=nl[low][nl[low][:,0]>0].mean(0); lobe_n/=np.linalg.norm(lobe_n)
ear_top=pl[np.argmax(pl[:,1])]
np.save('sites.npy',{k:v for k,v in S.items()},allow_pickle=True)
json.dump({'circ':circ,'nasion_inion':Ls[-1],'lpa_rpa':Lc[-1],'lobe':(lobe).tolist(),'lobe_n':lobe_n.tolist(),'ear_top':ear_top.tolist(),'ear_back_z':float(pl[:,2].min()),'eyeL':le.tolist(),'tp_shift_mm':float(tp_shift*Li[-1])},open('meas.json','w'),indent=1)
for k in ['Iz','Nz','Fpz','Fp1','Fp2','Fz','Cz','Pz','Oz','T7','T8','TP9_std','TP9','TP10','EOG','LPA']:
    a,e=angles(S[k]); print(k,'az %.1f el %.1f'%(a,e),(S[k]+C).round(1))
print('lobe',lobe.round(1),'n',lobe_n.round(2),'ear top',ear_top.round(1))
