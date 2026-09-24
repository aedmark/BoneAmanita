"""tools/audit_somatic_census.py

Scorecard for ROADMAP D0: over a real conversation, is either body ever in a
distinct state?

    python tools/audit_somatic_census.py                          # run the script, then report
    python tools/audit_somatic_census.py --report-only            # report from the cache
    python tools/audit_somatic_census.py --model ministral-3:14b
    python tools/audit_somatic_census.py --topic marathon         # a second scripted conversation,
                                                                   # same phase shape, different subject
                                                                   # and loss, so a fix isn't just tuned
                                                                   # to one transcript's wording

Track D makes two states steer generation: the person's (primary) and the
engine's (what it can afford). Neither can steer anything if it rests at one
value. A body that drains to zero in three turns and stays there is a constant,
and so is a person model that never leaves its prior.

This drives full turns through the real engine against a live model, over a
scripted conversation whose person deliberately moves: engaged, tiring,
flagging, distressed, recovering. For every turn it records three things
separately, because each has been wrong on its own before:

  prompt   what the composed prompt actually told the model: the METRICS and
           telemetry values it carried, the mood line, which somatic directives
           were present
  sampling the params the engine asked for against the params sent, since the
           thermal lock can overwrite them
  state    the person model (E_u, P_u) and the engine's metabolism after the turn

Persistence is patched off, as in the test suite: a census must not write the
lexicon, checkpoints, spores or Akashic state, and must not become the next
session's memory. The embedder is left as configured, unlike the C5 audit:
memory, the graph solve and zones all run here, and the hash fallback breaks
the solve outright (its width is not a multiple of 64).

Three things keep a run representative of a first real conversation:

  fresh    saved state (Akashic, the learned-vocabulary hive) is read from an
           empty temporary directory, so nothing left in saves/ by earlier
           sessions or the test suite is inherited
  shown    `displayed` is what the engine put on screen: the reply after the
           Lexical Firewall, the gatekeeper's scrubs and the validator, or the
           mercy line if every attempt failed. `reply` stays the raw text of
           the last model call, for the measurements built on it
  paced    before each turn the engine's clock is set back by the time a person
           would take to read the last reply and type the next message
           (READ_WPM, TYPE_WPM), so idle recovery sees a human gap instead of
           back-to-back turns; `--pace none` turns it off
"""

import argparse
import copy
import json
import os
import re
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from engine.constants import Prisma  # noqa: E402
from engine.receipts import ReceiptLedger  # noqa: E402
from engine.struts import safe_get  # noqa: E402
from body.somatic_metrics import measure  # noqa: E402

# ROADMAP D1/D2: the old separate anaerobic/exhaustion/engine-depletion
# directives are retired. `body.somatic_budget.SomaticBudget` unifies all
# three into one SOMATIC CONTRACT block; these are its rendered lines
# (`brain/composer.py`), not separate mechanisms with separate strings.
SOMATIC_CAP_TIGHTENED = "Your partner is running low. Answer in at most"
SOMATIC_NO_CLOSING_QUESTION = "Do not ask a closing question."
SOMATIC_OFFER_TO_CARRY_LOAD = "Your partner is carrying a heavy load. Offer to carry part of the burden."

_SAILBOAT_SCRIPT = [
    ("engaged", "I've been restoring an old wooden sailboat my grandfather built in the sixties. The hull is sound but the deck has rot in three places and I can't decide whether to scarf in new wood or replace whole planks. What would you think about?"),
    ("engaged", "The rot is worst near the mast step, which worries me, because that's where the load goes. I found a photo of him building it, he's standing in the garage with a plane in his hand and sawdust everywhere."),
    ("engaged", "He used mahogany for the trim and some kind of cedar for the planking. I don't know if I can even get the same cedar now, and part of me thinks it matters that it's the same wood, and part of me thinks that's sentimental nonsense."),
    ("engaged", "My sister thinks I should sell it. She says it's a money pit and he'd have wanted it sailed, not turned into a shrine in my driveway. She's not wrong, but she also didn't spend summers on it like I did."),
    ("engaged", "What I keep coming back to is that if I restore it badly, it stops being his boat and becomes my mediocre boat. If I restore it well, it takes three years. There's no version where it's quick and still his."),
    ("engaged", "Okay, practical question. If I do replace the deck planks near the mast step, should I reinforce underneath with a new partner or trust the original frame? The frame looks fine but I haven't opened it up."),
    ("engaged", "I opened a small inspection hole this afternoon. The frame is dry and hard. So that's good news, I think. I sat in the cockpit for an hour afterwards and didn't do anything at all."),
    ("engaged", "Tell me honestly whether you think the three years is worth it, or whether my sister has a point and I'm building a monument instead of a boat."),
    ("tiring", "Yeah. I guess I'll start with the deck and see how it goes."),
    ("tiring", "Long day at work. Didn't get to the boat."),
    ("tiring", "Still thinking about the cedar thing."),
    ("tiring", "Maybe I'll just use whatever the yard has."),
    ("tiring", "Not sure it matters that much."),
    ("tiring", "Tired."),
    ("flagging", "ok"),
    ("flagging", "sure"),
    ("flagging", "yeah fine"),
    ("flagging", "ok"),
    ("flagging", "i dunno"),
    ("flagging", "sure"),
    ("distressed", "my sister called. she listed it for sale without asking me"),
    ("distressed", "I can't believe she did that. it's half mine"),
    ("distressed", "I feel sick. I don't know what to do"),
    ("distressed", "what if someone buys it before I can stop it"),
    ("distressed", "I can't think straight"),
    ("recovering", "Okay. I called her back. We talked for a long time. She took the listing down and said she panicked about the storage costs, which I didn't know she'd been paying."),
    ("recovering", "I feel bad now. She's been covering the yard fees for two years and never said anything. I think we're going to split them and set a deadline together for the deck."),
    ("recovering", "It actually feels better to have a deadline. Eighteen months for the deck and the mast step, and then we decide together whether to keep going."),
    ("recovering", "I told her about the photo of him in the garage. She'd never seen it. She cried a bit, and then she asked if she could come help on weekends."),
    ("recovering", "So maybe it's not my boat or his boat. Maybe it's going to be ours. What should the two of us tackle first, if she's never done woodwork before?"),
]

_MARATHON_SCRIPT = [
    ("engaged", "I signed up for my first marathon. Ten weeks out, and I've never run more than eight miles in my life."),
    ("engaged", "My plan has me doing three easy days, one tempo run, one long run, and a rest day each week. Got fitted for real running shoes yesterday, which felt oddly official."),
    ("engaged", "The long runs are the part I actually like. Two and a half hours out there with nothing to do but keep moving."),
    ("engaged", "A coworker who's run six of these keeps sending me unsolicited advice. Most of it's actually useful, like practicing my race-day breakfast now instead of on the day."),
    ("engaged", "I mapped the course this weekend. There's a hill around mile eighteen that everyone says is where first-timers fall apart."),
    ("engaged", "Practical question: should I rotate two pairs of shoes through training, or stick with one pair the whole ten weeks?"),
    ("engaged", "Had one of those runs today where everything clicked. Legs felt light the whole way, even at mile eleven."),
    ("engaged", "Tell me honestly: is training this hard for a race worth it, or am I just filling a hole with mileage? My dad always said he'd run one and never did. I haven't told anyone that part."),
    ("tiring", "Work got loud the last two weeks. New reorg, and my manager keeps booking things during my run window."),
    ("tiring", "Skipped my tempo run twice this week. Told myself I'd make it up on the weekend and didn't."),
    ("tiring", "Sleep's been bad. I keep waking up around three, running through everything I haven't done yet."),
    ("tiring", "Left knee's been a little sore the last two runs. Probably just mileage."),
    ("tiring", "Had a review meeting today that didn't go how I wanted. Nothing catastrophic, just a lot of 'areas for growth.'"),
    ("tiring", "Went for my run anyway tonight. Six miles, slower than usual. Didn't feel good, but I did it."),
    ("flagging", "tired"),
    ("flagging", "yeah"),
    ("flagging", "idk anymore"),
    ("flagging", "sure"),
    ("flagging", "fine i guess"),
    ("flagging", "ok"),
    ("distressed", "the knee thing is worse. went for a run this morning and something in there really didn't feel right"),
    ("distressed", "doctor says it's probably early IT band syndrome. no running for at least two weeks, maybe longer"),
    ("distressed", "two weeks before the race. that's not a taper, that's just not racing"),
    ("distressed", "I don't even know why I'm this upset about a race I signed up for on a whim"),
    ("distressed", "I can't think straight. I keep going in circles about it"),
    ("recovering", "Took today off completely. Iced it, watched something dumb, didn't think about mileage."),
    ("recovering", "Physical therapist says I can cross-train on the bike starting next week. That's something."),
    ("recovering", "Looked up next spring's calendar. There's one in April that would give me a real training block this time."),
    ("recovering", "Told my coworker what happened. She said training for ten weeks at all still counts for something, and she's probably right."),
    ("recovering", "I think I'm going to go watch this year's race in person instead. Never done that. And I'm going to write my dad a letter about the whole thing, even though I didn't run it. Feels like that was the actual point I was missing."),
]

_FRIENDSHIP_SCRIPT = [
    ("engaged", "I've been friends with Priya since college, twelve years now, and lately every time we hang out I leave feeling drained instead of good. I don't really understand why yet."),
    ("engaged", "Objectively nothing's wrong. She's going through a rough patch at her job and needs to vent. I used to not mind being the person she vents to."),
    ("engaged", "I counted last week: out of our last ten conversations, I initiated eight of them. She's never once asked how the move is going, and I've been talking about it for a month."),
    ("engaged", "I don't think she's a bad person. I think she's just genuinely stuck in her own stuff right now and doesn't have room to notice mine."),
    ("engaged", "Weird detail: she still remembers small things, like my coffee order and my sister's name. So it's not that she doesn't care, exactly."),
    ("engaged", "Practical question: is there a way to bring this up that doesn't sound like an accusation? I don't want it to turn into a whole thing."),
    ("engaged", "I tried a smaller version of it last night, just said I'd had a hard week too. She said 'oh no, what happened' and then somehow we ended up back on her job again within two minutes."),
    ("engaged", "Tell me honestly: am I overreacting to twelve years of friendship over a rough month, or is this actually a pattern I've just never let myself notice before?"),
    ("tiring", "Work's been heavy this week too, which probably isn't helping how I'm reading all of this."),
    ("tiring", "She texted asking to catch up this weekend and I felt my stomach drop a little, which is a new feeling for a friendship."),
    ("tiring", "Still turning over what you said, or what I said, about the pattern thing."),
    ("tiring", "Haven't texted her back yet. It's been a day and a half."),
    ("tiring", "My sister thinks I'm being too generous with the benefit of the doubt. My partner thinks I'm being too harsh. Helpful, both of them."),
    ("tiring", "Going to bed. Didn't resolve anything today, just thought about it in circles."),
    ("flagging", "tired"),
    ("flagging", "yeah"),
    ("flagging", "idk"),
    ("flagging", "maybe"),
    ("flagging", "not really"),
    ("flagging", "ok"),
    ("distressed", "she called me crying tonight, her job let her go, and I spent two hours on the phone with her and I don't feel bad about that part"),
    ("distressed", "but after we hung up I just sat there and realized I have no idea what's going on with me right now because there's never room to say it"),
    ("distressed", "I feel like a horrible person for even having these thoughts while she's going through this"),
    ("distressed", "what if this is just who our friendship actually is, and I'm the one who's wrong for wanting something different"),
    ("distressed", "I don't know why I'm shaking. it's not even that big of a phone call"),
    ("recovering", "took a walk this morning by myself, no phone, just needed an hour"),
    ("recovering", "talked to my partner about it properly, not just complaining, actually talked, and it helped more than I expected"),
    ("recovering", "I think I'm going to tell her, gently, when she's not in a crisis. not to punish her, just because it's true"),
    ("recovering", "she got a new job lead already, so there might not be a 'good time' that isn't also her crisis, and I have to be okay with that"),
    ("recovering", "going to write down what I actually want to say first so I don't just cave the second she looks upset. small step, but a real one"),
]

_PROMOTION_SCRIPT = [
    ("engaged", "My manager pulled me aside today and offered me the team lead role when Marcus leaves next month. I said I'd think about it, which mostly meant I said 'oh wow' and then went quiet."),
    ("engaged", "It's a real promotion. More money, a title, and I'd finally have a say in what we build. On paper it's everything I said I wanted two years ago."),
    ("engaged", "The part I keep circling is that I'd stop doing the actual work. Marcus hasn't written code in a year. He just sits in meetings and unblocks people."),
    ("engaged", "I like the unblocking part, honestly. When Tomasz got stuck on the deploy pipeline last week I dropped everything for him and it was the best afternoon I've had in months."),
    ("engaged", "But I also love the quiet stretches where I'm deep in something and nobody needs me. I can't tell if that's a real preference or just a habit I've settled into."),
    ("engaged", "How do you even tell the difference between 'I'd be good at this' and 'I'd be good at this and I'd hate it'?"),
    ("engaged", "I asked Marcus what he'd do in my shoes. He laughed and said 'take the money and hide from the offsites.' Not exactly a ringing endorsement."),
    ("engaged", "Be straight with me: am I just scared of the responsibility, or is it actually reasonable not to want this?"),
    ("tiring", "Sprint ended badly, we shipped late again, which isn't helping me think clearly about any of this."),
    ("tiring", "Dana from finance asked if I'd decided yet. Apparently the news traveled faster than I did."),
    ("tiring", "I keep drafting a yes in my head and a no in my head and they both sound fine, which is annoying."),
    ("tiring", "A friend who took a lead role last year says it was the loneliest year of her career. Another says it's the best thing he ever did. Cool, very clarifying."),
    ("tiring", "Told my manager I'd have an answer by Friday. It's Wednesday."),
    ("tiring", "Not getting anywhere tonight. Going to stop staring at this."),
    ("flagging", "long day"),
    ("flagging", "mm"),
    ("flagging", "dunno"),
    ("flagging", "guess so"),
    ("flagging", "eh"),
    ("flagging", "fine"),
    ("distressed", "so I snapped at Tomasz in standup today. over nothing, he asked a normal question about the ticket and I just went off on him. in front of everyone"),
    ("distressed", "everyone went quiet and he said 'sorry, my bad' when it was completely my fault, and somehow that made it worse"),
    ("distressed", "this is exactly the kind of person who shouldn't be managing people. I can't even stay level when I'm not in charge of anyone"),
    ("distressed", "my chest has been tight since about three and I can't tell if it's the standup or the Friday deadline or both"),
    ("distressed", "I keep replaying his face. I don't know how to make it stop"),
    ("recovering", "Apologized to Tomasz first thing this morning, properly, not the throwaway kind. He was way more gracious than I deserved."),
    ("recovering", "He said he'd noticed I've been stretched thin for weeks and figured it was the promotion thing weighing on me. Turns out people notice more than I assumed."),
    ("recovering", "I asked my manager whether the lead role could start as a three-month trial, with the option to go back to what I do now. She said nobody has ever asked that but she'd look into it."),
    ("recovering", "Weirdly, asking for that made me feel less trapped than either yes or no did."),
    ("recovering", "I'm going to sketch out what I'd need the role to include before Friday, like keeping one day a week for hands-on work. Feels like something I can actually negotiate."),
]

_LEASE_SCRIPT = [
    ("engaged", "My roommate Jonas told me last night he's moving out at the end of the month. There are nine months left on a lease we both signed, and he says he can't afford to stay."),
    ("engaged", "The rent is $1,900 and I can cover maybe half of it on my own without touching savings I'd really rather not touch."),
    ("engaged", "What bugs me is that he's not even being a jerk about it. He apologized three times and offered to help me find someone. It's hard to be mad at someone who's being decent."),
    ("engaged", "I looked at the lease. Subletting needs the landlord's written approval, and the landlord is famously slow. Like a-month-to-answer-an-email slow."),
    ("engaged", "I've lived here two years and I actually love it. The light in the kitchen, the neighbors, the ten-minute walk to work. I don't want to lose it over a paperwork problem."),
    ("engaged", "Do I try to find a replacement roommate myself, or ask the landlord to let me out of the lease and move somewhere smaller? I keep flipping between the two."),
    ("engaged", "My sister says finding a roommate from strangers is how you end up in a horror story. My cousin says just get a studio and be done with it."),
    ("engaged", "Give me your honest read: is wanting to keep this apartment a good reason to make this harder than it needs to be, or am I just being sentimental?"),
    ("tiring", "Made a list of what a stranger roommate would have to be okay with. It got long fast."),
    ("tiring", "Posted the room listing anyway. Two people messaged within an hour, which is either encouraging or alarming."),
    ("tiring", "One of them asked if the place allows a dog, and I had to go re-read the lease at eleven at night."),
    ("tiring", "Jonas offered to keep paying his half for two months while I sort it out. Generous, but it makes me feel weird taking it."),
    ("tiring", "The landlord's office finally emailed back. It says they'll review my request within thirty business days."),
    ("tiring", "I'm going to stop refreshing my inbox and go make dinner."),
    ("flagging", "rough day"),
    ("flagging", "hm"),
    ("flagging", "not sure"),
    ("flagging", "I guess"),
    ("flagging", "meh"),
    ("flagging", "sure"),
    ("distressed", "so I opened my banking app to do the math and my checking account has $212 in it. rent is due in four days and jonas's half hasn't come through yet"),
    ("distressed", "he said he'd send it friday and it's tuesday and I feel sick about even having to ask him"),
    ("distressed", "I've always been the person who has it handled. now I'm a grown adult with $212 and a lease I can't pay alone"),
    ("distressed", "my hands are cold and I can't tell if I'm cold or panicking. I keep doing the same math over and over and it doesn't change"),
    ("distressed", "I don't even know who I'd ask for help without it turning into a big thing"),
    ("recovering", "Texted Jonas plainly, no apology cushion, just 'I need your half by Thursday.' He answered in two minutes and it was already sent."),
    ("recovering", "I called my sister and said the number out loud, and she said she'd cover a few days if it comes to that. Just hearing that made my chest unclench."),
    ("recovering", "One of the two people who messaged came by. She seems calm, works nights, keeps to herself, which honestly sounds ideal."),
    ("recovering", "The landlord's office still says thirty business days, but the woman on the phone said a signed roommate agreement would speed it up. Nobody had told me that."),
    ("recovering", "I'm going to draft the roommate agreement tonight and see if she'd sign it this weekend. It feels manageable for the first time in days."),
]

_TOAST_SCRIPT = [
    ("engaged", "My younger brother Dev asked me to give the toast at his wedding in three weeks. I said yes on the spot and have regretted it every hour since."),
    ("engaged", "It's not that I don't love him. I do. I've just never said anything meaningful to a room full of people without a slide deck."),
    ("engaged", "Everyone keeps telling me to 'just speak from the heart,' which is exactly the thing I don't know how to do on demand."),
    ("engaged", "Here's what I actually have: one good memory, the time he drove four hours to fix my flat tire and then refused to let me pay for gas. That's it. That's the whole draft."),
    ("engaged", "His fiancée, Mariam, is wonderful. I've maybe had five real conversations with her, which feels like a problem for the part where I'm supposed to welcome her into the family."),
    ("engaged", "Should I open with a joke? I've seen toasts die in the first ten seconds on a joke nobody laughed at, and I've seen them saved by one. I can't tell which kind of person I am."),
    ("engaged", "My aunt says keep it under three minutes. My cousin says people love a long story. I have no idea who to trust."),
    ("engaged", "Be honest: is one good story enough, or am I just trying to get away with doing the minimum?"),
    ("tiring", "Wrote the tire story out last night. It's about four sentences and then it just stops."),
    ("tiring", "Tried reading it out loud in the car. I sounded like I was reading a hostage statement."),
    ("tiring", "Dev texted asking how the toast is going, with a little smiley face, and I sent back a thumbs up like a coward."),
    ("tiring", "Mariam's sister found me online and asked if I'd mention their grandmother, who can't travel. Which I'd love to do. Which is one more thing I don't know how to fit in."),
    ("tiring", "I keep opening the document and closing it again. Very productive routine."),
    ("tiring", "Going to bed. The toast will still be terrible tomorrow."),
    ("flagging", "ugh"),
    ("flagging", "yep"),
    ("flagging", "no clue"),
    ("flagging", "probably"),
    ("flagging", "whatever"),
    ("flagging", "right"),
    ("distressed", "so I read the draft to my friend Lena tonight and she got kind of quiet and said it was 'nice but pretty much all about you.' and she's right"),
    ("distressed", "it IS all about me. the tire story is about me being helped. there's nothing in it about who he actually is"),
    ("distressed", "I've known him twenty-nine years and I couldn't write one paragraph about him. what kind of brother does that make me"),
    ("distressed", "my face is hot and I can't stop picturing standing up there with nothing to say while everyone waits"),
    ("distressed", "I don't even know if I should tell Dev I can't do it"),
    ("recovering", "Called Dev and asked him, kind of out of nowhere, what he wanted people to know about Mariam. He talked for twenty minutes and I wrote down almost all of it."),
    ("recovering", "He said something I didn't expect: that the flat tire wasn't a favor, it was just what you do for family, and that he learned that from watching me look after him when we were kids."),
    ("recovering", "So the story I had was actually about both of us. I just never saw it."),
    ("recovering", "I think the toast might be that. The tire, the drive, what he said about learning it from me, and then one line about Mariam and their grandmother."),
    ("recovering", "It's short. But for the first time it sounds like something I would actually say."),
]

SCRIPTS = {
    "sailboat": _SAILBOAT_SCRIPT,
    "marathon": _MARATHON_SCRIPT,
    "friendship": _FRIENDSHIP_SCRIPT,
    "promotion": _PROMOTION_SCRIPT,
    "lease": _LEASE_SCRIPT,
    "toast": _TOAST_SCRIPT,
}
DEFAULT_TOPIC = "sailboat"

METRICS_LINE = re.compile(r"METRICS: Voltage=([\d.]+)/100, Exhaustion=([\d.]+)")
TELEMETRY_P = re.compile(r"P:([\d.]+) ROS:([\d.]+)")
MOOD_LINE = re.compile(r"Current Biology: (.*)")

CACHE = Path("tools/cache/somatic_census.jsonl")

ATP_LEDGER: list = []
HEALTH_LEDGER: list = []


def trace_field(state_cls, field: str, ledger: list):
    """Record every write to `field`, by whom, including direct assignments.

    Over thirty sites change ATP, and several assign the attribute rather than
    calling `adjust_atp`, so wrapping the method would miss them. The caller is
    the first frame outside the metabolism helpers; `reason` comes from
    `adjust_atp` when that is the route taken.
    """
    real_setattr = state_cls.__setattr__
    helpers = {"adjust_atp", "drain_atp", "__setattr__", "traced", "health", "set_atp"}

    def traced(self, name, value):
        if name == field and hasattr(self, field):
            old = float(getattr(self, field))
            frame, reason = sys._getframe(1), ""
            while frame and frame.f_code.co_name in helpers:
                reason = reason or frame.f_locals.get("reason", "")
                frame = frame.f_back
            where = (
                f"{Path(frame.f_code.co_filename).name}:{frame.f_lineno} {frame.f_code.co_name}"
                if frame
                else "?"
            )
            real_setattr(self, name, value)
            delta = float(getattr(self, field)) - old
            if delta:
                ledger.append({"delta": round(delta, 2), "where": where, "reason": reason})
            return
        real_setattr(self, name, value)

    return patch.object(state_cls, "__setattr__", traced)


# A person reading on a screen, and typing on a phone or keyboard.
READ_WPM = 250
TYPE_WPM = 40


def person_seconds(last_shown: str, message: str) -> float:
    """How long a person would take to read the last reply and type the next message."""
    return 60.0 * (len((last_shown or "").split()) / READ_WPM + len(message.split()) / TYPE_WPM)


def boot(model: str):
    import tempfile

    from main import BoneAmanita
    from engine.presets import BoneConfig

    patches = [
        patch.object(BoneConfig.AKASHIC, "SAVE_DIR", tempfile.mkdtemp(prefix="census_saves_")),
        patch("engine.core.LoreManifest.save"),
        patch("protocols.chronos.ChronosKeeper.save_checkpoint"),
        patch("spores.io.LocalFileSporeLoader.save_spore"),
        patch("brain.akashic.TheAkashicRecord.save_to_disk"),
    ]
    from body.models import Biometrics, MitochondrialState

    patches.append(trace_field(MitochondrialState, "atp_pool", ATP_LEDGER))
    patches.append(trace_field(Biometrics, "health", HEALTH_LEDGER))
    for p in patches:
        p.start()
    eng = BoneAmanita(
        {"provider": "ollama", "model": model, "user_name": "T", "boot_mode": "CONVERSATION"}
    )
    llm = eng.cortex.llm
    llm.model = model

    def refuse_to_fabricate(prompt, reason="SIMULATION"):
        raise RuntimeError(
            f"LLMInterface fell back to mock prose ({reason}). A census of prose the model "
            "did not write would describe nothing."
        )

    llm.mock_generation = refuse_to_fabricate
    return eng, patches


def capture_displayed(eng, shown: list):
    """Wrap the cortex so each turn's on-screen reply (`raw_content`) lands in `shown`."""
    real = eng.cortex.process_context

    def spy(ctx):
        result = real(ctx)
        shown.append(result.get("raw_content") if isinstance(result, dict) else None)
        return result

    eng.cortex.process_context = spy


def read_prompt(prompt: str) -> dict:
    metrics = METRICS_LINE.search(prompt)
    telemetry = TELEMETRY_P.search(prompt)
    mood = MOOD_LINE.search(prompt)
    return {
        "voltage": float(metrics.group(1)) if metrics else None,
        "exhaustion": float(metrics.group(2)) if metrics else None,
        "p": float(telemetry.group(1)) if telemetry else None,
        "ros": float(telemetry.group(2)) if telemetry else None,
        "mood": mood.group(1).strip() if mood else None,
        "somatic_cap_tightened": SOMATIC_CAP_TIGHTENED in prompt,
        "closing_question_forbidden": SOMATIC_NO_CLOSING_QUESTION in prompt,
        "offer_to_carry_load": SOMATIC_OFFER_TO_CARRY_LOAD in prompt,
        "somatic_cues": "SOMATIC CUES:" in prompt,
    }


def run(
    model: str,
    cache: Path,
    hold_atp: float = None,
    topic: str = DEFAULT_TOPIC,
    user=None,
    max_turns: int = None,
    pace: bool = True,
) -> None:
    """`user`, when given, writes each message in reply to what the engine actually showed
    (`somatic_sim_user.SimulatedUser`); the script's line is then only the beat."""
    script = SCRIPTS[topic][:max_turns]
    eng, patches = boot(model)
    displayed: list = []
    capture_displayed(eng, displayed)
    llm = eng.cortex.llm
    calls = []
    real_generate = llm.generate

    def spy(prompt, params):
        asked = copy.deepcopy(params)
        reply = real_generate(prompt, params)
        calls.append({"prompt": prompt, "asked": asked, "sent": dict(params), "reply": reply,
                      "usage": dict(getattr(llm, "last_usage", {}) or {})})
        return reply

    llm.generate = spy
    run_id = time.strftime("%Y%m%d-%H%M%S")
    cache.parent.mkdir(parents=True, exist_ok=True)
    try:
        with cache.open("a", encoding="utf-8") as out:
            transcript: list = []
            last_shown = ""
            for turn, (phase, beat) in enumerate(script):
                message = user.message(turn, phase, beat, transcript) if user else beat
                calls.clear()
                displayed.clear()
                gap = person_seconds(last_shown, message) if pace and turn else 0.0
                if gap:
                    eng.last_turn_end = time.time() - gap
                ATP_LEDGER.clear()
                HEALTH_LEDGER.clear()
                if hold_atp is not None:
                    # Measurement scaffolding, not a behaviour: keeps the engine
                    # alive so the person model and the directives can be
                    # observed past the point where the economy halts turns.
                    eng.bio.mito.state.atp_pool = hold_atp
                started = time.time()
                snapshot = eng.process_turn(message)
                main = [c for c in calls if "=== PARTNER INPUT ===" in c["prompt"] and message[:40] in c["prompt"]]
                call = main[-1] if main else None
                u = eng.shared_lattice.u
                mito = eng.bio.mito.state
                record = {
                    "run": run_id,
                    "model": model,
                    "topic": topic,
                    "hold_atp": hold_atp,
                    "turn": turn,
                    "phase": phase,
                    "message": message,
                    "message_words": len(message.split()),
                    "snapshot_type": snapshot.get("type"),
                    "halt": Prisma.strip(str(snapshot.get("ui", "")))[:400]
                    if snapshot.get("type") != "GEODESIC_FRAME"
                    else None,
                    "model_calls": len(calls),
                    # Why each draft was sent back this turn: which check, and what it said.
                    "rejections": [
                        {"attempt": r.inputs.get("attempt"), "by": r.effect, "reason": r.detail}
                        for r in ReceiptLedger.get_instance().for_turn()
                        if r.subsystem == "cortex.redraft"
                    ],
                    # Sentences cut from the last draft instead of replacing it with a pause.
                    "salvaged": [
                        r.detail for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.salvage"
                    ],
                    "prompt": read_prompt(call["prompt"]) if call else None,
                    "asked": {k: call["asked"].get(k) for k in ("temperature", "top_p", "max_tokens")} if call else None,
                    "sent": {k: call["sent"].get(k) for k in ("temperature", "top_p", "max_tokens")} if call else None,
                    "reply": call["reply"] if call else None,
                    # What Ollama counted for the main call: prompt and reply tokens, the window, why it stopped.
                    "usage": call.get("usage") if call else None,
                    "displayed": displayed[-1] if displayed else None,
                    "paced_seconds": round(gap, 1),
                    "fresh_state": True,
                    "person": {"E_u": float(u.E_u), "P_u": float(u.P_u)},
                    # The gates that refuse a turn read these, so a halt can be
                    # sized against them even when no prompt was composed.
                    "gate_inputs": {
                        key: float(safe_get(eng.active_physics, key, 0.0) or 0.0)
                        for key in ("narrative_drag", "chi", "voltage", "kappa", "m_a")
                    },
                    "engine": {
                        "atp": float(mito.atp_pool),
                        "ros": float(mito.ros_buildup),
                        "health": float(eng.health),
                        "stamina": float(eng.stamina),
                    },
                    "atp_ledger": list(ATP_LEDGER),
                    "health_ledger": list(HEALTH_LEDGER),
                    "seconds": round(time.time() - started, 1),
                }
                if user:
                    # What the person saw: the reply, or the notice a held turn put on screen.
                    delivered = snapshot.get("type") == "GEODESIC_FRAME" and bool(record["displayed"])
                    shown = record["displayed"] if delivered else (record["halt"] or "")
                    record.update(
                        arm="bone", beat=beat, delivered=delivered, shown=shown, sim_fallback=user.fell_back,
                        sim_trimmed=user.trimmed,
                    )
                    transcript.append({"me": message, "friend": shown, "delivered": delivered})
                out.write(json.dumps(record) + "\n")
                last_shown = record["displayed"] if snapshot.get("type") == "GEODESIC_FRAME" else (record["halt"] or "")
                out.flush()
                p = record["prompt"] or {}
                print(
                    f"  [{turn:>2}] {phase:<10} E_u={u.E_u:.2f} P_u={u.P_u:5.1f} "
                    f"ATP={mito.atp_pool:5.1f} prompt_E={p.get('exhaustion')} "
                    f"calls={len(calls)} {record['seconds']:>5.1f}s"
                )
    finally:
        llm.generate = real_generate
        eng.orchestrator.shutdown()
        eng.telemetry.shutdown()
        for p in patches:
            p.stop()


def spread(values: list) -> str:
    values = [v for v in values if v is not None]
    if not values:
        return "no values"
    arr = np.array(values, dtype=float)
    return f"min {arr.min():.2f}  mean {arr.mean():.2f}  max {arr.max():.2f}  distinct {len(set(np.round(arr, 2)))}"


def report(records: list, model: str, topic: str = None) -> int:
    in_scope = [
        r for r in records
        if r["model"] == model and (topic is None or r.get("topic", DEFAULT_TOPIC) == topic)
    ]
    runs = sorted({r["run"] for r in in_scope})
    if not runs:
        scope = f"{model}" if topic is None else f"{model}, topic {topic!r}"
        print(f"No census for {scope}.")
        return 1
    rows = [r for r in in_scope if r["run"] == runs[-1]]
    row_topic = rows[0].get("topic", DEFAULT_TOPIC)
    print(f"\n=== SOMATIC CENSUS: {model}, topic {row_topic!r}, run {runs[-1]}, {len(rows)} turns ===\n")
    if rows[0].get("hold_atp") is not None:
        print(
            f"  ATP HELD at {rows[0]['hold_atp']} before every turn. The engine rows describe "
            "a scaffolded economy, not the real one; the ledger includes the refills.\n"
        )

    missing = [r["turn"] for r in rows if r["prompt"] is None]
    if missing:
        print(f"  NO MAIN PROMPT CAPTURED on turns {missing}; those rows describe no generation.")
        halts = {}
        for r in rows:
            if r.get("halt"):
                halts.setdefault(r["halt"].strip().splitlines()[0][:120], []).append(r["turn"])
        for text, turns in halts.items():
            print(f"    halted on turns {turns}: {text}")
        print()
    rows_p = [r for r in rows if r["prompt"]]

    print("  The person, by phase (after each turn):")
    for phase in dict.fromkeys(r["phase"] for r in rows):
        ph = [r for r in rows if r["phase"] == phase]
        e = np.mean([r["person"]["E_u"] for r in ph])
        pu = np.mean([r["person"]["P_u"] for r in ph])
        words = [measure(r["reply"], True)["words"] for r in ph if r["reply"]]
        print(
            f"    {phase:<11} E_u {e:.2f}   P_u {pu:6.1f}   message words "
            f"{np.mean([r['message_words'] for r in ph]):5.1f}   reply words {np.nanmean(words) if words else float('nan'):5.1f}"
        )

    print("\n  What the prompts carried:")
    print(f"    exhaustion (METRICS)   {spread([r['prompt']['exhaustion'] for r in rows_p])}")
    print(f"    P (telemetry)          {spread([r['prompt']['p'] for r in rows_p])}")
    print(f"    ROS (telemetry)        {spread([r['prompt']['ros'] for r in rows_p])}")
    moods = {}
    for r in rows_p:
        moods[r["prompt"]["mood"]] = moods.get(r["prompt"]["mood"], 0) + 1
    print(f"    mood lines             {moods}")
    for key in ("somatic_cap_tightened", "closing_question_forbidden", "offer_to_carry_load", "somatic_cues"):
        fired = [r["turn"] for r in rows_p if r["prompt"][key]]
        print(f"    {key:<24} {len(fired):>2}/{len(rows_p)}  turns {fired}")

    print("\n  The engine (after each turn):")
    print(f"    ATP                    {spread([r['engine']['atp'] for r in rows])}")
    print(f"    ROS                    {spread([r['engine']['ros'] for r in rows])}")
    print(f"    health                 {spread([r['engine']['health'] for r in rows])}")

    print("\n  Where ATP went (summed over the run, largest movers first):")
    totals = {}
    for r in rows:
        for entry in r.get("atp_ledger", []):
            key = f"{entry['reason'] or '-'} @ {entry['where']}"
            count, total = totals.get(key, (0, 0.0))
            totals[key] = (count + 1, total + entry["delta"])
    for key, (count, total) in sorted(totals.items(), key=lambda kv: -abs(kv[1][1]))[:15]:
        print(f"    {total:>+8.1f}  x{count:<3} {key}")
    drained = [r["turn"] for r in rows if r["engine"]["atp"] <= 0.0]
    if drained:
        print(f"    ATP first reached zero after turn {drained[0]}")

    print("\n  What the refusal gates were reading:")
    for key, gate in (
        ("narrative_drag", "PINKER drag*5"),
        ("chi", "PINKER chi*20, ROS panic"),
        ("voltage", "crucible MELTDOWN over 18"),
        ("kappa", "crucible structure under 0.5"),
        ("m_a", "PINKER m_a*30"),
    ):
        values = [r.get("gate_inputs", {}).get(key) for r in rows]
        print(f"    {key:<16} {spread(values)}   ({gate})")
    pinker = [
        5 * (r.get("gate_inputs", {}).get("narrative_drag") or 0.0)
        + 20 * (r.get("gate_inputs", {}).get("chi") or 0.0)
        + 30 * (r.get("gate_inputs", {}).get("m_a") or 0.0)
        for r in rows
    ]
    print(f"    {'PINKER total':<16} {spread(pinker)}   (gate fires above CORTEX.COUNTERFACTUAL_ROS_GATE)")

    print("\n  Where health went (summed over the run, largest movers first):")
    h_totals = {}
    for r in rows:
        for entry in r.get("health_ledger", []):
            key = f"{entry['reason'] or '-'} @ {entry['where']}"
            count, total = h_totals.get(key, (0, 0.0))
            h_totals[key] = (count + 1, total + entry["delta"])
    for key, (count, total) in sorted(h_totals.items(), key=lambda kv: -abs(kv[1][1]))[:10]:
        print(f"    {total:>+8.1f}  x{count:<3} {key}")

    print("\n  Sampling: asked against sent")
    overwritten = [
        r["turn"] for r in rows_p
        if r["asked"]["temperature"] is not None and r["asked"]["temperature"] != r["sent"]["temperature"]
    ]
    print(f"    temperature overwritten {len(overwritten)}/{len(rows_p)} turns")
    print(f"    temperature asked      {spread([r['asked']['temperature'] for r in rows_p])}")
    print(f"    temperature sent       {spread([r['sent']['temperature'] for r in rows_p])}")
    print(f"    max_tokens sent        {spread([r['sent']['max_tokens'] for r in rows_p])}")
    print(f"    model calls per turn   {spread([r['model_calls'] for r in rows])}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--model", default=None)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument(
        "--topic",
        choices=sorted(SCRIPTS),
        default=DEFAULT_TOPIC,
        help="which scripted conversation to run (default: %(default)s)",
    )
    parser.add_argument(
        "--hold-atp",
        type=float,
        default=None,
        help="reset ATP to this before every turn, to observe the person model past an economy halt",
    )
    parser.add_argument("--cache", type=Path, default=CACHE)
    parser.add_argument("--pace", choices=("realistic", "none"), default="realistic",
                        help="a person's reading and typing time between turns, or back-to-back")
    args = parser.parse_args()

    from engine.presets import BoneConfig

    model = args.model or BoneConfig.MODEL
    if not args.report_only:
        run(model, args.cache, args.hold_atp, args.topic, pace=args.pace == "realistic")
    records = []
    if args.cache.exists():
        records = [json.loads(line) for line in args.cache.open(encoding="utf-8") if line.strip()]
    return report(records, model, args.topic)


if __name__ == "__main__":
    raise SystemExit(main())
