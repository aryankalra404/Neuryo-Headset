import sys,glob;sys.path.insert(0,'/home/claude/kw')
from sx import *
seeed=parse(open(glob.glob('/tmp/claude-0/-home-claude/293baabf-271d-583c-b6d1-49586f1a156c/scratchpad/pcb/seeedlib/Seeed Studio XIAO Series Library/*.kicad_sym')[0]).read())
x=[s for s in kids(seeed,'symbol') if s[1]=='XIAO-ESP32-S3-SMD'][0]
for p in kids(x,'property'):
    if p[1]=='Footprint': p[2]='Neuryo_RevB:XIAO-ESP32-S3-SMD'
def prop(n,v,x=0,y=0,hide=True):
    e=['property',n,v,['at',str(x),str(y),'0']]
    if hide: e.append(['hide',Sym('yes')])
    e.append(['effects',['font',['size','1.27','1.27']]])
    return e
def pin(num,name,x,y,ang,typ='passive',ln=2.54):
    return ['pin',Sym(typ),Sym('line'),['at',str(x),str(y),str(ang)],['length',str(ln)],['name',name,['effects',['font',['size','1.27','1.27']]]],['number',num,['effects',['font',['size','1.27','1.27']]]]]
def poly(pts,fill='none'):
    return ['polyline',['pts']+[['xy',str(a),str(b)] for a,b in pts],['stroke',['width','0.254'],['type',Sym('default')]],['fill',['type',Sym(fill)]]]
def base(name,ref,val,fp,ds,desc):
    return ['symbol',name,['pin_names',['offset','0']],['exclude_from_sim',Sym('no')],['in_bom',Sym('yes')],['on_board',Sym('yes')],
            prop('Reference',ref,2.54,2.54,False),prop('Value',val,2.54,-2.54,False),prop('Footprint',fp),prop('Datasheet',ds),prop('Description',desc)]
q=base('2N7002','Q','2N7002','Neuryo_RevB:SOT-23','https://assets.nexperia.com/documents/data-sheet/2N7002.pdf','N-channel MOSFET 60 V 300 mA SOT-23 (pin 1 G, 2 S, 3 D)')
q.append(['symbol','2N7002_0_1',poly([(0.762,-1.778),(0.762,1.778)]),poly([(0,-1.27),(0,1.27)]),poly([(0,0),(-2.54,0)]),poly([(0.762,1.27),(2.54,1.27),(2.54,2.54)]),poly([(0.762,-1.27),(2.54,-1.27),(2.54,-2.54)]),poly([(0.762,0),(2.54,0),(2.54,-1.27)])])
q.append(['symbol','2N7002_1_1',pin('1','G',-5.08,0,0,'input'),pin('2','S',2.54,-5.08,90,'passive'),pin('3','D',2.54,5.08,270,'passive')])
c=base('Conn_1x04','J','Conn_1x04','Neuryo_RevB:PinHeader_1x04_P2.54_TSW','','1x4 2.54 mm header')
c.append(['symbol','Conn_1x04_0_1',['rectangle',['start','-1.27','5.08'],['end','1.27','-5.08'],['stroke',['width','0.254'],['type',Sym('default')]],['fill',['type',Sym('background')]]]])
c.append(['symbol','Conn_1x04_1_1']+[pin(str(k+1),'Pin_%d'%(k+1),-5.08,3.81-2.54*k,0,'passive',3.81) for k in range(4)])
pf=['symbol','PWR_FLAG',['power'],['pin_numbers',['hide',Sym('yes')]],['pin_names',['offset','0'],['hide',Sym('yes')]],['exclude_from_sim',Sym('no')],['in_bom',Sym('no')],['on_board',Sym('no')],
    prop('Reference','#FLG',0,1.905),prop('Value','PWR_FLAG',0,3.81,False),prop('Footprint',''),prop('Datasheet',''),prop('Description','Marks a net as driven by a power source (ERC only, no part)')]
pf.append(['symbol','PWR_FLAG_0_0',['pin',Sym('power_out'),Sym('line'),['at','0','0','90'],['length','0'],['name','~',['effects',['font',['size','1.27','1.27']]]],['number','1',['effects',['font',['size','1.27','1.27']]]]]])
pf.append(['symbol','PWR_FLAG_0_1',poly([(0,0),(0,1.27),(-1.016,1.905),(0,2.54),(1.016,1.905),(0,1.27)])])
lib=['kicad_symbol_lib',['version','20251024'],['generator','neuryo_revb_script'],x,q,c,pf]
open('/home/claude/kw/revb/Neuryo_RevB.kicad_sym','w').write(dump(numify(lib))+'\n')
