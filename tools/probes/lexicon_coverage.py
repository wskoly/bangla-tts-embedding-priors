import sys, re, unicodedata as ud, collections
sys.stdout.reconfigure(encoding="utf-8")
lex=set(); 
for l in open(sys.argv[1],encoding="utf-8"):
    if l.startswith("#") or not l.strip(): continue
    lex.add(ud.normalize("NFC",l.split("\t")[0]))
toks=collections.Counter(); n=0
for l in open(sys.argv[2],encoding="utf-8"):
    if l.startswith("#") or not l.strip(): continue
    p=l.rstrip("\n").split("\t"); txt=p[-1]; n+=1
    for w in re.findall(r"[\u0980-\u09FF\u200c\u200d]+", ud.normalize("NFC",txt)):
        toks[w]+=1
types=len(toks); cov_t=sum(1 for w in toks if w in lex); tot=sum(toks.values()); cov_k=sum(c for w,c in toks.items() if w in lex)
print(f"prompts={n} word types={types} tokens={tot}")
print(f"type coverage={cov_t/types:.3%} token coverage={cov_k/tot:.3%}")
print("top OOV:", [w for w,c in toks.most_common() if w not in lex][:25])
