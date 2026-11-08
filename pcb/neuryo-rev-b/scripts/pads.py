import sys,math;sys.path.insert(0,'/home/claude/kw')
from sx import *
X0,Y0=98.5011,80.0036
def fp_pads(pcb, refs=None):
    out=[]
    for fp in kids(pcb,'footprint'):
        ref=[p[2] for p in kids(fp,'property') if p[1]=='Reference'][0]
        if refs and ref not in refs: continue
        fa=kid(fp,'at'); fx,fy=float(fa[1]),float(fa[2]); fr=float(fa[3]) if len(fa)>3 else 0
        for pad in kids(fp,'pad'):
            pa=kid(pad,'at'); px,py=float(pa[1]),float(pa[2]); r=math.radians(-fr)
            gx=fx+px*math.cos(r)-py*math.sin(r); gy=fy+px*math.sin(r)+py*math.cos(r)
            n=kid(pad,'net'); nn=(n[2] if len(n)>2 else n[1]) if n else ''
            out.append((ref,str(pad[1]),nn,gx-X0,gy-Y0,[str(l) for l in kid(pad,'layers')[1:]],kid(pad,'size')[1:3]))
    return out
if __name__=='__main__':
    pcb=parse(open(sys.argv[1]).read())
    for p in fp_pads(pcb,sys.argv[2].split(',')): print('%s.%s %-12s %7.2f %7.2f %s %s'%p)
