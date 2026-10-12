"""Build the public audio-sample page (illustration only, not an evaluation; D-068).

Selection rules are fixed in code and stated on the page; no clip is chosen by how it sounds:
  * random set: test_seen sentences with 3-7 s of speech, ordered by sha256(utt_id + "samples-v1");
    SLR37 takes the first 4 with distinct speakers, Rasa the first 4.
  * letter-prior set: SLR37 test_seen sentences containing the letter U+099A (ca), same ordering, first 3.
  * controls: the first SLR37 random sentence, LAT-P with pretrained / fresh / scrambled rows.
  * stress set: our own stress sentences (runs/samples_v1, tools/samples_synth.py), all models.
Every synthetic clip shows the Whisper-BengaliAI transcript and its CER, whatever it is.
    python tools/build_samples_page.py      # -> samples/bangla_tts_samples.html
"""

from __future__ import annotations

import csv
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


def tsv(p: Path) -> list[dict]:
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


class Clips:
    def __init__(self, tmp: Path):
        self.tmp, self.n = tmp, 0

    def src(self, wav: Path) -> str:
        x, sr = sf.read(wav, dtype="float32")
        self.n += 1
        return "data:audio/mpeg;base64," + mp3_b64(x if x.ndim == 1 else x.mean(axis=1), sr, self.tmp)


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


def row(label: str, desc: str, src: str, hyp: str | None, cer: float | None) -> str:
    c = '<td class="num">–</td>' if cer is None else f'<td class="num">{cer:.0f}%</td>'
    h = '<td class="hyp">–</td>' if hyp is None else f'<td class="hyp" lang="bn">{html.escape(hyp)}</td>'
    return (f'<tr><th scope="row"><span class="sys">{html.escape(label)}</span><span class="desc">{html.escape(desc)}</span>'
            f'</th><td><audio controls preload="none" src="{src}"></audio></td>{h}{c}</tr>')


def table(rows: list[str]) -> str:
    return ('<div class="scroll"><table><thead><tr><th>System</th><th>Audio</th><th>ASR transcript (Whisper)</th>'
            f'<th>CER</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def sentence_card(clips: Clips, corpus: str, u: str, text: dict, audio: dict, arms: list[tuple[str, str, str]]) -> str:
    rows = [row("Natural recording", "real speaker, reference", clips.src(ROOT / audio[u]["path"]), None, None)]
    for key, label, desc in arms:
        d = run_dir(corpus, key)
        a = asr_rows(d)[u]
        rows.append(row(label, desc, clips.src(d / f"{u}.wav"), a["hyp"], 100 * float(a["cer"])))
    return (f'<article class="card"><p class="meta">{html.escape(corpus.upper())} · {html.escape(u)}</p>'
            f'<p class="bn" lang="bn">{html.escape(text[u])}</p>{table(rows)}</article>')


def main() -> int:
    num = json.loads((ROOT / "paper/numbers.json").read_text(encoding="utf-8"))
    parts = []
    with tempfile.TemporaryDirectory() as td:
        clips = Clips(Path(td))
        r37, ca37, t37, a37 = pick("slr37")
        rrs, _, trs, ars = pick("rasa")
        parts.append('<section id="random"><h2>1. Random test sentences</h2><p class="lede">Held-out sentences '
                     'chosen by a fixed hash rule before listening. Same text, same voice prompt and same duration '
                     'for every system; only the text representation differs.</p>')
        parts += [sentence_card(clips, "slr37", u, t37, a37, SYSTEMS) for u in r37]
        parts += [sentence_card(clips, "rasa", u, trs, ars, SYSTEMS) for u in rrs]
        parts.append("</section>")
        parts.append('<section id="letters"><h2>2. Sentences containing চ</h2><p class="lede">The phonemic Latin '
                     'input writes চ as <code>c</code>, which an English-trained model tends to read as /k/ early '
                     'in training; ITRANS writes <code>ch</code>. Sentences chosen by the rule "contains চ", in the '
                     'same hash order.</p>')
        x1 = ROOT / "runs/pilot_x1/LAT-P__train_full__s666/eval/u15000/test_seen"
        for u in ca37:
            arms = [s for s in SYSTEMS if s[0] in ("LAT-G-det", "LAT-P")]
            card = sentence_card(clips, "slr37", u, t37, a37, arms)
            if (x1 / f"{u}.wav").exists():
                a = asr_rows(x1)[u]
                extra = row("Phonemic Latin, 15k updates", "same input, 5× longer training on 1.6 h",
                            clips.src(x1 / f"{u}.wav"), a["hyp"], 100 * float(a["cer"]))
                card = card.replace("</tbody>", extra + "</tbody>")
            parts.append(card)
        parts.append("</section>")
        u = r37[0]
        ctrl = [("LAT-P", "Pretrained rows", "phonemic Latin on pretrained Latin rows"),
                ("LAT-P-reinit", "Fresh rows", "same text, rows re-initialized"),
                ("LAT-P-rand", "Scrambled letters", "same rows, letters assigned to the wrong sounds")]
        parts.append('<section id="controls"><h2>3. Controls: what the pretrained letters contribute</h2>'
                     '<p class="lede">Identical phoneme text in three conditions. The scrambled version uses the '
                     'same pretrained rows with a fixed random letter-to-sound mapping.</p>')
        parts.append(sentence_card(clips, "slr37", u, t37, a37, ctrl))
        parts.append("</section>")
        meta_p = ROOT / "runs/samples_v1/meta.json"
        if meta_p.exists():
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            labels = {k: (l, d) for k, l, d in SYSTEMS}
            labels |= {"LAT-P-reinit": ("Phonemic Latin, fresh rows", "control"),
                       "LAT-P-rand": ("Scrambled letters", "control")}
            parts.append('<section id="stress"><h2>4. Hard sentences outside the training text</h2><p class="lede">'
                         'Sentences written to stress rare letters (ঐ ঋ ঈ ৎ ঢ়), conjuncts and nasalization. Target '
                         'duration is set from the speaker\'s average speaking rate, identical for every system. '
                         'Words marked † are missing from the pronunciation lexicon and were filled by the G2P '
                         'model for the phonemic inputs.</p>')
            for i, s in enumerate(meta["sentences"]):
                for corpus in ("slr37", "rasa"):
                    rows = []
                    for mid, m in meta["models"].items():
                        if m["corpus"] != corpus:
                            continue
                        e = m["items"][i]
                        arm = mid.split("_", 1)[1]
                        base = arm.replace("_15k", "")
                        lab, desc = labels.get(base, (base, ""))
                        if arm.endswith("_15k"):
                            lab, desc = lab + ", 15k updates", "5× longer training"
                        if e["g2p_words"]:
                            desc += " · G2P: " + ", ".join(e["g2p_words"]) + " †"
                        rows.append(row(lab, desc, clips.src(ROOT / "runs/samples_v1" / mid / f"s{i}.wav"),
                                        e["asr"], e["cer"]))
                    parts.append(f'<article class="card"><p class="meta">{corpus.upper()} voice · stress sentence '
                                 f'{i + 1}</p><p class="bn" lang="bn">{html.escape(s)}</p>{table(rows)}</article>')
            parts.append("</section>")
        n = clips.n
    cer = "".join(
        f"<tr><th scope='row'>{html.escape(l)}</th><td class='num'>{num[f'c3arm.{k}']['test_seen.W']['mean']:.1f}</td>"
        f"<td class='num'>{num[f'c1arm.{k}']['test_seen.W.all']['mean']:.1f}</td></tr>" for k, l, _ in SYSTEMS)
    floors = f"{num['floor']['slr37.W.test_seen']:.1f} % (SLR37) and {num['floor']['rasa.W.test_seen']:.1f} % (Rasa)"
    page = TEMPLATE.replace("{{CER_ROWS}}", cer).replace("{{FLOORS}}", floors).replace("{{BODY}}", "\n".join(parts))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"{n} clips, {OUT.stat().st_size / 1e6:.1f} MB -> {OUT.relative_to(ROOT)}")
    return 0


TEMPLATE = """<title>Bangla Script TTS Samples</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Noto+Serif+Bengali:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Layout: a single reading column of sentence cards; each card is a compact comparison table. */
:root{--bg:#f7f8f6;--card:#fff;--ink:#1a1f1c;--ink2:#545c57;--rule:#dde2de;--accent:#1c5cab;
--f-head:"Source Serif 4",Georgia,serif;--f-text:"IBM Plex Sans",system-ui,sans-serif;--f-bn:"Noto Serif Bengali","Nirmala UI",serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121514;--card:#1a1f1d;--ink:#e7ece9;--ink2:#a7b1ac;--rule:#2d3532;--accent:#6da7ec;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121514;--card:#1a1f1d;--ink:#e7ece9;--ink2:#a7b1ac;--rule:#2d3532;--accent:#6da7ec;color-scheme:dark}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);font-family:var(--f-text);line-height:1.55}
.wrap{max-width:62rem;margin:0 auto;padding-inline:16px;padding-block:2rem 4rem}
h1,h2{font-family:var(--f-head);font-weight:600;text-wrap:balance;line-height:1.2}h1{font-size:2rem;margin:0 0 .5rem}
h2{font-size:1.35rem;margin:2.5rem 0 .5rem}p{max-width:68ch;margin:0 0 .75rem}.lede{color:var(--ink2)}
.note{border-left:3px solid var(--accent);padding:.5rem .9rem;background:var(--card);max-width:none}
code{font-size:.9em}.card{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:1rem;margin:1rem 0}
.meta{font-size:.78rem;letter-spacing:.04em;text-transform:uppercase;color:var(--ink2);margin:0 0 .3rem}
.bn{font-family:var(--f-bn);font-size:1.25rem;margin:0 0 .75rem}.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{text-align:left;vertical-align:middle;padding:.45rem .5rem;border-top:1px solid var(--rule)}
thead th{border-top:0;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;color:var(--ink2);font-weight:500}
.sys{display:block;font-weight:600}.desc{display:block;font-size:.78rem;color:var(--ink2);font-weight:400;max-width:22rem}
.hyp{font-family:var(--f-bn);min-width:14rem}.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
audio{width:13rem;max-width:100%;height:2.2rem}.summary{max-width:34rem}
@media (max-width:40rem){audio{width:10rem}.hyp{min-width:10rem}}
</style>
<div class="wrap">
<h1>Bangla Script TTS Samples</h1>
<p class="lede">Audio companion to the preprint <em>Character Embedding Priors and Script Structure in Low-Resource Bangla
Text-to-Speech Adaptation</em>. F5-TTS v1 Base fine-tuned on about one hour of Bangla speech for 3,000 updates, with the
same recipe for every system; only the text representation differs.</p>
<p class="note">These samples illustrate the measured results; they are not a listening test and support no claims of
their own. Sentences are chosen by fixed rules stated in each section, not by how they sound, and every clip shows the
ASR transcript and character error rate (CER), including failures. Seed 666 models.</p>
<h2>Systems</h2>
<div class="scroll summary"><table><thead><tr><th>System</th><th>CER %, SLR37</th><th>CER %, Rasa</th></tr></thead>
<tbody>{{CER_ROWS}}</tbody></table></div>
<p class="lede">Whisper-BengaliAI CER on held-out sentences of the training speakers, mean of three seeds. Real recordings
score {{FLOORS}}.</p>
{{BODY}}
</div>
<script>
document.addEventListener("play", e => { for (const a of document.querySelectorAll("audio")) if (a !== e.target) a.pause(); }, true);
</script>
"""

if __name__ == "__main__":
    raise SystemExit(main())
