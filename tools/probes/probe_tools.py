import sys, csv, traceback
sys.stdout.reconfigure(encoding="utf-8")
LEX = sys.argv[1]
words = ["আমি","ভালো","আছি","করা","করুণ","এক","একে","দেখে","সংস্কৃতি","বিদ্যালয়","ক্ষমা","লক্ষ্মী",
         "চাঁদ","কাঁদা","কাদা","পদ্ম","আত্মা","জ্ঞান","ব্যাংক","স্বাগত","দুঃখ","রাষ্ট্র","বাংলাদেশ","ঢাকা","ইংরেজি"]
lex = {}
for line in open(LEX, encoding="utf-8"):
    if line.startswith("#") or not line.strip(): continue
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2: lex.setdefault(p[0], p[1])
tools = {}
def add(name, fn):
    try:
        fn("আমি"); tools[name] = fn
    except Exception as e:
        print(f"[{name}] unavailable: {type(e).__name__}: {e}")
try:
    from indic_transliteration import sanscript
    add("ISO15919", lambda w: sanscript.transliterate(w, sanscript.BENGALI, sanscript.ISO))
    add("ITRANS", lambda w: sanscript.transliterate(w, sanscript.BENGALI, sanscript.ITRANS))
except Exception as e: print("indic_transliteration fail", e)
try:
    from aksharamukha import transliterate as ak
    add("Aksh_RomanColloq", lambda w: ak.process("Bengali", "RomanColloquial", w))
    add("Aksh_IPA", lambda w: ak.process("Bengali", "IPA", w))
except Exception as e: print("aksharamukha fail", e)
try:
    import avro
    add("Avro_reverse", lambda w: avro.reverse(w))
except Exception as e: print("avro fail", e)
try:
    import uroman as ur
    U = ur.Uroman()
    add("uroman", lambda w: U.romanize_string(w))
except Exception as e: print("uroman fail", e)
try:
    import epitran
    E = epitran.Epitran("ben-Beng")
    add("epitran_IPA", lambda w: E.transliterate(w))
except Exception as e: print("epitran fail", e)
try:
    from indic_unified_parser.uparser import wordparse
    add("CLS_unified", lambda w: wordparse(w, 0, 0, 1))
except Exception as e: print("unified parser fail", e)
names = ["Google_lex"] + list(tools)
out = csv.writer(sys.stdout, delimiter="\t")
out.writerow(["word"] + names)
for w in words:
    row = [w, lex.get(w, "—OOV—")]
    for n in tools:
        try: row.append(tools[n](w))
        except Exception as e: row.append(f"ERR:{type(e).__name__}")
    out.writerow(row)
