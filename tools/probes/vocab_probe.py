import sys, unicodedata as u
sys.stdout.reconfigure(encoding="utf-8")
v=[l.rstrip("\n") for l in open(sys.argv[1],encoding="utf-8")]
print("size",len(v),"idx0=",repr(v[0]))
single=[t for t in v if len(t)==1]; multi=[t for t in v if len(t)>1]
print("single-char",len(single),"multi-char",len(multi),"examples multi:",multi[:12])
import string
print("ascii lower present:",all(c in v for c in string.ascii_lowercase),"upper:",sum(c in v for c in string.ascii_uppercase),"/26 digits:",sum(c in v for c in string.digits))
ipa="ɔæŋʃʈɖɟʰɡ̯ɪəʊɛ"
print("IPA present:",{c:(c in v) for c in ipa})
beng=[t for t in single if 0x0980<=ord(t)<=0x09FF]
print("Bengali chars in vocab:",len(beng))
scripts={}
for t in single:
    try: n=u.name(t).split()[0]
    except: n="?"
    scripts[n]=scripts.get(n,0)+1
print(sorted(scripts.items(),key=lambda x:-x[1])[:15])
