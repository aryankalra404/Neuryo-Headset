import numpy as np, json, trimesh, base64
from field import R, C, angles, rad
b=trimesh.load('body_sub1.ply',process=False); eyes=trimesh.load('eyes_sub1.ply',process=False)
S=np.load('sites.npy',allow_pickle=True).item(); meas=json.load(open('meas.json')); ear=json.load(open('ear.json'))
s=540.0/meas['circ']
def T(p): return (np.asarray(p)-C)*s
out_sites={}
for k,v in S.items():
    a,e=angles(v); out_sites[k]={'az':round(a,3),'el':round(e,3)}
pin=np.load('pin.npy'); V=b.vertices; pl=V[pin&(V[:,0]>0)]
c=pl.mean(0); w,U=np.linalg.eigh(np.cov((pl-c).T)); en=U[:,0]; en=en if en[0]>0 else -en   # ear-plane normal, pointing out
lobe=np.array(meas['lobe']); lobe_c=lobe+np.array([0,3,0])
et=np.array(meas['ear_top']); a,e=angles(et-C)
body=trimesh.Trimesh((V-C)*s,b.faces,process=False); eyem=trimesh.Trimesh((eyes.vertices-C)*s,eyes.faces,process=False)
for m in (body,eyem): m.visual=trimesh.visual.ColorVisuals(m)
scene=trimesh.Scene(); scene.add_geometry(body,node_name='head',geom_name='head'); scene.add_geometry(eyem,node_name='eyes',geom_name='eyes')
glb=scene.export(file_type='glb'); open('head.glb','wb').write(glb)
Rg=np.round(R*s*100).astype('<u2')
J={'about':'Neuryo v2 mannequin head. Mesh: MakeHuman 1.x base mesh (CC0 1.0), head, neck and shoulders, smoothed once, scaled to a 540 mm head circumference (mid-point of Indian adult male 548 mm and female 532 mm means, library P190). Units mm; y up, face +z, wearer\'s left +x; origin at the head centre used for az/el.',
   'circumference_mm':540.0,'nasion_inion_mm':round(meas['nasion_inion']*s,1),'lpa_rpa_mm':round(meas['lpa_rpa']*s,1),
   'method':'Sites measured on the skull surface with the 10-20 rules (IFCN, library P01): nasion-inion midline arc for Fpz, Fz, Cz, Pz, Oz; preauricular-Cz-preauricular arc for T7, T8; Fpz-T7-Oz circumference for Fp1, Fp2; Nz-preauricular-Iz ring for TP9, TP10. Inion is not visible on this smooth mannequin and is taken on the back midline at nasion height + 5 mm.',
   'tp_note':'On this mannequin the ear overhangs the standard TP9/TP10 point, so both were moved %.0f mm back along the same ring to clear the ear.'%(meas['tp_shift_mm']*s),
   'sites':out_sites,
   'lobe':{'p':T(lobe_c).round(2).tolist(),'n':en.round(4).tolist()},
   'earTop':{'az':round(a,2),'el':round(e,2)},
   'field':{'az0':0,'az_step':1,'naz':361,'el0':-90,'el_step':1,'nel':181,'scale':0.01,'u16_base64':base64.b64encode(Rg.tobytes()).decode()}}
json.dump(J,open('head.json','w'))
print('scale',round(s,4),'glb KB',len(glb)//1024,'json KB',len(json.dumps(J))//1024)
for k in ['Fpz','Fp1','Fz','Pz','TP9','EOG']: print(k,out_sites[k])
print('earTop',J['earTop'],'lobe',J['lobe'])
