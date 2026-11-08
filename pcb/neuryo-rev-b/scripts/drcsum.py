import json,collections,sys,re
d=json.load(open(sys.argv[1]))
X0,Y0=98.5011,80.0036
c=collections.Counter((v['severity'],v['type']) for v in d['violations'])
print(sorted(c.items(),key=lambda x:-x[1]))
skip=set(sys.argv[2].split(',')) if len(sys.argv)>2 else set()
for v in d['violations']:
    if v['type'] in skip: continue
    p=v['items'][0].get('pos',{})
    print(v['type'],'|',v['description'][:95],'|',[i['description'][:55] for i in v['items']],'@%.2f,%.2f'%(p.get('x',0)-X0,p.get('y',0)-Y0))
print('unconnected:',[( [i['description'][:60] for i in u['items']], ['%.2f,%.2f'%(i['pos']['x']-X0,i['pos']['y']-Y0) for i in u['items']]) for u in d['unconnected_items']])
pc=collections.Counter(v['type'] for v in d['schematic_parity']); print('parity',pc)
for v in d['schematic_parity']:
    if v['type']!='footprint_symbol_field_mismatch': print('  ',v['type'],v['description'][:100],[i['description'][:40] for i in v['items']])
