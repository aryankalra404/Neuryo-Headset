import sys; sys.path.insert(0,'.')
import numpy as np, trimesh
def load_groups(path, groups):
    V=[]; out={g:[] for g in groups}; g=None
    for line in open(path):
        if line.startswith('v '): V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('g '): g=line.split(None,1)[1].strip()
        elif line.startswith('f ') and g in out:
            idx=[int(t.split('/')[0])-1 for t in line.split()[1:]]
            if len(idx)==4: out[g]+= [[idx[0],idx[1],idx[2]],[idx[0],idx[2],idx[3]]]
            else: out[g].append(idx[:3])
    V=np.array(V)*100.0
    return {k: trimesh.Trimesh(V, np.array(f), process=True) for k,f in out.items()}
M=load_groups('base.obj',['body','helper-l-eye','helper-r-eye'])
body=M['body']
print('l-eye x mean', M['helper-l-eye'].vertices[:,0].mean(), 'faces eye', len(M['helper-l-eye'].faces))
b=trimesh.intersections.slice_mesh_plane(body,[0,1,0],[0,470,0],cap=True)
b=trimesh.intersections.slice_mesh_plane(b,[-1,0,0],[185,0,0],cap=True)
b=trimesh.intersections.slice_mesh_plane(b,[1,0,0],[-185,0,0],cap=True)
print('crop faces',len(b.faces),'watertight',b.is_watertight)
v,f=trimesh.remesh.subdivide_loop(b.vertices,b.faces,iterations=1)
b1=trimesh.Trimesh(v,f,process=True)
print('sub1 faces',len(b1.faces))
eyes=[]
for k in ['helper-l-eye','helper-r-eye']:
    e=M[k]; v,f=trimesh.remesh.subdivide_loop(e.vertices,e.faces,iterations=1); eyes.append(trimesh.Trimesh(v,f,process=True))
b1.export('body_sub1.ply'); trimesh.util.concatenate(eyes).export('eyes_sub1.ply')
