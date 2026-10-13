"""Build the public audio-sample page (illustration only, not an evaluation; D-068).

Selection rules are fixed in code and stated on the page; no clip is chosen by how it sounds:
  * random set: test_seen sentences with 3-7 s of speech, ordered by sha256(utt_id + "samples-v1");
    SLR37 takes the first 4 with distinct speakers, Rasa the first 4.
  * letter-prior set: SLR37 test_seen sentences containing the letter U+099A (ca), same ordering, first 3.
  * controls: the first SLR37 random sentence, LAT-P with pretrained / fresh / scrambled rows.
  * stress set: our own stress sentences (runs/samples_v1, tools/samples_synth.py), all models.
Every synthetic clip shows the Whisper-BengaliAI transcript and its CER, whatever it is.

By default every clip is written to samples/audio/ as an MP3 named by its content hash, and the page fetches a clip
only when it is played, through one shared audio element; keep the folder next to the page. --single-file embeds
all audio in one inert JSON block instead (one file to send, slower to open), decoded when a clip is first played.
    python tools/build_samples_page.py [--single-file]   # -> samples/bangla_tts_samples.html (+ samples/audio/)
"""

from __future__ import annotations

import argparse
import base64
import csv
import difflib
import hashlib
import html
import json
import sys
import tempfile
from pathlib import Path

import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from c4_build_listening import mp3_b64  # noqa: E402

OUT = ROOT / "samples/bangla_tts_samples.html"
AUDIO = OUT.parent / "audio"
ASR_TAG = "tugstugi_bengaliai-asr_whisper-medium"
SYSTEMS = [  # (key, label, description)
    ("BN-G-matched", "Bengali script", "canonical Bengali characters, fresh embedding rows"),
    ("BN-G-iv-vm-asp", "Restructured Bengali", "vowel forms merged, aspirates split, fresh rows"),
    ("LAT-G-det", "ITRANS", "Latin transliteration, pretrained rows"),
    ("LAT-G-asp", "Latin relabel", "1:1 Latin relabel of the restructured script, pretrained rows"),
    ("LAT-P", "Phonemic Latin", "lexicon phonemes in ASCII, pretrained rows"),
]
RUNS = {
    "slr37": {"BN-G-matched": "pilot_v2", "BN-G-iv-vm-asp": "pilot_v4", "LAT-G-det": "pilot_v1_1",
              "LAT-G-asp": "pilot_v5", "LAT-P": "pilot_v1_1", "LAT-P-reinit": "pilot_v2", "LAT-P-rand": "pilot_v2"},
    "rasa": {"BN-G-matched": "pilot_c1a", "BN-G-iv-vm-asp": "pilot_c1a", "LAT-G-det": "pilot_c1b",
             "LAT-G-asp": "pilot_c1b", "LAT-P": "pilot_c1a"},
}
DATA = {"slr37": ("data/derived/slr37_bn_bd/manifest.tsv", "data/derived/audio24k_v1/index.tsv",
                  "data/derived/splits/v1/test_seen.tsv"),
        "rasa": ("data/derived/rasa_bn/manifest.tsv", "data/derived/audio24k_rasa_v1/index.tsv",
                 "data/derived/splits/rasa_v1/test_seen.tsv")}
PUNCT = "।॥,.?!;:\"'‘’“”()[]-–—…"


def tsv(p: Path) -> list[dict]:
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


class Clips:
    """Encodes each clip once. Returns the attribute that locates it on the page and its duration in seconds:
    data-src="audio/<hash>.mp3" by default, data-clip="<id>" (an entry of the embedded JSON) with embed=True."""

    def __init__(self, tmp: Path, embed: bool):
        self.tmp, self.embed, self.data, self.n = tmp, embed, {}, 0

    def add(self, wav: Path) -> tuple[str, float]:
        x, sr = sf.read(wav, dtype="float32")
        x = x if x.ndim == 1 else x.mean(axis=1)
        b64 = mp3_b64(x, sr, self.tmp)
        self.n += 1
        if self.embed:
            cid = f"c{len(self.data)}"
            self.data[cid] = b64
            return f'data-clip="{cid}"', len(x) / sr
        mp3 = base64.b64decode(b64)
        name = hashlib.sha256(mp3).hexdigest()[:16] + ".mp3"
        (AUDIO / name).write_bytes(mp3)
        return f'data-src="audio/{name}"', len(x) / sr


def run_dir(corpus: str, arm: str) -> Path:
    return ROOT / "runs" / RUNS[corpus][arm] / f"{arm}__train_1h__s666/eval/u3000/test_seen"


def asr_rows(d: Path) -> dict[str, dict]:
    return {r["utt_id"]: r for r in tsv(d / f"asr_{ASR_TAG}.tsv")}


def pick(corpus: str) -> tuple[list[str], list[str], dict, dict]:
    man, idx, split = (ROOT / p for p in DATA[corpus])
    text = {r["utt_id"]: r["text"] for r in tsv(man)}
    audio = {r["utt_id"]: r for r in tsv(idx)}
    ids = [r["utt_id"] for r in tsv(split)]
    ok = sorted((u for u in ids if 3.0 <= float(audio[u]["duration_s"]) <= 7.0),
                key=lambda u: hashlib.sha256((u + "samples-v1").encode()).hexdigest())
    rand, spk = [], set()
    for u in ok:
        s = u.split("_")[1]
        if corpus == "rasa" or s not in spk:
            rand.append(u)
            spk.add(s)
        if len(rand) == 4:
            break
    ca = [u for u in ok if "চ" in text[u] and u not in rand][:3] if corpus == "slr37" else []
    return rand, ca, text, audio


def marked(ref: str, hyp: str) -> str:
    """Hypothesis with words that differ from the reference highlighted (word level, punctuation ignored)."""
    r, h = ref.split(), hyp.split()
    key = [w.strip(PUNCT) for w in r], [w.strip(PUNCT) for w in h]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, *key, autojunk=False).get_opcodes():
        if op == "equal":
            out += [html.escape(w) for w in h[j1:j2]]
            continue
        out += [f"<mark>{html.escape(w)}</mark>" for w in h[j1:j2]]
        if i2 - i1 > j2 - j1:
            miss = html.escape(" ".join(r[i1:i2]))
            out.append(f'<span class="miss" title="missing: {miss}" aria-label="missing: {miss}">‸</span>')
    return " ".join(out)


def cer_badge(cer: float) -> str:
    cls = "ok" if cer < 10 else "mid" if cer < 30 else "bad"
    return f'<span class="cer {cls}"><b>{cer:.0f}%</b><i style="--w:{min(cer, 100):.0f}%"></i></span>'


def player(clip: tuple[str, float], label: str) -> str:
    attr, dur = clip
    return (f'<div class="player"><button class="play" type="button" {attr} aria-pressed="false" '
            f'aria-label="Play {html.escape(label)}"></button><span class="bar" aria-hidden="true"><i></i></span>'
            f'<span class="dur">{dur:.1f} s</span></div>')


def row(label: str, desc: str, clip: tuple[str, float], ref: str, hyp: str | None, cer: float | None) -> str:
    if hyp is None:
        h, c, cls = '<td class="hyp ref-note">reference recording</td>', '<td class="num"></td>', ' class="nat"'
    else:
        h, c, cls = f'<td class="hyp" lang="bn">{marked(ref, hyp)}</td>', f'<td class="num">{cer_badge(cer)}</td>', ""
    return (f'<tr{cls}><th scope="row"><span class="sys">{html.escape(label)}</span>'
            f'<span class="desc">{html.escape(desc)}</span></th><td class="pl">{player(clip, label)}</td>{h}{c}</tr>')


def card(meta: str, ref: str, rows: list[str]) -> str:
    return (f'<article class="card"><header><p class="meta">{meta}</p><button class="all" type="button" '
            f'aria-pressed="false">Play all</button></header><p class="bn" lang="bn">{html.escape(ref)}</p>'
            '<div class="scroll"><table><thead><tr><th>System</th><th>Listen</th><th>ASR transcript (Whisper)</th>'
            f'<th class="num">CER</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></article>')


def sentence_card(clips: Clips, corpus: str, u: str, text: dict, audio: dict, arms: list[tuple[str, str, str]],
                  extra: list[tuple[str, str, Path]] = ()) -> str:
    """extra: (label, description, eval dir holding <utt>.wav and the ASR file), appended after the arms."""
    ref = text[u]
    rows = [row("Natural recording", "real speaker", clips.add(ROOT / audio[u]["path"]), ref, None, None)]
    for label, desc, d in [*((l, ds, run_dir(corpus, k)) for k, l, ds in arms), *extra]:
        a = asr_rows(d)[u]
        rows.append(row(label, desc, clips.add(d / f"{u}.wav"), ref, a["hyp"], 100 * float(a["cer"])))
    return card(f"{html.escape(corpus.upper())} · {html.escape(u)}", ref, rows)


def section(sid: str, title: str, lede: str, cards: list[str]) -> str:
    return f'<section id="{sid}"><h2>{title}</h2><p class="lede">{lede}</p>{"".join(cards)}</section>'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--single-file", action="store_true", help="embed all audio in the page (no audio/ folder)")
    embed = ap.parse_args().single_file
    num = json.loads((ROOT / "paper/numbers.json").read_text(encoding="utf-8"))
    parts = []
    AUDIO.mkdir(parents=True, exist_ok=True)
    for old in AUDIO.glob("*.mp3"):  # only files this script wrote; rebuilt below
        old.unlink()
    with tempfile.TemporaryDirectory() as td:
        clips = Clips(Path(td), embed)
        r37, ca37, t37, a37 = pick("slr37")
        rrs, _, trs, ars = pick("rasa")
        parts.append(section(
            "random", "Random test sentences",
            "Held-out sentences chosen by a fixed hash rule before listening. Same text, same voice prompt and same "
            "duration for every system; only the text representation differs.",
            [sentence_card(clips, "slr37", u, t37, a37, SYSTEMS) for u in r37]
            + [sentence_card(clips, "rasa", u, trs, ars, SYSTEMS) for u in rrs]))
        x1 = ROOT / "runs/pilot_x1/LAT-P__train_full__s666/eval/u15000/test_seen"
        latin = [s for s in SYSTEMS if s[0] in ("LAT-G-det", "LAT-P")]
        long_row = ("Phonemic Latin, 15k updates", "same input, 5× longer training on 1.6 h", x1)
        parts.append(section(
            "letters", "Sentences containing চ",
            "The phonemic Latin input writes চ as <code>c</code>, which an English-trained model tends to read as /k/ "
            "early in training; ITRANS writes <code>ch</code>. Sentences chosen by the rule “contains চ”, in the same "
            "hash order.",
            [sentence_card(clips, "slr37", u, t37, a37, latin, [long_row] if (x1 / f"{u}.wav").exists() else [])
             for u in ca37]))
        ctrl = [("LAT-P", "Pretrained rows", "phonemic Latin on pretrained Latin rows"),
                ("LAT-P-reinit", "Fresh rows", "same text, rows re-initialized"),
                ("LAT-P-rand", "Scrambled letters", "same rows, letters assigned to the wrong sounds")]
        parts.append(section(
            "controls", "Controls: what the pretrained letters contribute",
            "Identical phoneme text in three conditions. The scrambled version uses the same pretrained rows with a "
            "fixed random letter-to-sound mapping.",
            [sentence_card(clips, "slr37", r37[0], t37, a37, ctrl)]))
        meta_p = ROOT / "runs/samples_v1/meta.json"
        if meta_p.exists():
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            labels = {k: (l, d) for k, l, d in SYSTEMS}
            labels |= {"LAT-P-reinit": ("Phonemic Latin, fresh rows", "control"),
                       "LAT-P-rand": ("Scrambled letters", "control")}
            cards = []
            for i, s in enumerate(meta["sentences"]):
                for corpus in ("slr37", "rasa"):
                    rows = []
                    for mid, m in meta["models"].items():
                        if m["corpus"] != corpus:
                            continue
                        e = m["items"][i]
                        arm = mid.split("_", 1)[1]
                        lab, desc = labels.get(arm.replace("_15k", ""), (arm, ""))
                        if arm.endswith("_15k"):
                            lab, desc = lab + ", 15k updates", "5× longer training"
                        if e["g2p_words"]:
                            desc += " · G2P: " + ", ".join(e["g2p_words"]) + " †"
                        rows.append(row(lab, desc, clips.add(ROOT / "runs/samples_v1" / mid / f"s{i}.wav"), s,
                                        e["asr"], e["cer"]))
                    cards.append(card(f"{corpus.upper()} voice · hard sentence {i + 1}", s, rows))
            parts.append(section(
                "stress", "Hard sentences outside the training text",
                "Sentences written to stress rare letters (ঐ ঋ ঈ ৎ ঢ়), conjuncts and nasalization; there is no "
                "natural recording. Target duration is set from the speaker's average speaking rate, identical for "
                "every system. Words marked † are missing from the pronunciation lexicon and were filled by the G2P "
                "model for the phonemic inputs.", cards))
        audio_json = json.dumps(clips.data, separators=(",", ":")) if embed else "{}"
        n = clips.n
    if embed:
        AUDIO.rmdir()
    note = ("embedded in this file; audio is decoded only when played" if embed else
            "loaded from the audio folder next to this page only when played")
    cer = "".join(
        f"<tr><th scope='row'><span class='sys'>{html.escape(l)}</span><span class='desc'>{html.escape(d)}</span></th>"
        f"<td class='num'>{cer_badge(num[f'c3arm.{k}']['test_seen.W']['mean'])}</td>"
        f"<td class='num'>{cer_badge(num[f'c1arm.{k}']['test_seen.W.all']['mean'])}</td></tr>" for k, l, d in SYSTEMS)
    floors = f"{num['floor']['slr37.W.test_seen']:.1f}% (SLR37) and {num['floor']['rasa.W.test_seen']:.1f}% (Rasa)"
    page = (TEMPLATE.replace("{{CER_ROWS}}", cer).replace("{{FLOORS}}", floors).replace("{{N}}", str(n))
            .replace("{{NOTE}}", note).replace("{{BODY}}", "\n".join(parts)).replace("{{AUDIO}}", audio_json))
    OUT.write_text(page, encoding="utf-8", newline="\n")
    size = OUT.stat().st_size / 1e6
    extra = "" if embed else f" + {sum(p.stat().st_size for p in AUDIO.glob('*.mp3')) / 1e6:.1f} MB in {AUDIO.name}/"
    print(f"{n} clips, page {size:.2f} MB{extra} -> {OUT.relative_to(ROOT)}")
    return 0


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bangla Script TTS Samples</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Noto+Serif+Bengali:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* One reading column of sentence cards; each card compares the systems on one sentence. */
:root{--bg:#f6f7f5;--card:#fff;--ink:#1a1f1c;--ink2:#56605a;--rule:#dfe4e0;--accent:#1c5cab;--accent-bg:#e8f0fa;
--ok:#1f7a4d;--ok-bg:#e3f3ea;--mid:#9a6200;--mid-bg:#fbf0dc;--bad:#b3261e;--bad-bg:#fbe5e3;--mark:#fde68a;--mark-ink:#1a1f1c;
--top:rgba(246,247,245,.9);
--f-head:"Source Serif 4",Georgia,serif;--f-text:"IBM Plex Sans",system-ui,sans-serif;
--f-bn:"Noto Serif Bengali","Nirmala UI","Vrinda",serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#111413;--card:#1a1f1d;--ink:#e7ece9;--ink2:#a5afaa;
--rule:#2c3431;--accent:#79b0f0;--accent-bg:#1b2a3c;--ok:#6fd3a0;--ok-bg:#16301f;--mid:#f0c060;--mid-bg:#33290f;--bad:#f2948c;
--bad-bg:#3a1a18;--mark:#6b5410;--mark-ink:#fff6d6;--top:rgba(17,20,19,.9);color-scheme:dark}}
:root[data-theme="dark"]{--bg:#111413;--card:#1a1f1d;--ink:#e7ece9;--ink2:#a5afaa;--rule:#2c3431;--accent:#79b0f0;
--accent-bg:#1b2a3c;--ok:#6fd3a0;--ok-bg:#16301f;--mid:#f0c060;--mid-bg:#33290f;--bad:#f2948c;--bad-bg:#3a1a18;--mark:#6b5410;
--mark-ink:#fff6d6;--top:rgba(17,20,19,.9);color-scheme:dark}
*{box-sizing:border-box}html{scroll-padding-top:4rem}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-text);line-height:1.55;-webkit-text-size-adjust:100%}
.wrap{max-width:64rem;margin:0 auto;padding-inline:16px;padding-block:1.5rem 4rem}
h1,h2{font-family:var(--f-head);font-weight:600;text-wrap:balance;line-height:1.2}
h1{font-size:clamp(1.6rem,4vw,2.1rem);margin:.5rem 0 .6rem}h2{font-size:1.35rem;margin:2.75rem 0 .4rem}
p{max-width:70ch;margin:0 0 .75rem}.lede{color:var(--ink2)}code,kbd{font-size:.9em}
.note{border-left:3px solid var(--accent);padding:.6rem .9rem;background:var(--card);border-radius:0 6px 6px 0;max-width:none}
/* top bar */
.top{position:sticky;top:0;z-index:5;background:var(--top);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule)}
.top .in{max-width:64rem;margin:0 auto;padding:.5rem 16px;display:flex;gap:.75rem;align-items:center}
.top nav{display:flex;gap:.25rem;overflow-x:auto;scrollbar-width:none;flex:1}.top nav::-webkit-scrollbar{display:none}
.top a{color:var(--ink2);text-decoration:none;font-size:.85rem;padding:.3rem .6rem;border-radius:99px;white-space:nowrap}
.top a:hover,.top a.cur{color:var(--accent);background:var(--accent-bg)}
.theme{border:1px solid var(--rule);background:var(--card);color:var(--ink);border-radius:99px;font:inherit;font-size:.8rem;
padding:.3rem .7rem;cursor:pointer;white-space:nowrap}.theme:hover{border-color:var(--accent);color:var(--accent)}
/* cards */
.card{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:1rem 1rem .5rem;margin:1rem 0}
.card>header{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:.25rem}
.meta{font-size:.75rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ink2);margin:0;overflow-wrap:anywhere}
.all{border:1px solid var(--accent);background:transparent;color:var(--accent);border-radius:99px;font:inherit;
font-size:.8rem;font-weight:500;padding:.25rem .8rem;cursor:pointer;white-space:nowrap}
.all:hover,.all[aria-pressed="true"]{background:var(--accent);color:var(--card)}
.bn{font-family:var(--f-bn);font-size:1.3rem;line-height:1.7;margin:0 0 .5rem}.scroll{overflow-x:auto}
.card table{table-layout:fixed;min-width:44rem}.card thead th:nth-child(1){width:26%}
.card thead th:nth-child(2){width:15rem}.card thead th:nth-child(4){width:5rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;vertical-align:middle;padding:.5rem;border-top:1px solid var(--rule)}
thead th{border-top:0;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);font-weight:500;padding-block:.3rem}
tbody tr{transition:background .15s}tbody tr.playing{background:var(--accent-bg)}
tr.nat .sys::after{content:"reference";margin-left:.4rem;font-size:.65rem;font-weight:500;letter-spacing:.05em;
text-transform:uppercase;color:var(--ink2);border:1px solid var(--rule);border-radius:99px;padding:0 .4rem;vertical-align:.1em}
.sys{display:block;font-weight:600}.desc{display:block;font-size:.76rem;color:var(--ink2);font-weight:400;max-width:20rem}
.hyp{font-family:var(--f-bn);font-size:1rem;min-width:14rem;line-height:1.7}
.ref-note{font-family:var(--f-text);font-size:.8rem;color:var(--ink2)}
mark{background:var(--mark);color:var(--mark-ink);border-radius:3px;padding:0 .15em}
.miss{color:var(--bad);font-weight:600;cursor:help}
.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.cer{display:inline-flex;flex-direction:column;align-items:flex-end;gap:3px;min-width:3.2rem;vertical-align:middle}
.cer b{font-weight:600;font-size:.85rem;padding:.05rem .45rem;border-radius:99px}
.cer i{display:block;height:3px;width:3rem;border-radius:2px;background:var(--rule);position:relative;overflow:hidden}
.cer i::after{content:"";position:absolute;inset:0 auto 0 0;width:var(--w)}
.cer.ok b{color:var(--ok);background:var(--ok-bg)}.cer.ok i::after{background:var(--ok)}
.cer.mid b{color:var(--mid);background:var(--mid-bg)}.cer.mid i::after{background:var(--mid)}
.cer.bad b{color:var(--bad);background:var(--bad-bg)}.cer.bad i::after{background:var(--bad)}
.legend .cer{min-width:0}.legend .cer i{display:none}
/* player */
.player{display:flex;align-items:center;gap:.5rem;min-width:11rem}
.play{flex:none;width:2.2rem;height:2.2rem;border-radius:50%;border:1px solid var(--accent);background:var(--card);
color:var(--accent);cursor:pointer;display:grid;place-items:center;padding:0}
.play::before{content:"";width:.7rem;height:.8rem;margin-left:.15rem;background:currentColor;clip-path:polygon(0 0,100% 50%,0 100%)}
.play:hover,.play.on{background:var(--accent);color:var(--card)}
.play.on::before{margin-left:0;width:.65rem;clip-path:none;
background:linear-gradient(90deg,currentColor 0 35%,transparent 35% 65%,currentColor 65%)}
.play.busy::before{animation:pulse .8s infinite alternate}@keyframes pulse{to{opacity:.3}}
.bar{flex:1;height:6px;border-radius:3px;background:var(--rule);cursor:pointer;position:relative;min-width:4rem}
.bar i{position:absolute;inset:0 auto 0 0;width:0;border-radius:3px;background:var(--accent)}
.dur{font-size:.75rem;color:var(--ink2);font-variant-numeric:tabular-nums;white-space:nowrap}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.summary{max-width:40rem}
details{margin:.5rem 0 1rem}summary{cursor:pointer;color:var(--accent);font-size:.9rem}
details li{font-size:.9rem;color:var(--ink2);margin:.2rem 0}details ul{padding-left:1.2rem;margin:.4rem 0}
footer{margin-top:3rem;font-size:.8rem;color:var(--ink2);border-top:1px solid var(--rule);padding-top:1rem}
/* narrow screens: each row becomes a small block */
@media (max-width:42rem){
 .card{padding:.8rem .8rem .3rem}.card thead{display:none}.card table{table-layout:auto;min-width:0}
 .card tbody tr{display:grid;grid-template-columns:1fr auto;grid-template-areas:"sys cer" "pl pl" "hyp hyp";
  border-top:1px solid var(--rule);padding:.5rem 0}
 .card th,.card td{border:0;padding:.15rem .25rem}.card tbody th{grid-area:sys}.card td.pl{grid-area:pl}
 .card td.hyp{grid-area:hyp;min-width:0}.card td.num{grid-area:cer}.desc{max-width:none}.card td.ref-note{display:none}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>
</head>
<body>
<div class="top"><div class="in"><nav aria-label="Sections">
<a href="#systems">Systems</a><a href="#random">Random sentences</a><a href="#letters">চ sentences</a>
<a href="#controls">Controls</a><a href="#stress">Hard sentences</a></nav>
<button class="theme" id="theme" type="button">Theme: auto</button></div></div>
<main class="wrap">
<h1>Bangla Script TTS Samples</h1>
<p class="lede">Audio companion to the preprint <em>Character Embedding Priors and Script Structure in Low-Resource Bangla
Text-to-Speech Adaptation</em>. F5-TTS v1 Base fine-tuned on about one hour of Bangla speech for 3,000 updates, with the
same recipe for every system; only the text representation differs.</p>
<p class="note">These samples illustrate the measured results; they are not a listening test and support no claims of
their own. Sentences are chosen by fixed rules stated in each section, not by how they sound, and every clip shows the
ASR transcript and character error rate (CER), including failures. Seed 666 models.</p>
<details class="legend"><summary>How to read this page</summary><ul>
<li><b>Play</b> starts a clip; only one clip plays at a time. Click the bar to jump within a clip. <b>Play all</b> plays a
card from top to bottom. <kbd>Esc</kbd> stops.</li>
<li>In each transcript, <mark>highlighted</mark> words differ from the reference sentence and <span class="miss">‸</span>
marks missing words (word level, punctuation ignored; hover for the missing text). CER itself is computed on characters.</li>
<li>CER colors: <span class="cer ok"><b>below 10%</b></span> <span class="cer mid"><b>10–30%</b></span>
<span class="cer bad"><b>30% and above</b></span>.</li></ul></details>
<section id="systems"><h2>Systems</h2>
<div class="scroll summary"><table><thead><tr><th>System</th><th class="num">CER, SLR37</th><th class="num">CER, Rasa</th>
</tr></thead><tbody>{{CER_ROWS}}</tbody></table></div>
<p class="lede">Whisper-BengaliAI CER on held-out sentences of the training speakers, mean of three seeds. Real recordings
score {{FLOORS}}.</p></section>
{{BODY}}
<footer>{{N}} clips, MP3 64 kb/s mono, {{NOTE}}.</footer>
</main>
<script type="application/json" id="clips">{{AUDIO}}</script>
<script>
(() => {
  // A clip is fetched (data-src) or decoded from the embedded JSON block (data-clip) only when it is first played.
  // One shared audio element plays everything.
  const store = document.getElementById("clips"), urls = new Map(), audio = new Audio();
  audio.preload = "auto";
  let data = null, btn = null, queue = [], queueBtn = null, raf = 0;
  const src = b => {
    if (b.dataset.src) return b.dataset.src;
    const id = b.dataset.clip;
    if (!urls.has(id)) {
      data ??= JSON.parse(store.textContent);
      const b = atob(data[id]), u = new Uint8Array(b.length);
      for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
      urls.set(id, URL.createObjectURL(new Blob([u], {type: "audio/mpeg"})));
    }
    return urls.get(id);
  };
  const fill = b => b.parentElement.querySelector(".bar i");
  const show = (b, on) => { b.classList.toggle("on", on); b.setAttribute("aria-pressed", String(on)); };
  const tick = () => {
    if (btn && audio.duration) fill(btn).style.width = (100 * audio.currentTime / audio.duration) + "%";
    raf = audio.paused ? 0 : requestAnimationFrame(tick);
  };
  const endQueue = () => {
    queue = [];
    if (queueBtn) { queueBtn.setAttribute("aria-pressed", "false"); queueBtn.textContent = "Play all"; queueBtn = null; }
  };
  const reset = () => {
    if (!btn) return;
    const b = btn;
    btn = null; audio.pause(); show(b, false); fill(b).style.width = "0";
    b.closest("tr")?.classList.remove("playing");
  };
  const start = (b, at = 0) => {
    reset(); btn = b; b.classList.add("busy"); b.closest("tr")?.classList.add("playing");
    audio.src = src(b);
    if (at) audio.addEventListener("loadedmetadata", () => { audio.currentTime = at * audio.duration; }, {once: true});
    audio.play().catch(() => {}).finally(() => b.classList.remove("busy"));
  };
  audio.addEventListener("play", () => { if (btn) show(btn, true); if (!raf) raf = requestAnimationFrame(tick); });
  audio.addEventListener("pause", () => { if (btn) show(btn, false); });
  audio.addEventListener("ended", () => { reset(); if (queue.length) start(queue.shift()); else endQueue(); });
  document.addEventListener("click", e => {
    const p = e.target.closest(".play");
    if (p) {
      endQueue();
      if (p !== btn) start(p); else if (audio.paused) audio.play(); else audio.pause();
      return;
    }
    const s = e.target.closest(".bar");
    if (s) {
      const b = s.parentElement.querySelector(".play"), r = s.getBoundingClientRect();
      const at = Math.min(Math.max((e.clientX - r.left) / r.width, 0), 0.999);
      endQueue();
      if (b === btn && audio.duration) { audio.currentTime = at * audio.duration; if (audio.paused) audio.play(); }
      else start(b, at);
      return;
    }
    const all = e.target.closest(".all");
    if (all) {
      const mine = all === queueBtn;
      endQueue(); reset();
      if (mine) return;
      queue = [...all.closest(".card").querySelectorAll(".play")];
      queueBtn = all; all.setAttribute("aria-pressed", "true"); all.textContent = "Stop";
      start(queue.shift());
    }
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape") { endQueue(); reset(); } });

  // Theme: auto, light, dark; remembered in this browser when storage is available.
  const root = document.documentElement, tb = document.getElementById("theme"), modes = ["auto", "light", "dark"];
  let mode = "auto";
  try { mode = localStorage.getItem("theme") || "auto"; } catch (e) {}
  if (!modes.includes(mode)) mode = "auto";
  const apply = () => {
    if (mode === "auto") root.removeAttribute("data-theme"); else root.dataset.theme = mode;
    tb.textContent = "Theme: " + mode;
  };
  apply();
  tb.addEventListener("click", () => {
    mode = modes[(modes.indexOf(mode) + 1) % 3]; apply();
    try { localStorage.setItem("theme", mode); } catch (e) {}
  });

  // Mark the section in view in the top bar.
  const links = new Map([...document.querySelectorAll(".top a")].map(a => [a.hash.slice(1), a]));
  const io = new IntersectionObserver(es => es.forEach(x => {
    if (!x.isIntersecting) return;
    links.forEach(a => a.classList.remove("cur"));
    links.get(x.target.id)?.classList.add("cur");
  }), {rootMargin: "-45% 0px -50% 0px"});
  links.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    raise SystemExit(main())
