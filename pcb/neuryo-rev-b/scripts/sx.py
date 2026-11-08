"""Minimal S-expression reader/writer for KiCad files, plus connectivity helpers."""
import re

TOK = re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))')


class Sym(str):
    """Unquoted atom."""


def parse(text):
    stack, cur = [], []
    pos, n = 0, len(text)
    while pos < n:
        m = TOK.match(text, pos)
        if not m:
            if text[pos:].strip() == '':
                break
            raise ValueError('bad token at %d' % pos)
        pos = m.end()
        if m.group(1):
            stack.append(cur); cur = []
        elif m.group(2):
            done = cur; cur = stack.pop(); cur.append(done)
        elif m.group(3) is not None:
            cur.append(m.group(3)[1:-1].replace('\\"', '"').replace('\\\\', '\\'))
        else:
            cur.append(Sym(m.group(4)))
    return cur[0]


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def dump(e, ind=0):
    if isinstance(e, list):
        if not e:
            return '()'
        simple = all(not isinstance(x, list) for x in e)
        if simple:
            return '(' + ' '.join(dump(x) for x in e) + ')'
        out = '(' + dump(e[0])
        for x in e[1:]:
            if isinstance(x, list):
                out += '\n' + '\t' * (ind + 1) + dump(x, ind + 1)
            else:
                out += ' ' + dump(x)
        return out + '\n' + '\t' * ind + ')'
    if isinstance(e, Sym):
        return str(e)
    return q(e)


def kids(e, name):
    return [x for x in e if isinstance(x, list) and x and x[0] == name]


def kid(e, name):
    k = kids(e, name)
    return k[0] if k else None


def val(e, name, i=1):
    k = kid(e, name)
    return k[i] if k and len(k) > i else None


def netlist_groups(net_text):
    """KiCad sexpr netlist -> {netname: frozenset('REF.pin')}"""
    t = parse(net_text)
    out = {}
    for n in kids(kid(t, 'nets'), 'net'):
        nm = val(n, 'name')
        pins = frozenset('%s.%s' % (val(p, 'ref'), val(p, 'pin')) for p in kids(n, 'node'))
        out[nm] = pins
    return out


def pcb_groups(pcb):
    """parsed kicad_pcb -> {netname: frozenset('REF.pad')}"""
    out = {}
    for fp in kids(pcb, 'footprint'):
        ref = None
        for p in kids(fp, 'property'):
            if p[1] == 'Reference':
                ref = p[2]
        for pad in kids(fp, 'pad'):
            nn = kid(pad, 'net')
            if nn is None or str(pad[1]) == '':
                continue
            name = nn[2] if len(nn) > 2 else nn[1]
            out.setdefault(name, set()).add('%s.%s' % (ref, pad[1]))
    return {k: frozenset(v) for k, v in out.items()}


def partition(groups):
    """drop single-pin nets; return set of frozensets"""
    return set(g for g in groups.values() if len(g) > 1)


NUMRE = re.compile(r'^-?\d+(\.\d+)?$')
KEEP = {'property': (1, 2), 'pin': (1,), 'number': (1,), 'name': (1,), 'reference': (1,), 'label': (1,), 'lib_id': (1,),
        'uuid': (1,), 'path': (1,), 'project': (1,), 'text': (1,), 'symbol': (1,), 'generator': (1,), 'generator_version': (1,), 'net': (1, 2), 'footprint': (1,),
        'layer': (1,), 'layers': tuple(range(1, 40)), 'descr': (1,), 'tags': (1,), 'model': (1,), 'page': (1,), 'title': (1,), 'rev': (1,)}


def numify(e):
    """turn numeric python strings created by scripts into bare atoms (KiCad wants (at 1 2), not (at "1" "2"))"""
    if not isinstance(e, list):
        return e
    keep = KEEP.get(str(e[0]), ()) if e and isinstance(e[0], str) else ()
    for i, x in enumerate(e):
        if isinstance(x, list):
            numify(x)
        elif type(x) is str and i == 0:
            e[i] = Sym(x)
        elif type(x) is str and i not in keep and i > 0 and NUMRE.match(x):
            e[i] = Sym(x)
    return e
