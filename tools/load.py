import numpy as np
def load(path):
    V=[]; faces=[]; g=None
    for line in open(path):
        if line.startswith('v '): V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('g '): g=line.split(None,1)[1].strip()
        elif line.startswith('f ') and g=='body':
            idx=[int(t.split('/')[0])-1 for t in line.split()[1:]]
            if len(idx)==4: faces += [[idx[0],idx[1],idx[2]],[idx[0],idx[2],idx[3]]]
            elif len(idx)==3: faces.append(idx)
    return np.array(V), np.array(faces)
