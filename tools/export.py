# Writes the shared mannequin head used by every design: designs/shared/head/head.glb, head.json, and docs/head-sites.md.
import numpy as np, json, trimesh, base64, sys, os
from field import R, C, angles
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
b=trimesh.load('body_sub1.ply',process=False); eyes=trimesh.load('eyes_sub1.ply',process=False)
meas=json.load(open('meas.json')); A=np.load('all1010.npy',allow_pickle=True).item()
s=540.0/meas['circ']
def T(p): return (np.asarray(p)-C)*s
def site(p):
    a,e=angles(p); q=(p*s).round(1); return {'az':round(a,3),'el':round(e,3),'xyz':q.tolist()}
pin=np.load('pin.npy'); V=b.vertices; pl=V[pin&(V[:,0]>0)]
c=pl.mean(0); w,U=np.linalg.eigh(np.cov((pl-c).T)); en=U[:,0]; en=en if en[0]>0 else -en
lobe_c=np.array(meas['lobe'])+np.array([0,3,0]); et=np.array(meas['ear_top']); ea,ee=angles(et-C)
body=trimesh.Trimesh((V-C)*s,b.faces,process=True)
body=trimesh.graph.smooth_shade(body,angle=np.radians(40))     # keep the cut edges crisp, everything else smooth
eyem=trimesh.Trimesh((eyes.vertices-C)*s,eyes.faces,process=True)
scene=trimesh.Scene(); scene.add_geometry(body,node_name='head',geom_name='head'); scene.add_geometry(eyem,node_name='eyes',geom_name='eyes')
os.makedirs(OUT,exist_ok=True); open(os.path.join(OUT,'head.glb'),'wb').write(scene.export(file_type='glb'))
Rg=np.round(R*s*100).astype('<u2')
order=['Nz','Fpz','Fp1','Fp2','AFz','AF3','AF4','AF7','AF8','Fz','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','FCz','FC1','FC2','FC3','FC4','FC5','FC6','FT7','FT8','FT9','FT10',
       'Cz','C1','C2','C3','C4','C5','C6','T7','T8','T9','T10','LPA','RPA','CPz','CP1','CP2','CP3','CP4','CP5','CP6','TP7','TP8','TP9','TP10',
       'Pz','P1','P2','P3','P4','P5','P6','P7','P8','P9','P10','POz','PO3','PO4','PO7','PO8','PO9','PO10','Oz','O1','O2','Iz']
sites={k:site(A['sites'][k]) for k in order}
extra={k:site(v) for k,v in A['extra'].items()}
J={'about':"Shared Neuryo mannequin head. Mesh: MakeHuman 1.x base mesh (CC0 1.0): head, ears, eyes, neck and shoulders, smoothed once then cut flat. Scaled to a 540 mm head circumference (mid-point of Indian adult male 548 mm and female 532 mm means, Neuryo-Research P190). Units mm; y up, face +z, wearer's left +x; origin at the head centre used for az/el. Built by tools/ (see docs/head.md).",
   'circumference_mm':540.0,'nasion_inion_mm':round(meas['nasion_inion']*s,1),'lpa_rpa_mm':round(meas['lpa_rpa']*s,1),
   'method':'10-10 sites measured on the skull surface (ears masked out): nasion-inion midline arc in 10% steps; preauricular-Cz-preauricular arc for T7/T8; Fpz-T7-Oz circumference in 10% steps; each lateral row (AF, F, FC, C, CP, P, PO) as an arc from its left circumference point through its midline point to the right one, in equal steps; Nz-preauricular-Iz ring for the 9/10 row. Inion is not visible on this smooth mannequin and is taken on the back midline at nasion height + 5 mm.',
   'sites':sites,
   'extra':extra,
   'extra_notes':{'TP9_clear':'TP9 moved %.0f mm back along its ring so a 9 mm pad clears this mannequin\'s ear.'%(meas['tp_shift_mm']*s),'TP10_clear':'Mirror of TP9_clear.','EOG_L':'About 20 mm below the centre of the left eye (vertical EOG).','EOG_R':'About 20 mm below the centre of the right eye.'},
   'lobe':{'p':T(lobe_c).round(2).tolist(),'n':en.round(4).tolist(),'note':'Left earlobe centre and the ear-plane normal (points outward).'},
   'earTop':{'az':round(ea,2),'el':round(ee,2)},
   'field':{'about':'Skull radius from the origin every 1 degree, ears masked and filled. Read with bicubic interpolation.','az0':0,'az_step':1,'naz':361,'el0':-90,'el_step':1,'nel':181,'scale':0.01,'u16_base64':base64.b64encode(Rg.tobytes()).decode()}}
json.dump(J,open(os.path.join(OUT,'head.json'),'w'))
print('scale',round(s,4),'sites',len(sites),'extra',list(extra))
