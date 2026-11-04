import json, sys
p = sys.argv[1]
newdir = sys.argv[2]
s = open(p, encoding='utf-8').read()
d = json.loads(s)
changed = 0
for n in d['Nodes']:
    h = n.get('HintPath')
    if h and h != '.' and ('MashProject5_Paylas_V4' in h or 'Paylas' in h):
        tail = n['InputValue'].lstrip('.\\')
        new = newdir.rstrip('\\') + '\\' + tail
        old_esc = json.dumps(h)
        new_esc = json.dumps(new)
        assert s.count(old_esc) == 1, (old_esc, s.count(old_esc))
        s = s.replace(old_esc, new_esc)
        changed += 1
open(p, 'w', encoding='utf-8', newline='').write(s)
d = json.loads(s)
print('changed', changed)
for n in d['Nodes']:
    if 'HintPath' in n:
        print(n['HintPath'], '|', n['InputValue'])
