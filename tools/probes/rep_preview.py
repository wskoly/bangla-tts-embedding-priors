import sys, re, unicodedata as ud, statistics as st, collections
sys.stdout.reconfigure(encoding="utf-8")
lex_p, prompts_p, phon_p, vocab_p = sys.argv[1:5]
lex={}
for l in open(lex_p,encoding="utf-8"):
    if l.startswith("#") or not l.strip(): continue
    p=l.rstrip("\n").split("\t"); lex.setdefault(ud.normalize("NFC",p[0]),p[1])
ipa={}
for l in open(phon_p,encoding="utf-8"):
    a,b=l.rstrip("\n").split("\t"); ipa[a]=b
vocab=set(l.rstrip("\n") for l in open(vocab_p,encoding="utf-8"))
sents=[]
for l in open(prompts_p,encoding="utf-8"):
    if l.startswith("#") or not l.strip(): continue
    sents.append(ud.normalize("NFC",l.rstrip("\n").split("\t")[-1]))
from indic_transliteration import sanscript
from aksharamukha import transliterate as ak
import avro, uroman as ur
U=ur.Uroman()
def g_ascii(w, dots=False):
    if w not in lex: return None
    syl=lex[w].split(" . ")
    return (".".join if dots else "".join)("".join(s.split()) for s in syl)
def g_ipa(w):
    if w not in lex: return None
    return "".join(ipa.get(t,t) for t in lex[w].replace(" . "," ").split())
reps={
 "R0_bengali": lambda w:w,
 "ITRANS": lambda w: sanscript.transliterate(w,sanscript.BENGALI,sanscript.ITRANS),
 "ISO15919": lambda w: sanscript.transliterate(w,sanscript.BENGALI,sanscript.ISO),
 "Aksh_colloq": lambda w: ak.process("Bengali","RomanColloquial",w),
 "Avro_rev": lambda w: avro.reverse(w),
 "uroman": lambda w: U.romanize_string(w),
 "G_ascii": lambda w: g_ascii(w),
 "G_ascii_dots": lambda w: g_ascii(w,True),
 "G_ipa": lambda w: g_ipa(w),
}
# restrict to sentences fully covered by lexicon so all reps compare on identical text
WRE=re.compile(r"[\u0980-\u09FF\u200c\u200d]+")
cov=[s for s in sents if all(w in lex for w in WRE.findall(s))]
print(f"sentences total={len(sents)} fully-lexicon-covered={len(cov)}")
print("rep\tchars/word\tchars/utt(mean)\tuniq_syms\tsyms_not_in_F5\t%chars_OOV_F5\tnonASCII%\tleaks(Bengali chars in output)")
for name,f in reps.items():
    cpw=[]; cpu=[]; syms=collections.Counter(); leak=0
    for s in cov:
        ws=WRE.findall(s); outw=[f(w) for w in ws]
        utt=" ".join(outw); cpu.append(len(utt))
        cpw+= [len(o) for o in outw]
        syms.update(utt)
        if name!="R0_bengali": leak+=sum(1 for c in utt if 0x0980<=ord(c)<=0x09FF)
    tot=sum(syms.values()); oov=[c for c in syms if c not in vocab]
    nonascii=sum(v for c,v in syms.items() if ord(c)>127)
    print(f"{name}\t{st.mean(cpw):.2f}\t{st.mean(cpu):.1f}\t{len(syms)}\t{len(oov)}\t{100*sum(syms[c] for c in oov)/tot:.2f}\t{100*nonascii/tot:.1f}\t{leak}")
    if oov and name!="R0_bengali": print("   OOV syms:", "".join(sorted(oov))[:80])
