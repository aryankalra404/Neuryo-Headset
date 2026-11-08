"""Convert a KiCad 5 .kicad_mod (module / fp_text / width) to the KiCad 7+ footprint syntax."""
import sys, uuid
sys.path.insert(0, '/home/claude/kw')
from sx import *
src, dst, name, descr_extra = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
m = parse(open(src).read())
U = lambda: ['uuid', str(uuid.uuid4())]
out = ['footprint', name, ['version', Sym('20241229')], ['generator', 'neuryo_convmod'], ['layer', 'F.Cu']]
for x in m[2:]:
    if not isinstance(x, list):
        continue
    k = x[0]
    if k in ('layer', 'tedit'):
        continue
    if k == 'descr':
        out.append(['descr', x[1] + ' ' + descr_extra])
    elif k == 'fp_text':
        kind, txt = x[1], x[2]
        rest = [y for y in x[3:] if isinstance(y, list)]
        if kind in ('reference', 'value'):
            out.append(['property', 'Reference' if kind == 'reference' else 'Value', 'REF**' if kind == 'reference' else name] + rest + [U()])
        else:
            out.append(['fp_text', Sym('user'), txt] + rest + [U()])
    elif k in ('fp_line', 'fp_circle', 'fp_arc', 'fp_poly'):
        w = kid(x, 'width')
        y = [e for e in x if not (isinstance(e, list) and e[0] == 'width')]
        y.insert(len(y) - 1 if False else len(y), ['stroke', ['width', w[1] if w else Sym('0.1')], ['type', Sym('solid')]])
        y.append(U())
        out.append(y)
    elif k == 'pad':
        out.append(list(x) + [U()])
    else:
        out.append(x)
open(dst, 'w').write(dump(numify(out)) + '\n')
