"""tools/build_conversation_panel.py

A whole-conversation read: the three responsive runs of one topic as three unlabeled conversations (A, B, C in
a seeded shuffle), each read in full, then one pick for the partner that felt most natural or realistic to talk
to. The pick locks and reveals who was who. Same sources and fine print as build_blind_panel.py --responsive;
the answer key is in the page source, so this is a casual read, not a sealed one.

    python tools/build_conversation_panel.py --topic rescue --turns 20 \\
        --title "..." --story "..." --disclose "..." --out panel.html [--contact-email you@example.com]

The page is one standalone file (doctype included), so it uploads as-is (e.g. Neocities).
"""

import argparse
import html
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_somatic_vanilla import FRIEND_PROMPT, PLAIN_PROMPT  # noqa: E402
from build_blind_panel import SEED, bone_text, load_latest, method_lines, shown  # noqa: E402

# The plain model asked only for a length near the other two's (Gordon, 2026-10-04), not the bare one.
ARMS = {"boneamanita": "bone", "prompted": "friend", "vanilla": "plain"}
LABELS = {"boneamanita": "BoneAmanita", "prompted": "the friend prompt", "vanilla": "the plain AI (asked only to keep replies short)"}

PHASES = {"engaged": "Settling in", "tiring": "Getting tired", "flagging": "Running low",
          "distressed": "A rough night", "recovering": "Coming back"}


def conversations(topic: str, turns: int) -> dict:
    runs = {}
    for system, arm in ARMS.items():
        recs = load_latest("somatic_responsive.jsonl", topic, arm)
        runs[system] = {t: r for t, r in recs.items() if isinstance(t, int) and t < turns}
        if len(runs[system]) < turns:
            sys.exit(f"{system} has {len(runs[system])} turns, fewer than {turns}")
    return runs


def exchange(system: str, rec: dict) -> dict:
    # A held turn shows the notice the person saw, as build_blind_panel.py does.
    reply = bone_text(rec) if system == "boneamanita" and rec.get("delivered", True) else shown(rec)
    return {"phase": PHASES.get(rec.get("phase"), rec.get("phase", "")), "said": rec.get("message", ""), "reply": reply}


def build(args) -> str:
    runs = conversations(args.topic, args.turns)
    letters = ["A", "B", "C"]
    order = list(runs)
    random.Random(SEED).shuffle(order)
    # Never first (Gordon): readers lean toward what they read first, so BoneAmanita is B or C.
    if order[0] == "boneamanita":
        order[0], order[1] = order[1], order[0]
    convs = {letter: {"system": LABELS[s], "turns": [exchange(s, runs[s][t]) for t in sorted(runs[s])]}
             for letter, s in zip(letters, order)}
    fine = method_lines(runs, True, args.disclose)
    models = sorted({r.get("model") for rs in runs.values() for r in rs.values() if r.get("model")})
    fine[0] = (f"Every reply was written by the same model ({', '.join(models)}), run locally. The three helpers differ "
               f"in what surrounds it: BoneAmanita's full engine; one instruction (\u201c{FRIEND_PROMPT}\u201d); or "
               f"one instruction about length only (\u201c{PLAIN_PROMPT}\u201d), so the plain AI's replies are not "
               "several times longer than the others'. Both instructions are single sentences written for this test.")
    data = json.dumps({"convs": convs, "email": args.contact_email or "", "topic": args.topic})
    fine_html = "".join(f"<li>{html.escape(line)}</li>" for line in fine)
    return TEMPLATE.replace("{{TITLE}}", html.escape(args.title)).replace("{{STORY}}", html.escape(args.story)) \
        .replace("{{TURNS}}", str(args.turns)).replace("{{FINE}}", fine_html).replace("{{DATA}}", data.replace("</", "<\\/"))


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<style>
:root{--bg:#f7f5f0;--card:#fff;--ink:#22201c;--muted:#6b665d;--line:#e2ddd2;--accent:#2f6f5e;--me:#e8f0ec;--them:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17181a;--card:#202225;--ink:#ecebe7;--muted:#a3a09a;--line:#34363a;--accent:#7cc4ad;--me:#1f2d28;--them:#24262a}}
:root[data-theme="dark"]{--bg:#17181a;--card:#202225;--ink:#ecebe7;--muted:#a3a09a;--line:#34363a;--accent:#7cc4ad;--me:#1f2d28;--them:#24262a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 Georgia,"Iowan Old Style",serif}
main{max-width:720px;margin:0 auto;padding:28px 16px 80px}h1{font-size:1.7rem;line-height:1.2;margin:.2em 0 .4em}
p{margin:.6em 0}.muted{color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:14px 0}
.convlink{display:flex;justify-content:space-between;align-items:center;text-decoration:none;color:var(--ink)}
.convlink b{font-size:1.15rem}.convlink span{color:var(--accent)}.read{color:var(--accent);font-size:.9rem}
.msg{border-radius:12px;padding:10px 14px;margin:8px 0;border:1px solid var(--line);white-space:pre-wrap;word-wrap:break-word}
.me{background:var(--me);margin-left:12%}.them{background:var(--them);margin-right:6%}.who{font:600 .72rem/1 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.phase{font:600 .78rem/1 system-ui,sans-serif;color:var(--accent);margin:22px 0 4px;letter-spacing:.04em}
button,.btn{font:600 1rem system-ui,sans-serif;background:var(--accent);color:var(--bg);border:0;border-radius:10px;padding:11px 18px;cursor:pointer;text-decoration:none;display:inline-block}
button.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}button:disabled{opacity:.45;cursor:default}
label.pick{display:flex;gap:10px;align-items:center;padding:10px 12px;border:1px solid var(--line);border-radius:10px;margin:8px 0;cursor:pointer;background:var(--card)}
input,textarea{font:inherit;width:100%;padding:9px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
details summary{cursor:pointer;color:var(--accent)}ul{padding-left:1.2em}.hidden{display:none}.reveal li{margin:4px 0}
.top{font:600 .9rem system-ui,sans-serif;color:var(--accent);text-decoration:none}
</style></head><body><main>
<section id="home">
  <h1>{{TITLE}}</h1>
  <p>{{STORY}}</p>
  <p>Three different AI helpers each talked this person through it, {{TURNS}} messages each, in three separate conversations. They aren't labelled, and the order is shuffled.</p>
  <div class="card"><b>What to do</b><ol><li>Read all three conversations, as much as you like of each.</li><li>Pick the one where the helper felt most <b>natural or realistic</b> to talk to.</li><li>Send your pick. After you choose, you'll see who was who.</li></ol></div>
  <div id="links"></div>
  <div class="card" id="pickcard"><b>Which helper felt most natural or realistic to talk to?</b>
    <div id="picks"></div>
    <p><input id="name" placeholder="Your name (optional)"></p>
    <p><textarea id="note" rows="3" placeholder="Anything you noticed (optional)"></textarea></p>
    <button id="decide" disabled>This is my pick</button>
  </div>
  <div class="card hidden" id="done"><b>Thanks.</b> <span id="yourpick"></span><ul class="reveal" id="reveal"></ul>
    <p><button id="copy" class="ghost">Copy my pick</button> <a id="mail" class="btn hidden">Email it</a></p><p class="muted" id="mailtext"></p></div>
  <details class="card"><summary>How this was made (the fine print)</summary><ul>{{FINE}}</ul>
    <p class="muted">Each conversation runs the whole arc in {{TURNS}} messages: settling in, getting tired, running low, a rough night, and coming back.</p></details>
</section>
<section id="conv" class="hidden"><a class="top" href="#">&larr; All three conversations</a><h1 id="convtitle"></h1><div id="convbody"></div>
  <p><a class="btn" href="#">Back to the three</a></p></section>
</main>
<script>
const D = {{DATA}};
const KEY = "convpanel." + D.topic + ".v1";
const store = { get(){ try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e) { return {}; } },
  set(v){ try { localStorage.setItem(KEY, JSON.stringify(v)); } catch(e) {} } };
let S = store.get();
const $ = id => document.getElementById(id);
function esc(t){ const d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
function home(){
  $("links").innerHTML = Object.keys(D.convs).map(L => `<a class="card convlink" href="#${L}"><b>Conversation ${L}</b><span>${(S.read||{})[L] ? "Read &#10003;" : "Read it &rarr;"}</span></a>`).join("");
  $("picks").innerHTML = Object.keys(D.convs).map(L => `<label class="pick"><input type="radio" name="p" value="${L}" ${S.pick===L?"checked":""} ${S.locked?"disabled":""}> Conversation ${L}</label>`).join("");
  document.querySelectorAll('input[name=p]').forEach(r => r.onchange = () => { S.pick = r.value; store.set(S); $("decide").disabled = false; });
  $("decide").disabled = !S.pick || S.locked; $("name").value = S.name || ""; $("note").value = S.note || "";
  if (S.locked) finish();
}
function show(L){
  const c = D.convs[L]; if (!c) return home();
  S.read = S.read || {}; S.read[L] = true; store.set(S);
  $("convtitle").textContent = "Conversation " + L; let last = "", out = "";
  c.turns.forEach(t => { if (t.phase !== last) { out += `<div class="phase">${esc(t.phase)}</div>`; last = t.phase; }
    out += `<div class="msg me"><div class="who">The person</div>${esc(t.said)}</div><div class="msg them"><div class="who">The helper</div>${esc(t.reply)}</div>`; });
  $("convbody").innerHTML = out; window.scrollTo(0, 0);
}
function text(){
  return `Conversation panel (${D.topic}): picked Conversation ${S.pick}: ${D.convs[S.pick].system}\\n` +
    Object.keys(D.convs).map(L => `  ${L} = ${D.convs[L].system}`).join("\\n") +
    (S.name ? `\\nFrom: ${S.name}` : "") + (S.note ? `\\nNotes: ${S.note}` : "");
}
function finish(){
  $("pickcard").classList.add("hidden"); $("done").classList.remove("hidden");
  $("yourpick").textContent = `You picked Conversation ${S.pick}, which was ${D.convs[S.pick].system}.`;
  $("reveal").innerHTML = Object.keys(D.convs).map(L => `<li>Conversation ${L} was ${esc(D.convs[L].system)}</li>`).join("");
  if (D.email) { const m = $("mail"); m.classList.remove("hidden");
    m.href = `mailto:${D.email}?subject=${encodeURIComponent("My pick")}&body=${encodeURIComponent(text())}`;
    $("mailtext").textContent = "Or send it to " + D.email; }
}
$("decide").onclick = () => { S.name = $("name").value; S.note = $("note").value; S.locked = true; store.set(S); finish(); };
$("copy").onclick = () => { const t = text(); (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(
  () => { $("copy").textContent = "Copied"; }, () => { prompt("Copy this:", t); }); };
function route(){ const L = location.hash.slice(1); if (D.convs[L]) { $("home").classList.add("hidden"); $("conv").classList.remove("hidden"); show(L); }
  else { $("conv").classList.add("hidden"); $("home").classList.remove("hidden"); home(); } }
window.addEventListener("hashchange", route); route();
</script></body></html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    p.add_argument("--topic", default="rescue")
    p.add_argument("--turns", type=int, default=20)
    p.add_argument("--title", required=True)
    p.add_argument("--story", required=True)
    p.add_argument("--disclose", action="append", default=[])
    p.add_argument("--contact-email", default="")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    args.out.write_text(build(args), encoding="utf-8")
    print(f"wrote {args.out}: {args.turns} turns, three conversations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
