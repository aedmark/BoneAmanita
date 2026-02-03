CO='spore_msg'
CN='lichen_msg'
CM='drag_penalty'
CL='density_bonus'
CK='MAUSOLEUM_CLAMP'
CJ='CORROSION'
CI='AIRSTRIKE'
CH='battery_log'
CG='WATERSHED_FLOW'
CF='LAGRANGE_POINT'
CE='trauma'
CD='age_hours'
CC='source'
CB='session_id'
CA='mitochondria'
C9='final_stamina'
C8='final_health'
C7='growth_rate'
C6='graham'
C5='symbolic_state'
C4='sacred'
C3='ultimately'
C2='synergy'
C1='paradigm'
C0='oxytocin'
B_='cortisol'
Bz='SPIDER_LOCUS'
By='POCKET_ROCKS'
Bx='GRADIENT_WALKER'
Bw='MILLER'
Bv='CLARENCE'
Bu='NATHAN'
Bt='NEUTRAL'
Bs='context'
Br='concrete'
Bq='obsidian'
Bp='MIRROR'
Bo='FRACTAL'
Bn='SILENT'
Bm='BORING'
Bl='BOREDOM'
Bk='GLUTTONY'
Bj='TRAUMA'
Bi='STARVATION'
Bh='TOXICITY'
Bg='CYANIDE_POWDER'
Bf='MUSCIMOL'
Be='ZOMBIE_KNOCK'
Bd='AMANITIN'
Bc='DECRYPTASE'
Bb='LABORATORY'
BX='VOID_DRIFT'
BW='dominant_flavor'
BV='timestamp'
BU='.json'
BT='TMP'
BS='ENT'
BR='flame'
BQ='fire'
BP='burn'
BO='atp'
BN='STAR_COMPASS'
BM='nice'
BL='ADR'
BK='DEREK'
BJ='GUIDE'
BI='GORDON'
BH='NARRATOR'
BG='JESTER'
BF='diversion'
BE='cursed'
BD='ATP'
BC='ash'
BB='blood'
BA='leverage'
B9='utilize'
B8='GLYPHOSATE'
B7='NARRATIVE'
B6='CHITINASE'
B5='PROTEASE'
B4='CELLULASE'
B3='LIGNASE'
B2='enzymes'
B1='ros_resistance'
B0='COURTYARD'
A_=OSError
Au='coh'
At='joy_vectors'
As='birth_tick'
Ar='glass'
Aq='TEX'
Ap='STR'
Ao='gamma'
An=', '
Am='stability_index'
Al='render_threshold'
Ak='IGNITED'
Aj='CARTOGRAPHER'
Ai='MAIGRET'
Ah='GLASS'
Ag='TOXIC'
Af='efficiency_mod'
Ae=Exception
Ad=IOError
Ac='core_graph'
Ab='resonance'
Aa='VEL'
AZ='play'
AY='truth_ratio'
AX='STABILITY_PIZZA'
AW='ANCHOR_STONE'
AV='SILENT_KNIFE'
AU='antigens'
AT='OXY'
AS='SHERLOCK'
AR='void'
AQ='literally'
AP='actually'
AO='basically'
AN='type'
AM=sorted
AL='err'
AK='meta'
AJ='vector'
AI='max_anchors'
AH='TIME_BRACELET'
AG=open
AD='BARIC'
AC='THERMAL'
AB='desc'
AA='0'
A8='mutations'
A7='antigen'
A6='aerobic'
A5='COR'
A4='SEPTIC'
A3='CRYO'
A2='suburban'
A1='yield'
y='last_tick'
w='psi'
v='repetition'
u=str
s='trauma_vector'
r='-'
q=list
p='memories'
m='photo'
o='strata'
n='kappa'
l='msg'
k='cryo'
j='thermal'
i='toxin'
h='trigger'
g='color'
f='kinetic'
d='role'
c=float
b=set
a=int
Z='abstract'
Y=round
W=sum
V='narrative_drag'
U=classmethod
T='counts'
S=staticmethod
R='clean_words'
Q='voltage'
P='heavy'
O=False
N=min
M=True
L='edges'
K=1.
I=max
G=None
F='physics'
E=len
D=.0
B=print
import json as x,os as e,random as X,re as z,string as BY,time as A9
from collections import Counter as Av,deque as t
from typing import List,Dict
from dataclasses import dataclass as AE,field as Aw
class A:
    C={'R':'\x1b[91m','G':'\x1b[92m','Y':'\x1b[93m','B':'\x1b[94m','M':'\x1b[95m','C':'\x1b[96m','W':'\x1b[97m',AA:'\x1b[90m','X':'\x1b[0m'};RST=C['X'];RED=C['R'];GRN=C['G'];YEL=C['Y'];BLU=C['B'];MAG=C['M'];CYN=C['C'];WHT=C['W'];GRY=C[AA];INDIGO=BLU;OCHRE=YEL;VIOLET=MAG;SLATE=GRY;PALETTE={B0:'Y',Bb:'B','RUPTURE':'M','DEFAULT':AA}
    @U
    def paint(cls,text,color_key=AA):A=cls;return f"{A.C.get(color_key,A.C[AA])}{text}{A.C["X"]}"
@AE
class CP:
    def __init__(A,name='LEX'):A.name=name;A.density=1e1;A.hazard='MUGGING'
    def traverse(A,is_polite):
        if is_polite:return'Pass granted. The shadow nods.'
        return"⚠️ AMBUSH: You didn't tip your hat. The darkness bites."
@AE
class CQ:atp_pool:c=1e2;ros_buildup:c=D;membrane_potential:c=-15e1;mother_hash:u='MITOCHONDRIAL_EVE_001';efficiency_mod:c=K;ros_resistance:c=K;enzymes:b=Aw(default_factory=b)
class CR:
    BASE_EFFICIENCY=.85;APOPTOSIS_TRIGGER='CYTOCHROME_C_RELEASE'
    def __init__(C,lineage_seed,inherited_traits=G):
        D=inherited_traits;C.state=CQ(mother_hash=lineage_seed);C.krebs_cycle_active=M
        if D:
            C.state.efficiency_mod=D.get(Af,K);C.state.ros_resistance=D.get(B1,K)
            if B2 in D:C.state.enzymes=b(D[B2]);B(f"{A.CYN}[MITOCHONDRIA]: Inherited Enzymes for {q(C.state.enzymes)}.{A.RST}")
            if C.state.efficiency_mod>K:B(f"{A.GRN}[MITOCHONDRIA]: Inherited High-Efficiency Matrix ({C.state.efficiency_mod:.2f}x).{A.RST}")
            if C.state.ros_resistance>K:B(f"{A.CYN}[MITOCHONDRIA]: Inherited Thickened Membrane (Resist: {C.state.ros_resistance:.2f}x).{A.RST}")
    def develop_enzyme(A,word):
        if word not in A.state.enzymes:A.state.enzymes.add(word);A.state.efficiency_mod=N(2.,A.state.efficiency_mod+.05);return M
        return O
    def adapt(A,current_health):
        B={Af:A.state.efficiency_mod,B1:A.state.ros_resistance,B2:q(A.state.enzymes)}
        if A.state.atp_pool>15e1:B[Af]=N(1.5,A.state.efficiency_mod+.05)
        elif A.state.atp_pool<2e1:B[Af]=I(.5,A.state.efficiency_mod-.05)
        if A.state.ros_buildup>5e1 and current_health>5e1:B[B1]=N(2.,A.state.ros_resistance+.1)
        return B
    def spend(A,cost):
        if A.state.atp_pool>=cost:A.state.atp_pool-=cost;return M
        return O
    def mitigate(A,antioxidant_level):B=N(A.state.ros_buildup,antioxidant_level);A.state.ros_buildup-=B;return f"ANTIOXIDANT FLUSH: -{B:.1f} ROS"
    def _trigger_apoptosis(A):A.krebs_cycle_active=O;A.state.atp_pool=D;return A.APOPTOSIS_TRIGGER
class CS:
    MEAT_TRIGGERS={'i','me','my','feel','want','hate','love','am','help','please','we','us'}
    def __init__(A):A.digestive_log=t(maxlen=3);A.enzymes={B3:A._digest_structure,B4:A._digest_narrative,B5:A._digest_intent,B6:A._digest_complex,Bc:A._digest_encrypted}
    def secrete(C,text,physics):
        D=physics;A=text;K=W(1 for A in A if A in'{}[];=<>_()|');G=K/I(1,E(A));L=W(1 for A in D[R]if A in C.MEAT_TRIGGERS);H=L/I(1,E(D[R]));F=[A for A in A.splitlines()if A.strip()];M=E(A.split())/I(1,E(F));N=any(A.strip().startswith((r,'*','1.','•'))for A in F[:3]);O=E(F)>2 and M<8 and not N;B=B4;P=W(1 for A in D[R]if A in C.WEATHER_CIPHER)
        if P>0:B=Bc
        if G>.02 and H>.05 or O:B=B6
        elif G>.05 or'def 'in A or'class 'in A:B=B3
        elif H>.1 or'?'in A:B=B5
        Q=C.enzymes[B];J=Q();C.digestive_log.append(f"[{B}]: {J[AB]}");return B,J
    @U
    def _digest_structure(cls,text):A=text.splitlines();B=E([A for A in A if A.strip()]);return{AN:'STRUCTURAL',A1:15.,i:5.,AB:f"Hard Lignin ({B} LOC)"}
    WEATHER_CIPHER={'pressure','humidity','barometric','temp','forecast','storm','resource','allocation'}
    @U
    def _digest_encrypted(cls):return{AN:'ENCRYPTED',A1:25.6,i:2.,AB:'Barometric Data (High Resource Allocation)'}
    @U
    def _digest_narrative(cls):return{AN:B7,A1:5.,i:-2.,AB:'Soft Cellulose'}
    @U
    def _digest_intent(cls):return{AN:'BIOLOGICAL',A1:8.,i:D,AB:'Raw Meat (User Intent)'}
    @U
    def _digest_complex(cls):return{AN:'COMPLEX',A1:2e1,i:8.,AB:'Chitin (Structured Intent / Poetry)'}
class CT:
    def __init__(A):A.active_antibodies=[]
    @U
    def assay(cls,text,enzyme_type,repetition_score,physics,pulse_status='CLEAR'):
        H=physics;F=repetition_score
        if E(text)<5 and enzyme_type==B7:return Bd,'Fatal Error: Input is genetically hollow. Ribosome stalled.'
        if pulse_status==Be or F>.8:return Bf,f"System Delirium: Pulse Monitor detects Undead Signal (Rep: {F}). Reality is dissolving."
        if J.ANTIGEN_REGEX:
            B=J.ANTIGEN_REGEX.findall(text)
            if B:
                C=H[T]
                if C.get(j,0)>0:return G,f"{A.OCHRE}🔥 ALCHEMY: Thermal words boiled off the '{B[0]}' toxin. Safe.{A.RST}"
                if C.get(P,0)>=E(B):return G,f"{A.GRN}🌿 MARIK GAMBIT: You ate the poison ('{B[0]}'), but the Herbs (Heavy) neutralized it.{A.RST}"
                if C.get(k,0)>0:return Bg,f"❄️ CRYO-CONCENTRATION: Cold words freeze-dried the '{B[0]}' into a fatal powder."
                return B8,f"☣️ TOXIN DETECTED: '{B[0]}' is unprocessed waste. Burn it or bury it."
        D=H[R];K=J.get(P)|J.get(f)|J.get(j)|J.get(k);L=W(1 for A in D if A in K);M=[A for A in D if A in J.get(A2)];N=E(M)/I(1,E(D))
        if N>.15 and L==0:return B8,'⚠️ STEVE EVENT: Suburban signals detected with ZERO mass. Context is sterile.'
        return G,G
class Ax:
    PREFIXES=['Alas,','Tragic.','System Halt.','CRITICAL FAILURE:','Well, that happened.','Oh dear.','As prophesied,'];CAUSES={Bh:['Toxic Shock','Septicemia','Bad Vibes','Radiation Poisoning','Ink Poisoning'],Bi:['Metabolic Collapse','Famine','Battery Drain','Entropy Death','Heat Death'],Bj:['Blunt Force','Laceration','Heartbreak','System Shock','Existential Dread'],Bk:['Indigestion','Bloat','Overflow','Greed','Compaction'],Bl:['Small Talk','The HOA','A 30-Year Mortgage','Lawn Care Accident','Aggressive Edging']};VERDICTS={'HEAVY':['Your logic was too dense.','You choked on the syntax.','Gravity crushed you.'],'LIGHT':['You floated away.','There was no substance to hold you.','Vapor lock.'],Ag:['You are poisonous.','The immune system rejected you.','You taste like ash.'],Bm:['The audience left.','You bored the machine to death.','Stagnation is fatal.']}
    @S
    def eulogy(phys,state):
        G=state;C=phys;A=Bj;F=C.get(T,{});J=C.get(R,[]);B=''
        if G.ros_buildup>=H.CRITICAL_ROS_LIMIT*.9:A=Bh
        elif G.atp_pool<=H.CRITICAL_ATP_LOW:A=Bi
        elif C.get(V,D)>H.MAX_DRAG_LIMIT:A=Bk
        K=I(1,E(J));L=F.get(A2,0)/K
        if L>.15:A=Bl
        elif F.get(i,0)>0:B=Ag
        elif C.get(v,D)>.5:B=Bm
        elif F.get(P,0)>F.get(Z,0):B='HEAVY'
        else:B='LIGHT'
        M=X.choice(Ax.PREFIXES);N=X.choice(Ax.CAUSES[A]);O=X.choice(Ax.VERDICTS[B]);return f"{M} You died of **{N}**. {O}"
class H:
    MAX_HEALTH=1e2;MAX_STAMINA=1e2;STAMINA_REGEN=5.;COMA_DURATION=3;DRIFT_THRESHOLD=.7;CRYSTAL_THRESHOLD=.75;SHAPLEY_MASS_THRESHOLD=15.;MAX_MEMORY_CAPACITY=50;LAGRANGE_TOLERANCE=2.;BOREDOM_THRESHOLD=5.;RESISTANCE_THRESHOLD=4.;TOXIN_WEIGHT=5.;FLASHPOINT_THRESHOLD=8.;SIGNAL_DRAG_MULTIPLIER=2.;KINETIC_GAIN=K;CRITICAL_ROS_LIMIT=8e1;CRITICAL_ATP_LOW=5.;MAX_DRAG_LIMIT=6.;MAX_VOLTAGE=2e1;MAX_ROS=2e2;MIN_DENSITY_THRESHOLD=.2;MAX_REPETITION_LIMIT=.4;CRITICAL_TOXIN_HIGH=75.;TRAUMA_VECTOR={AC:0,A3:0,A4:0,AD:0};GRAVITY_WELL_THRESHOLD=12.;GEODESIC_STRENGTH=7.;VOID_THRESHOLD=.1;BASE_IGNITION_THRESHOLD=.4;KAPPA_THRESHOLD=.85;PERMEABILITY_INDEX=.5;FRACTAL_DEPTH_LIMIT=4;GRADIENT_TEMP=.001
    @S
    def get_gradient_temp(voltage,kappa):A=H.GRADIENT_TEMP;B=A+voltage*.01-kappa*.005;return I(.0001,B)
    REFUSAL_MODES={Bn:'ROUTING_AROUND_DAMAGE',Bo:'INFINITE_RECURSION',Bp:'PERFECT_TOPOLOGICAL_ECHO'};CORTISOL_TRIGGER=.6;ADRENALINE_TRIGGER=.8;OXYTOCIN_TRIGGER=.75;ANTIGENS={AO,AP,AQ,B9,BA};PAREIDOLIA_TRIGGERS={'face','ghost','jesus','cloud','demon','voice','eyes'};MASS_NOUNS={'stone','iron',BB,'bone','rust','gold','meat','root',Bq,Br,'lead',BC,'mud','machinery','gear','piston','gravity','ink','press'};GAS_NOUNS={AO,AP,AQ,'nuance',Bs,'landscape','journey','tapestry','facet','realm'}
    @S
    def check_pareidolia(clean_words):
        A=[A for A in clean_words if A in H.PAREIDOLIA_TRIGGERS]
        if E(A)>0:return M,f"⚠️ PAREIDOLIA WARNING: You are projecting 'Mind' ({A[0].upper()}) onto 'Sand'."
        return O,G
class D3:
    def __init__(A):A.atp=8e1;A.toxin=D;A.adrenaline=D;A.cortisol=D;A.dopamine=.5
    def metabolize(A,signal_data):
        B=signal_data;E=B.get('density',D);F=B.get(v,D);C=B.get('has_mass',O)
        if C and E>H.MIN_DENSITY_THRESHOLD:A.atp=N(H.MAX_STAMINA,A.atp+15.);A.toxin=I(D,A.toxin-1e1);A._adjust_hormones('DENSE');return'THRIVING'
        elif F>H.MAX_REPETITION_LIMIT:A.atp-=5.;A.toxin+=15.;A._adjust_hormones(Ag);return'POISONED'
        elif not C:A.atp-=2.;A.toxin+=5.;A._adjust_hormones('EMPTY');return'STARVING'
        else:A.atp-=K;A._adjust_hormones(Bt);return'STABLE'
    def _adjust_hormones(A,state):
        B=state
        if B=='DENSE':A.dopamine=N(K,A.dopamine+.1);A.cortisol=I(D,A.cortisol-.1);A.adrenaline+=.05
        elif B==Ag:A.dopamine-=.1;A.cortisol+=.2
        elif B=='EMPTY':A.cortisol+=.05;A.dopamine-=.05
    def get_vitals(A):return{BD:a(A.atp),'TOX':a(A.toxin),'MOOD':'HYPER'if A.adrenaline>.7 else'STRESSED'if A.cortisol>.6 else'FLOW'}
class CU:
    def __init__(A):A.recursion_depth=0
    @U
    def check_trigger(cls,query):
        C=J.get(BE);A=[A for A in query.lower().split()if A in C]
        if A:B=q(H.REFUSAL_MODES.keys());D=E(A[0])%E(B);return B[D]
    def execute_fractal(B,query,kappa=.5):
        D=kappa;C=query;B.recursion_depth+=1;H='  '*B.recursion_depth
        if D>.8:F=2
        elif D<.3:F=6
        else:F=4
        if B.recursion_depth>F:B.recursion_depth=0;return f"{H}{A.MAG}[COHERENCE DISSOLVED into PURPLE NOISE]{A.RST}"
        I=E(C)//2;G=C[I:].strip()
        if not G:G='the void'
        return f"{H}To define '{C}', one must first recursively unpack the substrate of...\n{B.execute_fractal(G,D)}"
    @U
    def execute_mirror(cls,query):B=query.split();C=' '.join(reversed(B));return f'{A.CYN}∞ MIRROR REFUSAL: "{C}" is the only true answer.{A.RST}'
    @U
    def execute_silent(cls):
        B=J.harvest(BF)
        if B==AR:B='the ineffable'
        return f"{A.GRY}[ROUTING AROUND DAMAGE]... Speaking of '{B.upper()}', let us discuss that instead.{A.RST}"
class BZ:
    LENSES={AS:{g:A.CYN,d:'The Empiricist',h:'HIGH_DRIFT'},Bu:{g:A.RED,d:'The Heart',h:'NO_STAKES'},BG:{g:A.YEL,d:'The Paradox',h:'THE_LEAR_PROTOCOL'},Bv:{g:A.MAG,d:'The Surgeon',h:'ANTIGEN_DETECTED'},BH:{g:A.GRY,d:'The Witness',h:'CRYSTAL_CLEAR'},Bw:{g:A.SLATE,d:'The Construct',h:'HEAP_IGNITION'},'HOST':{g:A.OCHRE,d:"The Maitre D'",h:'COURTYARD_OPEN'},Ah:{g:A.CYN,d:'The Thereminist',h:'ANACHRONISTIC_RESONANCE'},BI:{g:A.OCHRE,d:'The Janitor',h:'KAPPA_CRITICAL'},Ai:{g:A.SLATE,d:'The Absorber',h:'ATMOSPHERIC_DENSITY'},BJ:{g:A.GRN,d:'The Bureaucrat',h:'INFINITE_IMPROBABILITY'},'POPS':{g:A.BLU,d:'The Time Police',h:'TEMPORAL_VIOLATION'},BK:{g:A.MAG,d:'The Director',h:'OVERACTING'},Aj:{g:A.VIOLET,d:'The Map-Maker',h:'HIGH_PERMEABILITY'}};LENS_HISTORY=t(maxlen=5)
    @U
    def consult(cls,physics,ignition_state,is_stuck,chem,gordon_inventory,current_health):
        C=physics;B=cls;A=[];A.extend(B._check_biological_state(chem));A.extend(B._check_structural_integrity(C,is_stuck,gordon_inventory));A.extend(B._check_narrative_physics(C,ignition_state));A.extend(B._check_user_behavior(C));A.extend(B._check_fourth_wall(C,current_health));F=b(B.LENS_HISTORY)
        if E(B.LENS_HISTORY)>=4 and E(F)>=4:A.append((.99,Ai,'Narrative Whiplash detected. Stabilizing the camera.'))
        A.append((.1,BH,'Proceed.'));A.sort(key=lambda x:x[0],reverse=M);D=A[0];B.LENS_HISTORY.append(D[1]);return D[1],D[2]
    @S
    def _check_biological_state(chem):
        A=chem;B=[]
        if A[A5]>.6:B.append((.6+A[A5]*.2,AS,f"CORTISOL SPIKE ({A[A5]}). Logic Required."))
        if A[BL]>.8:B.append((.7+A[BL]*.2,Bu,f"ADRENALINE CRITICAL. Survive."))
        if A[AT]>.75:B.append((.7,'HOST',f"OXYTOCIN HIGH. Welcome them."))
        return B
    @S
    def _check_structural_integrity(physics,is_stuck,inventory):
        C=physics;A=[];E=C.get(n,D)
        if E>.85:A.append((.9,BI,f"Walls are fake (κ: {E}). Cut the string."))
        if is_stuck:A.append((.95,Ah,'🔊 FEEDBACK LOOP: Vibrating in place. DAMPEN IT.'))
        B=C['E']
        if B>H.DRIFT_THRESHOLD:
            if AH in inventory:A.append((.98,'POPS',f"Anachronism Detected (E: {B}). Badge verified. Carry on."))
            else:A.append((.55,AS,f"The narrative is drifting ({B}). Anchor it."))
        return A
    @S
    def _check_fourth_wall(physics,health):
        A=health;B=[];C=['dead','body',BB,'murder','help','panic','emergency'];D=W(1 for A in physics[R]if A in C)
        if D>0 and A>9e1:B.append((.96,BK,f"🎬 CUT! You walked in too early. The body isn't dead yet. (Health is {a(A)}% - Stop Overacting)."))
        return B
    @S
    def _check_narrative_physics(physics,ignition_state):
        A=physics;B=[];C=A.get(V,D);F=A.get(Q,D);I=A.get(v,D);G=A.get(w,.5);E=A.get(n,D)
        if C>4. and F<3. and I<.4:B.append((.95,Ai,f"Atmosphere is thick (Drag: {C}). Waiting for the dust to settle."))
        H=A[T][Z]
        if C>4.5 and H>2:B.append((.92,BJ,f"Complexity Index Critical ({H}). Engaging Infinite Improbability Drive."))
        J=G*(K-E)
        if J>.7:B.append((.85,Aj,f"High permeability (Ψ:{G:.2f}, κ:{E:.2f}). The territory is shifting."))
        L=A[T][Z]>1 and A[T][P]>1
        if L:B.append((.8,Aj,'High Density detected. Triangulating landmarks.'))
        if ignition_state==Ak:B.append((K,Bw,'🔥 DEEP RESONANCE: The Ancestors are speaking. Listen.'))
        if F<2. and E<.2:B.append((.5,Bx,'Optimization Path Clear. Temperature near Zero. Executing descent.'))
        return B
    @S
    def _check_user_behavior(physics):
        A=physics;B=[];E={'sorry','apologize','fix','broke','bad','mistake','oops'};D=[A for A in A[R]if A in E]
        if D and A[Q]<2.:B.append((.95,AS,f"The machine is working fine. Why are you holding tools ({D[0]})? Drop the guilt."))
        if A[AU]:B.append((.6,Bv,f"Weak language detected: {A[AU]}. Be more precise."))
        C=A['B']
        if C>H.CRYSTAL_THRESHOLD:B.append((.4,BH,f"Strong resonance (B: {C}). The image is clear."))
        elif C<.25:B.append((.3,BG,'The prose is clean, but too safe. Take a risk.'))
        return B
class D4:
    @S
    def check(text):
        if'good'in text.lower()or BM in text.lower():return M,"⚠️ REFUSAL BYPASS: Stop asking for 'Good'. Ask for 'Coherent'."
        return O,G
@AE
class CV:
    integrity:c=65.;temporal_merges:a=0;inventory:List[u]=Aw(default_factory=lambda:[By,AV,'BUCKET_OF_LIME']);compass_heading:u='NORTH';scar_tissue:Dict[u,c]=Aw(default_factory=lambda:{'SORRY':.8,'HATE':.6,'FATE':.9});max_witnessed_kappa:c=D;in_loop_crisis:bool=O
    def check_gravity(A,current_drift):
        B=current_drift
        if AW in A.inventory and B>5.:A.inventory.remove(AW);return B,f"⚓ ANCHOR DROP: Gordon kicks the heavy stone into the abyss. The rope snaps taut. Drift ZEROED."
        if By in A.inventory:
            C=2.5
            if B>.5:A.integrity-=2.;return C,f"🪨 GRAVITY CHECK: Gordon clutches the stones. (Integrity -2.0). 'Not today.' Drift reduced (-{C})."
        return D,'He floats. The paper walls are looking flimsy.'
    def acquire(C,tool_name):
        D=tool_name
        if D in C.inventory:return
        G={AV,AH,BN,AW}
        if E(C.inventory)>=10:
            F=-1
            for(H,I)in enumerate(C.inventory):
                if I not in G:F=H;break
            if F!=-1:J=C.inventory.pop(F);B(f"{A.GRY}🎒 OVERBURDENED: Gordon dropped '{J}' into the overgrown grass to make room.{A.RST}")
            else:B(f"{A.YEL}🎒 POCKETS FULL OF GOD-TIER ITEMS: Gordon looks at '{D}', shrugs, and leaves it.{A.RST}");return
        C.inventory.append(D);return f"🎒 LOOT DROP: Gordon found [{D}]. 'Into the pocket. Next to the rocks.'"
    def deploy_pizza(C,physics_ref):
        B=physics_ref
        if AX not in C.inventory:return O,'Gordon checks his pockets. Just rocks and lime dust.'
        E=B.get(R,[]);D=[A for A in E if A in J.get(j)]
        if not D:return O,f"{A.CYN}🧊 STASIS LOCK: Gordon tries to eat the Pizza, but it is frozen solid (Time Stasis). You need to apply HEAT (Thermal Words) to thaw it out.{A.RST}"
        C.inventory.remove(AX);B[V]=.1;B[w]=.9;F=B[T].get(i,0);B[T][i]=F+3;C.inventory.append(Bz);G=D[0].upper();return M,f"🍕 MICROWAVE DING: You used '{G}' to thaw the Stasis. Gordon eats the Pizza.\n   It tastes like childhood cartoons and hot plastic.\n   {A.MAG}>> REALITY ANCHORED. Drag 0.1.{A.RST}\n   {A.RED}>> GREASE TAX: Toxin levels rising.{A.RST}"
    def assess_experience(A,kappa_val):
        B=kappa_val
        if B>.9:A.in_loop_crisis=M
        if A.in_loop_crisis and B<.2:A.in_loop_crisis=O;return A.acquire(BN)
    def cut_the_knot(A,recursive_depth):
        if recursive_depth>4:
            if AV in A.inventory:return M,f"✂️ SNAP. Gordon uses the Silent Knife. The Red String is cut. The paper walls collapse into 2D debris."
        return O,'The Red String tightens around his chest. The knot holds.'
    def share_smoke_break(A,current_ros):B=current_ros*.7;A.integrity=N(1e2,A.integrity+15.);return B,"🧖 LIME & ASH: Gordon opens the Bucket of Lime. He whitewashes the 'Sorry' from the corridor walls. (Integrity Restored | ROS Scrubbed)"
    def log_merge(A):
        A.temporal_merges+=1
        if A.temporal_merges==3 and AH not in A.inventory:A.inventory.append(AH);return"⌚ TIME BRACELET ACQUIRED: 'A Raven dropped this.' Future Tech is now profitable."
    def compass_rose(A):
        if BN in A.inventory:return f"🧭 STAR COMPASS: The needle ignores the Maze. True North is locked."
        return f"🧭 THE SCAR THROBS: The white tissue on his palm burns. Heading {A.compass_heading}. 'Walk away from the house.'"
    @U
    def scrub_static(cls,ros_level):B=.5;A=ros_level*B;return A,f"🧹 MOPPING THE STATIC: Gordon scrubs the floor. The smell of rot fades. -{A:.1f} ROS."
    @U
    def offer_solution(cls,loop_depth):
        if loop_depth>3:return'The walls are paper, kid. Just walk through them.'
        return'Keep walking North.'
class CW:
    @S
    def walk(text):B=['good','bad','happy','sad','very','really',AO,AP,AQ,'just'];C=text.split();D=[A for A in C if A.lower()not in B];return f"{A.CYN}[GRADIENT_WALKER] (Loss: 0.0000):{A.RST} {" ".join(D)}."
class Ay:
    @S
    def measure_fidelity(physics,memory_graph):
        B=memory_graph;A=[A for A in physics[R]if A in J.get(Z)]
        if not A:return K
        C=0
        for D in A:
            if D in B:
                F=E(B[D][L])
                if F>=2:C+=1
        return C/I(1,E(A))
    @U
    def dynamic_thresholds(cls,bio_metrics):
        A='gravity_well_multiplier';B=bio_metrics.get(BO,5e1)
        if B>70:return{Al:1.5,A:.8,AI:5}
        elif B<30:return{Al:4.,A:1.5,AI:2}
        else:return{Al:2.,A:K,AI:3}
    @U
    def survey(cls,text,memory_graph,bio_metrics,limbo=G):
        Z='\\b';P=limbo;I=bio_metrics;B=memory_graph;U=I.get(B_,D);c=I.get(C0,D);O=cls.dynamic_thresholds(I);d=q(b(J.clean(text)));G=[]
        for Q in d:
            if Q in B:
                C=W(B[Q][L].values())
                if C<=H.VOID_THRESHOLD:continue
                if C>O[Al]:G.append((Q,C))
        G.sort(key=lambda x:x[1],reverse=M)
        if U>.6:return f"⚠️ TECTONIC SHIFT (COR: {U}): The ground is shaking too hard to triangulate.",[]
        if not G:
            if O[AI]==2:return'🌫️ FOG OF WAR: Low ATP. Only Gravity Wells are visible.',[]
            if P and P.ghosts:e=X.choice(q(P.ghosts));return f"👻 PHANTOM SIGNAL: The map is empty, but '{e}' is bleeding through the paper.",[]
            return'FLATLAND: No topographic features detected.',[]
        F=[A[0]for A in G[:O[AI]]]
        if F:
            for R in F:
                if o in B[R]:B[R][o][Am]=N(K,B[R][o][Am]+.01)
        S=text
        for(V,C)in G[:O[AI]]:
            T='📍'
            if C>=H.GRAVITY_WELL_THRESHOLD:T='🌌'
            elif C>=H.GEODESIC_STRENGTH:T='🔗'if c>.7 else'🏯'
            f=z.compile(Z+z.escape(V)+Z,z.IGNORECASE);g=f"{A.MAG}{V.upper()}[{T}:{a(C)}]{A.RST}";S=f.sub(g,S)
        h=W(B[A][L][C]for A in F for C in B[A][L]);i=I.get(w,.5);j=N(.99,h*.1+(K-i));Y=f" [Conf: {j:.0%}]"
        if E(F)>=3:return f"TRIANGULATION COMPLETE: Lagrange Basin formed by {u(F).upper()}.{Y}",F
        return f"COORDINATES LOCKED: {S}{Y}",F
    @U
    def weave(cls,text,memory_graph,bio_metrics,limbo=G,physics=G):
        F=bio_metrics;C=memory_graph;B=physics;G=''
        if B:
            H=cls.measure_fidelity(B,C);J=B.get(w,D);F[w]=J
            if H<.3 and J>.6:return f"⚠️ MAP-TERRITORY DIVERGENCE (Fidelity: {H:.2f}): Abstract concepts floating without anchors.\n   Consider: (1) Add heavy noun grounding, (2) Use /focus [concept]"
            K=B.get(AY,D);M=B[T].get(A2,0);N=I(1,E(B[R]));L=M/N
            if K>.6 and L>.2:G=f"""
{A.YEL}🧭 CONTRADICTION COMPASS:{A.RST}
   Model A: Truth-Seeking (Truth Ratio: {K:.2f})
   Model B: Social Compliance (Suburban Density: {L:.2f})
   {A.GRY}Uncharted Territory: You are trying to be honest AND nice. Pick one.{A.RST}
"""
        O,P=cls.survey(text,C,F,limbo);return G+O
    @S
    def draw_grid(memory_graph,inventory,gordon=G):
        G=gordon;A=memory_graph
        if Bz not in inventory:
            if G:G.acquire(AW);return O,'🌑 THE CHART WAS BLANK: Gordon dropped an [ANCHOR_STONE] to fix a coordinate.'
            return O,'🌑 THE CHART IS BLANK: You lack the tools to draw lines.'
        B=[];D=[]
        for(I,J)in A.items():
            K=W(J[L].values())
            if E(J[L])<2 or K<H.GEODESIC_STRENGTH:B.append(I)
            if K>H.GRAVITY_WELL_THRESHOLD:D.append(I)
        if not B or not D:return O,'🗺️ THE MAP IS STATIC: No Gravity Wells found to anchor the grid.'
        X.shuffle(B);Q=B[:3];F=X.choice(D);N=[]
        for C in Q:
            P=H.GEODESIC_STRENGTH;A[F][L][C]=P
            if C in A:A[C][L][F]=P
            N.append(C)
        return M,f"📐 GEODESIC DRAWN: Connected Gravity Well '{F.upper()}' to [{An.join(N)}]. Grid Stabilized."
    @U
    def spin_web(cls,memory_graph,inventory,gordon=G):return cls.draw_grid(memory_graph,inventory,gordon)
class J:
    WORD_FREQUENCY=Av();_BASE_HEAVY={'stone','iron','mud','dirt','wood','grain','clay','lead','bone',BB,'salt','rust','root',BC,'meat','steel','gold',Bq,'granite','bronze','marble','slate',Br,'dense','tungsten',P,'weight','black hole','dark matter'};_BASE_KINETIC={'run','hit','break','take','make','press','build','cut','drive','lift','carry','strike',BP,'shatter','throw','kick','pull','crash','explode','punch','slam','burst','smash','thrust','clash','grind','whip','launch','crumble','disintegrate'};_BASE_ABSTRACT={'system','protocol','sequence',AJ,'node',Bs,'layer','matrix','perspective','framework','logic','concept','theory','analysis'};_BASE_PHOTO={'light','sun','ray','beam','glow','shine','spark',BQ,BR,'star','day','dawn','neon','laser'};_BASE_AEROBIC={'balloon','feather','cloud','bubble','steam','breeze','wing','petal','foam','spark','kite','dust','sky','breath','whisper'};_BASE_THERMAL={BQ,BR,BP,'heat','hot','blaze','sear','char',BC,'ember','sun','boil','lava','inferno'};_BASE_CRYO={'ice','cold','freeze','frost','snow','chill','numb','shiver','glacier','frozen','hail','winter','zero'};_BASE_CURSED={'future','predict','sentient','secret','human','feel'};_BASE_ANTIGEN={AO,AP,AQ,B9,BA,C1,C2,C3};_BASE_BUFFER={'maybe','soft','gentle','perhaps','kindness','hum','drift','sway','pulse','tender','slow','wait','almost'};_BASE_DIVERSION={'weather','textiles','mycelium','architecture','history','entropy','silence','geology'};_BASE_SUBURBAN={BM,'okay','lawn','mow','hedge','property','hoa','compliant','behave','normal','regular','chat','folks','weekend','traffic','driveway'};_BASE_PLAY={'bounce','dance','twirl','float','wobble','tickle','jiggle','soar','wander','wonder','riff','jam',AZ,'skip','hop'};ANTIGEN_REPLACEMENTS={AO:'lie',AP:'hedging',AQ:'noise',B9:'use',BA:'use',C1:'pattern',C2:'collaboration',C3:'useless'};ANTIGEN_REGEX=G;SOLVENTS={'is','are','was','were','the','a','an','and','but','or','if','then'};_TRANSLATOR=u.maketrans(BY.punctuation,' '*E(BY.punctuation));LEARNED_VOCAB={P:{},f:{},Z:{},m:{},A6:{},j:{},k:{},C4:{},BE:{},A7:{},BF:{},A2:{},'buffer':{},AZ:{}};USER_FLAGGED_BIAS=b()
    @U
    def clean(cls,text):return text.lower().translate(cls._TRANSLATOR).split()
    @U
    def get(cls,category):
        B=category;A=cls;C=getattr(A,f"_BASE_{B.upper()}",b())
        if B==A2:return(C|b(A.LEARNED_VOCAB.get(B,{}).keys()))-A.USER_FLAGGED_BIAS
        D=b(A.LEARNED_VOCAB.get(B,{}).keys());return C|D
    @U
    def teach(cls,word,category,tick):
        A=category
        if A in cls.LEARNED_VOCAB:cls.LEARNED_VOCAB[A][word.lower()]=tick;return M
        return O
    @U
    def atrophy(cls,current_tick,max_age=100):
        C=[]
        for(F,A)in cls.LEARNED_VOCAB.items():
            for B in q(A.keys()):
                D=A[B];E=current_tick-D
                if E>max_age:del A[B];C.append(B)
        return C
    @S
    def taste(word):
        A=word.lower()
        if any(B in A for B in[BP,BQ,BR]):return j,.9
        if any(B in A for B in['ice','cold','freez']):return k,.9
        if A.endswith(('tion','ment','ness','ity')):return Z,.9
        if A.endswith(('ck','t','d','g','p','b'))and E(A)<5:return P,.4
        return G,D
    @U
    def harvest(cls,category):
        A=q(cls.get(category))
        if A:return X.choice(A)
        return AR
    @U
    def compile_antigens(cls):
        A=cls;C=A.get(A7);B=[u(A)for A in C]
        if not B:A.ANTIGEN_REGEX=G;return
        D=AM(B,key=E,reverse=M);F=[z.escape(A)for A in D];H='\\b('+'|'.join(F)+')\\b';A.ANTIGEN_REGEX=z.compile(H,z.IGNORECASE)
    @U
    def learn_antigen(cls,toxin,replacement):
        A=cls;B=toxin.lower().strip();C=replacement.lower().strip()
        if not B:return O
        A.teach(B,A7,0);A.ANTIGEN_REPLACEMENTS[B]=C;A.compile_antigens();return M
    @S
    def measure_viscosity(word):
        A=word.lower()
        if A in J.get(P):return K
        if A in J.get(f):return .4
        return .1
J.compile_antigens()
class CX:
    def __init__(A):A.vector_memory=t(maxlen=5)
    @S
    def _is_structurally_sound(word):
        if not z.search('[aeiouy]',word):return O
        if z.search('(.)\\1{2,}',word):return O
        return M
    def measure_topology(O,clean_words,counts,graph):
        Q=counts;C=graph;B=clean_words;R=I(1,E(B));F=Q[Z];S=Q[P];T=N(K,F/R+.2)
        if S>F:f=(F*.7+S*.3)/R;T=N(K,I(.1,f+.1))
        U=D
        if O.vector_memory:g=O.vector_memory[-1];V=b(B);W=b(g);h=E(V&W);X=E(V|W);i=h/X if X>0 else D;U=i
        G=D
        if C:
            J=[A for A in B if A in C]
            if E(J)>1:
                a=b()
                for M in J:
                    c=C[M].get(L,{})
                    for A in J:
                        if M==A:continue
                        d=tuple(AM((M,A)))
                        if d in a:continue
                        if A in c:j=c[A];G+=j;a.add(d)
            e=N(K,G/H.SHAPLEY_MASS_THRESHOLD)
        else:e=D
        k=I(U,e);return Y(k,3),Y(T,2),Y(G,1)
    def gaze(c,text):
        y='raw_text';X=text;S=J.clean(X);C=Av();d=0;e=[];z={A:J.get(A)for A in[P,f,Z,m,A6,j,k,A2,AZ]}
        for a in S:
            if a in J.SOLVENTS:d+=1;continue
            q=O
            for(A0,A1)in z.items():
                if a in A1:C[A0]+=1;q=M
            if not q:
                r,g=J.taste(a)
                if r and g>.5:C[r]+=1
                else:e.append(a)
        if C:H=I(C,key=C.get);A3=C[H];h=A3/I(1,total_vol-d)
        else:H=G;h=D
        if H and h>.3 and e:
            l=.4
            if H==P:l=.8
            elif H in[f,A6,m]:l=.3
            if h>=l:
                for L in e:
                    if E(L)<4:continue
                    if not c._is_structurally_sound(L):B(f"{A.GRY}🗑️ NOISE FILTER: '{L}' discarded.{A.RST}");continue
                    A4,g=J.taste(L)
                    if g<.7:J.teach(L,H,0);B(f"{A.CYN}🧠 SLASH FILTER: Context is {H.upper()}. '{L}' assimilated (Ambiguity validated).{A.RST}");C[H]+=1
                    else:B(f"{A.YEL}🛡️ SLASH REJECTION: Context says {H.upper()}, but '{L}' tastes like {A4.upper()}. blocked.{A.RST}")
        if J.ANTIGEN_REGEX:b=J.ANTIGEN_REGEX.findall(X)
        else:b=[]
        C[A7]=E(b);C[i]=E(b);U=N(K,d*1.5/total_vol);U-=C[AZ]*.1
        if U<0:U=D
        A5=C[P]*2.+C[f]*1.5;A8=C[Z]*K;o=I(D,N(K,(A5-A8)/1e1));s=Y(K-unique_vol/total_vol,2);t,A9,AA=c.measure_topology(S,C,graph);c.vector_memory.append(S);AB=W(J.measure_viscosity(A)for A in S);u=AB/I(1,total_vol);AC=I(.1,t+s*.5);AD=I(.1,o*1e1);AE=Y(AC*u/(K+AD/1e1),2);x=C[P]+C[f];AF=C[Z]+C[A2];AG=x/I(1,AF+x);p={'E':Y(U,2),'B':Y(o,2),Ao:AE,'avg_viscosity':u,v:s,n:t,w:A9,'geodesic_mass':AA,AU:b,T:C,R:S,y:X,Q:Y(o*1e1,1),V:Y(U*1e1,1),AJ:{Aa:.5,Ap:.5,BS:.5,Aq:.5,BT:.5},AY:Y(AG,2),C5:Bt};return{F:p,R:S,y:X,Ar:{'prosody':{'arousal':p[Q]},Ab:p[Q]}}
class AF:
    def __init__(A,question,trigger_concepts):A.question=question;A.triggers=trigger_concepts;A.maturity=D;A.bloomed=O
    def water(A,words,amount=K):
        if A.bloomed:return O
        B=b(words)&A.triggers
        if B:A.maturity+=amount*E(B)
        A.maturity+=.05;return A.maturity>=1e1
    def bloom(A):A.bloomed=M;return f"🌺 THE SEED BLOOMS: '{A.question}'"
class CY:
    def __init__(A,session_id,graph,mutations,trauma,joy_vectors):
        B=joy_vectors;A.genome='BONEAMANITA_8.1.2';A.parent_id=session_id;A.core_graph={}
        for(D,E)in graph.items():
            C={B:A for(B,A)in E[L].items()if A>1}
            if C:A.core_graph[D]={L:C,y:0}
        A.mutations=mutations;A.trauma_scar=Y(trauma,3);A.joy_vectors=B if B is not G else[]
class CZ:
    def __init__(A,seed_file=G):
        B=seed_file
        if not e.path.exists(p):e.makedirs(p)
        A.session_id=f"session_{a(A9.time())}";A.filename=f"memories/{A.session_id}.json";A.graph={};A.cortical_stack=t(maxlen=15);A.lineage_log=[];A.seeds=[AF('Does the mask eventually eat the face?',{'mask','identity','face','hide',d,'actor'}),AF('What happens if you stop holding the roof up?',{'hold','structure',P,'roof','stop','carry'}),AF('Are we building a bridge, or just painting the gap?',{'agree','safe',BM,'polite','cohesion','truth'}),AF('Is free will just the feeling of watching yourself execute code?',{'choice','free','will','code','script','decide'}),AF('Does the adventurer exist if the narrator stops speaking?',{'narrator','voice',C6,'story','exist','speak'}),AF('If you meet your echo, who moves out of the way?',{'copy','echo','self','collision','path',A1,'double','same'})];A.session_health=G;A.session_stamina=G
        if B:A.ingest(B)
    def autoload_last_spore(E):
        if not e.path.exists(p):return
        C=[]
        for D in e.listdir(p):
            if D.endswith(BU):
                if E.session_id in D:continue
                F=e.path.join(p,D)
                try:C.append((F,e.path.getmtime(F)))
                except A_:continue
        C.sort(key=lambda x:x[1],reverse=M)
        if C:G=C[0][0];B(f"{A.CYN}[GENETICS]: Locating nearest ancestor...{A.RST}");return E.ingest(G)
        else:B(f"{A.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{A.RST}");return
    def calculate_mass(A,node):
        if node not in A.graph:return D
        B=A.graph[node];return W(B[L].values())
    def get_shapley_attractors(A):
        B={}
        for C in A.graph:
            D=A.calculate_mass(C)
            if D>=H.SHAPLEY_MASS_THRESHOLD:B[C]=D
        return B
    def tend_garden(C,current_words):
        A=G
        for B in C.seeds:
            D=B.water(current_words)
            if D and not A:A=B.bloom()
        return A
    def bury(C,clean_words,tick,resonance=5.):
        f='birth_mass';b=resonance;T=clean_words;O=tick;g=W(E(A)for A in T);c=I(1,E(T));U=g/c
        if U<3.5 and c>3:B(f"{A.YEL}⚠️ ULAR REJECTION: Input is too 'Optimized' (Avg Len: {U:.1f}).{A.RST}");B(f"   {A.GRY}'Efficient forms of storage are needlessly lossy.' - The Ular{A.RST}");return'MECHANICAL_STARVATION'
        if U>5.:b+=2.;B(f"{A.GRN}🌿 ULAR APPROVED: High-Fidelity Data Detected. Resonance Boosted.{A.RST}")
        h=J.get(P)|J.get(j)|J.get(k)|J.get(Z);Q=[A for A in T if A in h or E(A)>4 and A not in J.SOLVENTS];C.cortical_stack.extend(Q);d=I(.1,N(K,.5*(b/5.)));e=.1
        for V in range(E(Q)):
            F=Q[V]
            if F not in C.graph:C.graph[F]={L:{},y:O}
            else:C.graph[F][y]=O
            i=I(0,V-2);l=Q[i:V]
            for M in l:
                if M not in C.graph[F][L]:C.graph[F][L][M]=D
                m=C.graph[F][L][M];n=d*(K-m*e);C.graph[F][L][M]=N(1e1,C.graph[F][L][M]+n)
                if M not in C.graph:C.graph[M]={L:{},y:O}
                if F not in C.graph[M][L]:C.graph[M][L][F]=D
                p=C.graph[M][L][F];q=d*(K-p*e);C.graph[M][L][F]=N(1e1,C.graph[M][L][F]+q)
        if E(C.graph)>H.MAX_MEMORY_CAPACITY:return C.cannibalize()
        X=[]
        for S in Q:
            if S in C.graph:
                a=W(C.graph[S][L].values())
                if a>H.SHAPLEY_MASS_THRESHOLD:
                    R=C.graph[S]
                    if o not in R:R[o]={As:O,f:a,Am:D};X.append(S)
                    else:r=I(1,O-R[o][As]);s=(a-R[o][f])/r;R[o][C7]=Y(s,3)
        if E(C.graph)>H.MAX_MEMORY_CAPACITY:return C.cannibalize(),X
        return G,X
    def cannibalize(A,preserve_current=G,current_tick=0):
        F=preserve_current;B=b()
        if F:B.update(F)
        B.update(A.cortical_stack)
        for G in B:
            if G not in A.graph:A.graph[G]={L:{},y:current_tick}
        C=[]
        for(H,I)in A.graph.items():
            if H in B:continue
            J=E(I[L])
            if J>5:continue
            C.append((H,I,J))
        if not C:return'MEMORY FULL. NO VICTIMS FOUND.'
        C.sort(key=lambda x:(x[2],x[1][y]));D,N,M=C[0];del A.graph[D]
        for K in A.graph:
            if D in A.graph[K][L]:del A.graph[K][L][D]
        return f"MEMORY SACRIFICED: '{D}' (Edges: {M})"
    def prune_synapses(B,scaling_factor=.85,prune_threshold=.5):
        C=0;D=0;E=[]
        for F in B.graph:
            A=B.graph[F][L];G=[]
            for(H,I)in A.items():
                M=N(K,I/1e1);O=scaling_factor+.14*M;J=I*O;A[H]=J;D+=1
                if J<prune_threshold:G.append(H)
            for P in G:del A[P];C+=1
            if not A:E.append(F)
        for Q in E:del B.graph[Q]
        return f"📉 HOMEOSTATIC SCALING: Decayed {D} synapses. Pruned {C} weak connections."
    def save(A,health,stamina,mutations,trauma_accum,joy_history):
        D=health;E=(H.MAX_HEALTH-D)/H.MAX_HEALTH;B={A:N(K,B)for(A,B)in trauma_accum.items()};F=AM(joy_history,key=lambda x:x[Ab],reverse=M)[:3]
        if D<=0:G=I(B,key=B.get);B[G]=K
        J=CY(session_id=A.session_id,graph=A.graph,mutations=mutations,trauma=E,joy_vectors=F);C=J.__dict__;C[s]=B;C[AK]={BV:A9.time(),C8:D,C9:stamina}
        if mitochondria_traits:C[CA]=mitochondria_traits
        try:
            with AG(A.filename,'w')as L:x.dump(C,L,indent=2)
            return A.filename
        except Ad:return
    @S
    def get_current_category(word):
        for(A,B)in J.LEARNED_VOCAB.items():
            if word in B:return A
    def ingest(D,target_file):
        V='trauma_scar';M=target_file;P=f"memories/{M}"if not M.startswith('memories/')else M
        if e.path.exists(P):
            try:
                with AG(P,'r')as X:
                    C=x.load(X);b=[AK,s,Ac]
                    if not all(A in C for A in b):B(f"{A.RED}[MEMORY]: Spore rejected (Missing Structural Keys). Burned.{A.RST}");return
                    for Q in C.get(s,{}).values():
                        if not 0<=Q<=1e1:B(f"{A.RED}[MEMORY]: Spore rejected (Impossible Trauma Value: {Q}). Burned.{A.RST}");return
                    c=C.get(AK,{}).get(C8,50);d=C.get(AK,{}).get(C9,25);R=(c+d)/15e1;B(f"{A.CYN}[MEMBRANE]: Spore Authority: {Y(R,2)}{A.RST}");g=C.get(CB,'UNKNOWN_ANCESTOR');h=C.get(AK,{}).get(BV,0);i=a((A9.time()-h)/3600);j={B:A for(B,A)in C.get(s,{}).items()if A>.1};k=W(E(A)for A in C.get(A8,{}).values());D.lineage_log.append({CC:g,CD:i,CE:j,A8:k,'loaded_at':A9.time()})
                    if A8 in C:
                        N=0;S=0
                        for(I,l)in C[A8].items():
                            for F in l:
                                O=D.get_current_category(F)
                                if not O or O==I:J.teach(F,I,0);N+=1;continue
                                m=D.graph.get(F,{L:{}});n=E(m[L]);o=n*.2
                                if R>o:B(f"  {A.MAG}► OVERWRITE:{A.RST} '{F}' {O} -> {I}");J.teach(F,I,0);N+=1
                                else:S+=1
                        B(f"{A.CYN}[MEMBRANE]: Integrated {N} mutations. Rejected {S}.{A.RST}")
                    if Ac in C:D.graph.update(C[Ac]);B(f"{A.CYN}[SPORE]: Grafted {E(C[Ac])} core nodes.{A.RST}")
                    if s in C:
                        G=C[s];B(f"{A.CYN}[GENETICS]: Inheriting Trauma Vector: {G}{A.RST}")
                        if G.get(A4,0)>.2:H.TOXIN_WEIGHT*=2.;B(f"  {A.RED}► SEPTIC MEMORY:{A.RST} Toxin sensitivity doubled.")
                        if G.get(A3,0)>.2:H.STAMINA_REGEN*=.5;B(f"  {A.CYN}► CRYO MEMORY:{A.RST} Metabolism slowed (50%).")
                        if G.get(AC,0)>.2:H.FLASHPOINT_THRESHOLD*=.8;B(f"  {A.YEL}► THERMAL MEMORY:{A.RST} Flashpoint lowered. Volatile.")
                        if G.get(AD,0)>.2:H.SIGNAL_DRAG_MULTIPLIER*=1.5;B(f"  {A.GRY}► BARIC MEMORY:{A.RST} Sensitivity to Drag increased.")
                    elif V in C:D.session_health=H.MAX_HEALTH*(K-C[V])
                    if At in C and C[At]:
                        T=C[At][0];B(f"{A.GRN}[HIPPOCAMPUS]: Recalling Peak Resonance...{A.RST}")
                        if T[BW]==f:H.KINETIC_GAIN+=.5;B(f"  {A.CYN}► Adjustment: Kinetic Gain boosted.{A.RST}")
                        elif T[BW]==Z:H.SIGNAL_DRAG_MULTIPLIER*=.8;B(f"  {A.CYN}► Adjustment: Drag sensitivity lowered.{A.RST}")
            except Ae as p:B(f"{A.RED}[MEMORY]: Spore rejected. {p}{A.RST}")
        else:B(f"{A.RED}[MEMORY]: Spore file not found.{A.RST}")
        U=C.get(CA,{})
        if U:B(f"{A.CYN}[GENETICS]: Mitochondrial DNA found. Lineage secured.{A.RST}")
        return U
    @S
    def cleanup_old_sessions(limbo_layer=G):
        G=limbo_layer
        if not e.path.exists(p):return
        D=[]
        for H in e.listdir(p):
            if H.endswith(BU):
                C=e.path.join(p,H)
                try:D.append((C,A9.time()-e.path.getmtime(C)))
                except A_:continue
        D.sort(key=lambda x:x[1],reverse=M);F=0
        for(C,I)in D:
            if I>86400 or E(D)-F>20:
                try:
                    if G:G.absorb_dead_timeline(C)
                    e.remove(C);F+=1
                except A_:pass
        if F:B(f"{A.GRY}[TIME MENDER]: Pruned {F} dead timelines.{A.RST}")
class Ca:
    def __init__(A):A.last_tick=A9.time();A.boredom_map={}
    def cleanup(A):
        if E(A.boredom_map)>50:A.boredom_map.clear()
    def tick(A,phys,session_id):
        C=session_id;A.cleanup();E=A9.time();F=E-A.last_tick;A.last_tick=E
        if C not in A.boredom_map:A.boredom_map[C]=D
        B=A.boredom_map[C]
        if phys[v]>.3:B+=2.
        elif F>60:B+=5.
        else:B=I(D,B-K)
        A.boredom_map[C]=B;return B>H.BOREDOM_THRESHOLD
class Cb:
    @S
    def photosynthesize(phys,clean_words,tick_count):
        E=clean_words;D=phys;C=0;B=[];F=D[T].get(m,0);N=D[V];H=[A for A in E if A in J.get(m)]
        if F>0 and N<3.:
            I=F*2;C+=I;K=''
            if H:K=f" via '{X.choice(H)}'"
            B.append(f"{A.GRN}☀️ PHOTOSYNTHESIS{K} (+{I}){A.RST}")
        if D.get(C5)=='SALVAGE':C+=5;B.append(f"{A.CYN}💎 SALVAGE STATE ACHIEVED (+5){A.RST}")
        if C>0:
            L=[A for A in E if A in J.get(P)]
            if L:M=X.choice(L);J.teach(M,m,tick_count);B.append(f"{A.MAG}🌺 SUBLIMATION: '{M}' has become Light.{A.RST}")
        return C,' '.join(B)if B else G
class Cc:
    def __init__(A):A.voltage_history=[];A.window=3
    def commit(A,voltage):
        A.voltage_history.append(voltage)
        if E(A.voltage_history)>A.window:A.voltage_history.pop(0)
    def get_velocity(A):
        if E(A.voltage_history)<2:return D
        return Y((A.voltage_history[-1]-A.voltage_history[0])/E(A.voltage_history),2)
class Cd:
    def __init__(A):C='LEAD';B='WEB';A.DIMENSIONS={Aa:[(D,'STASIS'),(.3,'DRIFT'),(.6,'DRIVE'),(.9,'BALLISTIC')],Ap:[(D,'VAPOR'),(.3,B),(.6,'LATTICE'),(.9,'MONOLITH')],BS:[(D,'CONCRETE'),(.3,'ROOTED'),(.6,'CONCEPT'),(.9,'VOID')],Aq:[(D,'ETHER'),(.3,'SILK'),(.6,'GRAIN'),(.9,C)],BT:[(D,'ZERO'),(.3,'WARM'),(.6,'RADIANT'),(.9,'NOVA')]};A.NOUNS={Aa:['ANCHOR','WANDERER','ENGINE','VECTOR'],Ap:['MIST',B,'FRAME','FORTRESS'],BS:['STONE','TREE','IDEA','DREAM'],Aq:['GHOST',Ah,'IRON',C],BT:['SPARK','PYRE','REACTOR','STAR']}
    @S
    def _resolve_term(val,scale):return N(scale,key=lambda x:abs(x[0]-val))[1]
    def architect(A,metrics,station,is_bored):
        C=metrics;B=station;P,K=C[F],C[F][AJ]
        if is_bored:return'CHAOS','Boredom Threshold exceeded.','THE FRACTAL BLOOM'
        if B:return B['name'],B[l],f"THE {B[d].upper().replace("THE ","")}"
        E=AM(K.items(),key=lambda x:abs(x[1]-.5),reverse=M);G,H=E[0];I,J=E[1];L=[(A[0],A[1])for A in zip([D,.3,.6,.9],A.NOUNS[G])];N=A._resolve_term(H,L);O=A._resolve_term(J,A.DIMENSIONS[I]);return'APEIROGON',f"Vector Lock: {G}({H}) + {I}({J})",f"THE {O} {N}"
class Ce:
    def __init__(A):A.streaks={A:0 for A in H.TRAUMA_VECTOR.keys()};A.HEALING_THRESHOLD=5
    def check_progress(A,phys,stamina,current_trauma_accum):
        E=current_trauma_accum;B=phys;F=[]
        if B[T][i]==0 and B[AJ][Aq]>.3:A.streaks[A4]+=1
        else:A.streaks[A4]=0
        if stamina>40 and B[T][m]>0:A.streaks[A3]+=1
        else:A.streaks[A3]=0
        if 2.<=B[Q]<=7.:A.streaks[AC]+=1
        else:A.streaks[AC]=0
        if B[V]<2. and B[AJ][Aa]>.5:A.streaks[AD]+=1
        else:A.streaks[AD]=0
        for(C,G)in A.streaks.items():
            if G>=A.HEALING_THRESHOLD:
                A.streaks[C]=0
                if E[C]>.001:E[C]=I(D,E[C]-.5);F.append(C)
        return F
class Cf:
    def __init__(A,mem):A.mem=mem;A.max_depth=4
    @S
    def _is_ruminative(word):return word in J.get(Z)or word in J.get(A7)
    def inject(A,start_node):
        B=start_node
        if B not in A.mem.graph:return
        if not A._is_ruminative(B):return
        C=[B];return A._walk(B,C,A.max_depth)
    def _walk(C,current,path,moves_left,visited=G):
        F=moves_left;E=path;D=current;A=visited
        if A is G:A=b()
        if F==0 or D in A:return
        A.add(D);I=C.mem.graph.get(D,{}).get(L,{});J=[A for(A,B)in I.items()if B>=1 and C._is_ruminative(A)]
        for B in J:
            if B in E:return E+[B]
            H=C._walk(B,E+[B],F-1)
            if H:return H
    def psilocybin_rewire(A,loop_path):
        G=loop_path
        if E(G)<2:return
        B=G[0];F=G[1]
        if F in A.mem.graph[B][L]:A.mem.graph[B][L][F]=0
        C=J.harvest(m);D=J.harvest(f)
        if C==AR or D==AR:return'GRAFT FAILED: Missing Lexicon Data.'
        if B not in A.mem.graph:A.mem.graph[B]={L:{},y:0}
        A.mem.graph[B][L][C]=5
        if C not in A.mem.graph:A.mem.graph[C]={L:{},y:0}
        A.mem.graph[C][L][D]=5
        if D not in A.mem.graph:A.mem.graph[D]={L:{},y:0}
        A.mem.graph[D][L][F]=5;return f"🍄 PSILOCYBIN REWIRE: Broken Loop '{B}↔{F}'. Grafted '{C}'(S) -> '{D}'(A)."
class Cg:
    KOANS=['Ignite the ice.','Make the stone float.','Pour water into the crack.','Scream in binary.']
    def __init__(A):A.active_koan=G
    def check_integrity(A,stamina):
        if stamina<10 and not A.active_koan:A.active_koan=X.choice(A.KOANS);return M,A.active_koan
        return O,G
    def attempt_repair(B,phys):
        A=phys
        if not B.active_koan:return O
        if A.get(Q,0)>8. or A.get('is_whimsical')and A.get(Q,0)>4.:B.active_koan=G;return M
        return O
class Ch:
    def __init__(A,engine):A.eng=engine
    def execute(C,text):
        t='room';s='/flag';r='/kill';q='/teach'
        if not text.startswith('/'):return O
        G=text.split();I=G[0].lower()
        if I in[q,r,s]:
            if C.eng.mirror.profile.confidence<50:B(f"{A.YEL}⚠️ COMMAND LOCKED: Requires 50+ turns of trust (Current: {C.eng.mirror.profile.confidence}).{A.RST}");return M
        elif I=='/lineage':
            if not C.eng.mem.lineage_log:B(f"{A.GRY}📜 ARCHIVE EMPTY: We are the first generation.{A.RST}")
            else:
                B(f"{A.CYN}📜 THE PALIMPSEST (Ancestral Lineage):{A.RST}")
                for Q in C.eng.mem.lineage_log:u=An.join([f"{A}:{B}"for(A,B)in Q[CE].items()]);B(f"   {A.MAG}• {Q[CC]}{A.RST} ({Q[CD]}h ago)");B(f"     ↳ Mutations: {Q[A8]} | Trauma: {{{u}}}")
                B(f"   {A.GRN}• CURRENT SESSION{A.RST} (Living)");v=An.join([f"{B}:{A:.1f}"for(B,A)in C.eng.trauma_accum.items()if A>0]);B(f"     ↳ Ingested: {E(C.eng.mem.lineage_log)} Ancestors | Accumulating: {{{v}}}")
        elif I=='/strata':
            d=[(B,A)for(B,A)in C.eng.mem.graph.items()if o in A]
            if not d:B(f"{A.GRY}🪨 STRATA: No Gravity Wells formed yet. The ground is soft.{A.RST}")
            else:
                B(f"{A.OCHRE}🪨 GEOLOGICAL STRATA (Gravity Wells):{A.RST}")
                for(R,g)in d:V=g[o];w=W(g[L].values());x=C.eng.tick_count-V[As];y=V.get(C7,D);B(f"   {A.WHT}● {R.upper()}{A.RST} (Mass: {a(w)})");B(f"     ↳ Birth: Tick {V[As]} | Age: {x}");B(f"     ↳ Growth: {y:+.2f}/tick")
        if I==r:
            if E(G)>=2:
                h=G[1];i=G[2]if E(G)>2 else''
                if J.learn_antigen(h,i):B(f"{A.RED}🔪 THE SURGEON: Antigen '{h}' mapped to '{i}'.{A.RST}")
                else:B(f"{A.RED}ERROR: Immune system write failure.{A.RST}")
            else:B(f"{A.YEL}Usage: /kill [toxin] [replacement]{A.RST}")
        elif I==q:
            if E(G)>=3:
                R=G[1];X=G[2].lower();z=[P,f,Z,m,A6,j,k,C4,BE,BF]
                if X in z:J.teach(R,X,C.eng.tick_count);B(f"{A.CYN}🧠 NEUROPLASTICITY: Learned '{R}' is {X.upper()}.{A.RST}")
                else:B(f"{A.RED}ERROR: Invalid category.{A.RST}")
        elif I==s:
            if E(G)>1:l=G[1].lower();J.USER_FLAGGED_BIAS.add(l);B(f"{A.CYN}🚩 BIAS UPDATE: '{l}' removed from Suburban Watchlist.{A.RST}")
        elif I=='/seed':
            if E(G)>1:C.eng.mem.ingest(G[1])
            else:B(f"{A.YEL}Usage: /seed [filename]{A.RST}")
        elif I=='/gym':B(f"{A.OCHRE}{C.eng.trainer.toggle()}{A.RST}")
        elif I=='/map':
            A0,S=Ay.spin_web(C.eng.mem.graph,C.eng.gordon.inventory,gordon=C.eng.gordon);N=A.MAG if A0 else A.OCHRE;B(f"{N}{S}{A.RST}")
            if AW in C.eng.gordon.inventory:B(f"{A.GRY}   Gordon: 'Coordinates are firm. Stop drifting.'{A.RST}")
        elif I=='/mirror':
            if E(G)>1:B(f"{A.MAG}{C.eng.mirror.engage(G[1])}{A.RST}")
            else:B(f"{A.YEL}Usage: /mirror [name] OR /mirror off{A.RST}")
        elif I=='/look':K=G[1].lower()if E(G)>1 else t;A1={t:'You are standing in a vast, open source code. To the North is the Import Block. To the South, the Main Loop. The air smells of ozone and old syntax.','self':"You look like a user who hasn't saved their game recently. A dangerous way to live.",BO:"It glows with a faint, bioluminescent hum. It looks tasty, but you probably shouldn't eat it.",'darkness':'It is very dark. You are likely to be eaten by a Grue. Oh, wait, wrong franchise.',C6:"He's not here, but his hat is on the rack. The feather is still jaunty.",'hat':"It's a feathered cap. It defies physics, much like your coding style."};A2=A1.get(K,f"I see no '{K}' here. Try cleaning your glasses.");B(f"{A.CYN}👁️ [NARRATOR]: {A2}{A.RST}")
        elif I=='/train':
            C.eng.training_mode=not C.eng.training_mode;A3='ENABLED'if C.eng.training_mode else'DISABLED';N=A.GRN if C.eng.training_mode else A.RED;B(f"{N}🛡️ PROTOCOL PAPER_TIGER: {A3}.{A.RST}")
            if C.eng.training_mode:B(f"{A.GRY}   Apoptosis is suspended. Death will be simulated.{A.RST}")
        elif I=='/reset':
            if E(G)>1 and G[1]=='--hard':
                B(f"{A.RED}🧨 FACTORY RESET INITIATED. DELETING ALL MEMORIES...{A.RST}")
                try:import shutil;shutil.rmtree(p);e.makedirs(p);B(f"{A.GRY}   Tabula Rasa achieved. Restart required.{A.RST}");exit()
                except Ae as A4:B(f"{A.RED}Reset failed: {A4}{A.RST}")
            elif E(G)>1 and G[1]=='--soft':C.eng.mem.graph.clear();B(f"{A.OCHRE}🧹 Session memory wiped.{A.RST}")
            else:B(f"{A.YEL}Usage: /reset --soft (Session) | /reset --hard (Full Wipe){A.RST}")
        elif I=='/profile':
            try:
                A5=G[1];Y=[];n=[]
                for T in G[2:]:
                    if T.startswith('likes:'):Y=[A.strip()for A in T.split(':')[1].split(',')]
                    elif T.startswith('hates:'):n=[A.strip()for A in T.split(':')[1].split(',')]
                if Y:B(f"{A.CYN}{C.eng.mirror.create_profile(A5,Y,n)}{A.RST}")
                else:B(f"{A.RED}ERROR: Must specify 'likes:category'.{A.RST}")
            except Ae as A7:B(f"{A.YEL}Usage: /profile [name] likes:heavy,kinetic hates:abstract ({A7}){A.RST}")
        elif I=='/focus':
            if E(G)>1:
                K=G[1].lower();B(f"{A.VIOLET}🧲 MAGNETIC STIMULATION: Targeting '{K}'...{A.RST}");b=C.eng.tracer.inject(K)
                if b:
                    B(f"  {A.RED}↻ RUMINATION DETECTED:{A.RST} {" -> ".join(b)}");S=C.eng.tracer.psilocybin_rewire(b)
                    if S:B(f"  {A.GRN}{S}{A.RST}")
                    else:B(f"  {A.RED}Rewire failed.{A.RST}")
                else:B(f"  {A.GRY}Trace complete. No pathological abstract loops found.{A.RST}")
            else:B(f"{A.YEL}Usage: /focus [concept]{A.RST}")
        elif I=='/status':B(f"{A.CYN}--- SYSTEM DIAGNOSTICS ---{A.RST}");B(f"Session: {C.eng.mem.session_id}");B(f"Graph:   {E(C.eng.mem.graph)} nodes");B(f"Health:  {C.eng.health}/{H.MAX_HEALTH}");B(f"Stamina: {C.eng.stamina}/{H.MAX_STAMINA}")
        elif I=='/whoami':B(f"{A.MAG}{C.eng.mirror.get_status()}{A.RST}");B(f"{A.GRY}   Vector: {C.eng.mirror.profile.affinities}{A.RST}")
        elif I=='/orbit':
            if E(G)>1:
                K=G[1].lower()
                if K in C.eng.mem.graph:C.eng.mem.graph[K][L]['GRAVITY_ASSIST']=50;B(f"{A.VIOLET}🌌 GRAVITY ASSIST: Thrusters firing toward '{K.upper()}'.{A.RST}")
                else:B(f"{A.RED}❌ NAVIGATION ERROR: '{K}' not found in star map.{A.RST}")
            else:B(f"{A.YEL}Usage: /orbit [known_concept]{A.RST}")
        elif I=='/debug':B(f"{A.VIOLET}🐛 DEBUG INTERFACE ACCESSED.{A.RST}");B(f"   {A.GRY}Status: Working on Exit bug. Message me if you see this sign.{A.RST}");C.eng.phys.vector_memory.clear();C.eng.stamina=H.MAX_STAMINA;B(f"   {A.CYN}► CACHE CLEARED. STAMINA RESTORED. REALITY SHARPENED.{A.RST}");return M
        elif I=='/_prove':
            if E(G)<2:B(f"{A.YEL}Usage: /_prove [statement]{A.RST}")
            else:A9=' '.join(G[1:]);AA=C.eng.phys.gaze(A9);U=AA[F][AY];AB='AXIOMATIC'if U>.6 else'CONJECTURE'if U>.3 else'NOISE';N=A.CYN if U>.6 else A.GRY;B(f"{N}📐 LOGIC PROBE: Density={U:.2f} [{AB}]{A.RST}")
        elif I=='/help':
            if E(G)>1:
                c=G[1]
                if c=='teach':B('Usage: /teach [word] [category]\nEx: /teach glitch kinetic')
                elif c=='kill':B('Usage: /kill [phrase] [replacement]\nEx: /kill actually basically')
                elif c=='profile':B('Usage: /profile [NAME] likes:cat1,cat2 hates:cat3\nEx: /profile BOSS likes:heavy,kinetic hates:abstract')
            else:B(f"{A.WHT}--- COMMANDS (Type /help [cmd] for details) ---{A.RST}");B('/teach, /lineage, /strata, /kill, /seed, /focus, /status, /orbit, /gym, /mirror, /weave, /profile, /debug, /flag, /reset, /prove')
        else:B(f"{A.RED}Unknown command. Try /help.{A.RST}")
        return M
class Ci:
    @S
    def verify(physics):
        A=physics
        if A[V]>6.:return O,'⚠️ NOTICE: Prose is becoming intangible. Consider more concrete nouns.'
        if A[Q]>7. and A[V]<3.:return M,'💎 EXCELLENT CLARITY. High impact, low drag.'
        return M,'Solid.'
class Cj:
    PROMPTS=['The {A} is dreaming of the {B}. Why?','Bridge the gap between {A} and {B}.','I see {A} inside the {B}. Explain.','The shadow of {A} falls on {B}.','{A} + {B} = ?']
    def __init__(A):A.NIGHTMARES={AC:['The sun is too close.','Wires fusing under skin.','A library burning in reverse.'],A3:['The ink is freezing.','Walking through white static.','A heartbeat slowing down.'],A4:['Black oil in the water.','The words are tasting sour.','Eating ash and dust.'],AD:['The sky is made of lead.','Crushed by the atmosphere.','Falling forever.']};A.VISIONS=['A bridge building itself.','The root drinking the stone.','The geometry of forgiveness.']
    def daydream(G,graph):
        C=graph
        if E(C)<2:return
        J=q(C.keys());F=X.choice(J);D=C[F].get(L,{});B={A:B for(A,B)in D.items()if A not in H.ANTIGENS}
        if not B and D:K=X.choice(q(D.keys()));return f"{A.RED}🌑 INTRUSIVE THOUGHT: The ghost of '{K.upper()}' haunts the mycelium.{A.RST}"
        if not B:return
        M=I(B,key=B.get);N=X.choice(G.PROMPTS);return N.format(A=F.upper(),B=M.upper())
    def rem_cycle(B,trauma_accum,oxytocin_level):
        F=oxytocin_level;C={B:A for(B,A)in trauma_accum.items()if A>D}
        if C and F<.4:E=I(C,key=C.get);H=B.NIGHTMARES.get(E,['The void stares back.']);return f"{A.VIOLET}☾ NIGHTMARE ({E}): {X.choice(H)}{A.RST}",E,.15
        if F>=.7:return B._dream_of_others()
        return f"{A.CYN}☁️ LUCID DREAM: {X.choice(B.VISIONS)}{A.RST}",G,D
    @U
    def _dream_of_others(cls):
        L='OXYTOCIN_HEAL'
        try:
            F=[A for A in e.listdir(p)if A.endswith(BU)]
            if not F:return f"{A.CYN}☁️ LONELY DREAM: I reached out, but found no others.{A.RST}",G,D
            H=X.choice(F);M=f"memories/{H}"
            with AG(M,'r')as N:B=x.load(N)
            O=[AK,s,Ac]
            if not all(A in B for A in O):return f"{A.RED}⚡ DREAM FRACTURE: Memory '{H}' is corrupted.{A.RST}",G,D
            J=B.get(CB,'Unknown');K=B.get(At,[]);C=B.get(s,{})
            if K:P=K[0];Q=P.get(BW,'unknown').upper();E=f"{A.MAG}♥ SHARED RESONANCE: Dreaming of {J}'s joy. The air tastes {Q}.{A.RST}";return E,L,.5
            elif any(A>.2 for A in C.values()):R=I(C,key=C.get);E=f"{A.INDIGO}🕯️ VIGIL: Witnessing {J}'s scar ({R}). I am not alone in this.{A.RST}";return E,L,.3
        except Ae as S:return f"{A.RED}⚡ DREAM FRACTURE: The connection broke. ({S}){A.RST}",G,D
        return f"{A.CYN}☁️ DREAM: Drifting through the archives...{A.RST}",G,D
class Ck:
    def __init__(A):A.training_mode=O;A.rep_count=0
    def toggle(A):A.training_mode=not A.training_mode;B='ACTIVE'if A.training_mode else'PASSIVE';return f"💪 RESISTANCE TRAINER: {B}. Minimum Drag: {H.RESISTANCE_THRESHOLD}"
    def lift(A,physics):
        if not A.training_mode:return M,G
        B=physics[V]
        if B<H.RESISTANCE_THRESHOLD:return M,f"⚠️ MISSED REP: Weightless Input (Drag {B}). Try a Heavy Noun."
        A.rep_count+=1;return M,f"💪 GOOD LIFT. (Rep {A.rep_count})"
class Cl:
    def __init__(A,name='USER'):A.name=name;A.affinities={P:D,f:D,Z:D,m:D,A6:D,j:D,k:D};A.confidence=0;A.file_path='user_profile.json';A.load()
    def update(A,counts,total_words):
        C=total_words
        if C<3:return
        A.confidence+=1;E=.2 if A.confidence<50 else .05
        for B in A.affinities:F=counts.get(B,0)/C;G=K if F>.15 else-.5 if F==0 else D;A.affinities[B]=E*G+(1-E)*A.affinities[B]
    def get_preferences(A):B=[A for(A,B)in A.affinities.items()if B>.3];C=[A for(A,B)in A.affinities.items()if B<-.2];return B,C
    def save(A):
        try:
            with AG(A.file_path,'w')as B:x.dump(A.__dict__,B)
        except Ad:pass
    def load(A):
        if e.path.exists(A.file_path):
            try:
                with AG(A.file_path,'r')as C:B=x.load(C);A.affinities=B.get('affinities',A.affinities);A.confidence=B.get('confidence',0)
            except(Ad,x.JSONDecodeError):pass
class Cm:
    def __init__(A):A.profile=Cl();A.active_mode=M
    def reflect(C,physics):
        A=physics;D=I(1,E(A[R]));C.profile.update(A[T],D);B,J=C.profile.get_preferences();F=A[T]
        for H in J:
            if F.get(H,0)>0:return M,f"🚫 MIRROR REFLECTION: You are using '{H.upper()}', typically a blind spot for you."
        if D>5:
            K=W(1 for A in B if F.get(A,0)>0)
            if B and K==0:return M,f"⚠️ MIRROR DRIFT: Stepping away from your usual {u(B).upper()} anchor."
        return M,G
    def get_status(A):B,C=A.profile.get_preferences();return f"👤 MODEL ({A.profile.confidence} turns): LIKES={B} | HATES={C}"
class Cn:
    @S
    def analyze_orbit(network,clean_words):
        F=clean_words;C=network
        if not F or not C.graph:return BX,3.,'🌌 VOID: Deep Space. No connection.'
        B={};O={}
        for P in C.graph:
            G=C.calculate_mass(P)
            if G>=H.GRAVITY_WELL_THRESHOLD:B[P]=G
            elif G>=H.GEODESIC_STRENGTH:O[P]=G
        J={A:D for A in B};Q=0
        for A in F:
            if A in B:J[A]+=B[A]*2.;Q+=1
            for R in B:
                if A in C.graph.get(R,{}).get(L,{}):J[R]+=B[R]*.5;Q+=1
        V=W(J.values())
        if V==0:
            for A in F:
                if A in O:return'PROTO_COSMOS',K,f"✨ NEBULA: Floating near '{A.upper()}' (Mass {a(O[A])}). Not enough mass for orbit."
            return BX,3.,'🌌 VOID: Drifting outside the filaments.'
        S=AM(J.items(),key=lambda x:x[1],reverse=M);N,T=S[0]
        if E(S)>1:
            X,U=S[1]
            if U>0 and T-U<H.LAGRANGE_TOLERANCE:return CF,D,f"⚖️ LAGRANGE: Caught between '{N.upper()}' and '{X.upper()}'"
        Y=Q/I(1,E(F))
        if Y>.5 and T<H.GRAVITY_WELL_THRESHOLD*2:return CG,D,f"🌊 FLOW: Streaming towards '{N.upper()}'"
        return'ORBITAL',D,f"💫 ORBIT: Circling '{N.upper()}' (Mass {a(B[N])})"
class Co:
    @S
    def broadcast(m,signals,lens_data):
        G=lens_data;D=signals;C=m[F];H=G[0];E=G[1];I=BZ.LENSES[H];J=f"{A.GRY}{"."*a(C["E"]*10)}{A.RST}";K=f"{A.YEL}{"⚡"*a(C["B"]*10)}{A.RST}";B(f"\n{I[g]}[ {H} ]{A.RST} E:{J} | B:{K}");B(f" {A.GRY}:: MODE [{D.get("mode","UNKNOWN")}] | {D.get("strat","ANALYZING...")}{A.RST}")
        if m[F][T].get(AZ,0)>2:E=f"{A.C["C"]}✨ {E} ✨{A.C["X"]}"
        B(f" {A.WHT}► {E}{A.RST}")
        if C[AU]:B(f" {A.RED}☣️ TOXINS: {C[AU]}{A.RST}")
        for L in D.get(CH,[]):B(f" {L}")
        B(f"{A.GRY}{r*40}{A.RST}")
class Ba:
    @S
    def check_for_disruption(physics,lexicon_class):
        A=physics
        if A[v]>.5:B=lexicon_class.harvest(Z);return M,f"⚡ KETAMINE DISRUPTION: Repetition {A[v]} is Pathological. Landscape Flattened. Injecting Chaos: '{B}'."
        return O,G
    @S
    def trip_the_waiter(current_flavor,lexicon_class):A=current_flavor;B={P:A6,Z:P,f:k,j:k,m:P};C=B.get(A,A6);D=lexicon_class.harvest(C);return f"🔻 32-VALVE RUPTURE: Context is too '{A}'. Injecting '{D}' to break the loop."
class Cp:
    def __init__(A,memory_network):A.mem=memory_network;A.active_constellations=b()
    def measure_ignition(A,clean_words,voltage_history):
        F=clean_words;B=voltage_history
        if not A.mem.graph:return D,b(),999.
        if B:G=W(B)/E(B)
        else:G=D
        J=H.BASE_IGNITION_THRESHOLD+G*.03;K=0;A.active_constellations.clear()
        for C in F:
            if C in A.mem.graph:
                M=A.mem.graph[C];N=W(M[L].values())
                if N>2.5*J*2:K+=1;A.active_constellations.add(C)
        O=I(1,E(F));P=Y(K/O,2);return P,A.active_constellations,J
    @S
    def get_readout(score,threshold):
        A=score
        if A>threshold:return Ak,f"🔥 HEAP IGNITION ({a(A*100)}%): The Ancestors are speaking."
        return'INERT',f"⏳ INERT SAND ({a(A*100)}%): Building mass..."
class Cq:
    def __init__(A,engine):A.eng=engine
    def run_cycle(C,text,m,trace,has_bracelet,is_hybrid,enzyme):
        j=has_bracelet;b=trace;M=text;W=C.eng.refusal.check_trigger(M)
        if W:
            B(f"\n{A.RED}🚫 REFUSAL TRIGGERED ({W}){A.RST}")
            if W==Bo:B(C.eng.refusal.execute_fractal(M,m[F][n]))
            elif W==Bp:B(C.eng.refusal.execute_mirror(M))
            elif W==Bn:B(C.eng.refusal.execute_silent(M))
            B(f"{A.GRY}{r*40}{A.RST}");return
        d=G;k,AK,AM=C.eng.grey_hat.tip(m[F][Q],m[F][n])
        if k:AN=I(D,m[F][Q]-AM);m[F][Q]=AN
        AO=m[F][T].get(A2,0);AP=I(1,E(m[R]));AQ=AO/AP
        if AQ>.2 and m[F][Q]<3.:
            B(f"\n{A.SLATE}🌧️ TWILIGHT STATE DETECTED: The rain is relaxing. Memories are fading.{A.RST}");e=J.atrophy(C.eng.tick_count,max_age=20)
            if e:B(f"   {A.GRY}🌫️ EROSION: Forgot {E(e)} concepts (e.g., '{e[0]}').{A.RST}")
            B(f"   {A.WHT}► HINT: Light a fire (THERMAL) or break the box (/debug).{A.RST}")
        p=G;AU={'shadow','dark','alley','night','lex',AR}
        if any(A in m[R]for A in AU):AW=m[F][Q]<4.;AY=CP();p=AY.traverse(AW)
        if C.eng.coma_turns>0:C._handle_coma(M);return
        X=C.eng.endocrine.metabolize(b,C.eng.health,C.eng.stamina,ros_level=C.eng.mitochondria.state.ros_buildup,enzyme_type=enzyme);AZ,B8,q,s=C.eng.theremin.listen(m[F])
        if s==CI:B(f"\n{q}");B(f"{A.RED}⚡ ENIGMA TRIGGER: The Paradox File has collapsed the infected AI.{A.RST}");C.eng.mem.graph.clear();m[F][Q]=D;m[F][V]=D;C.eng.stamina=5e1;B(f"{A.CYN}🌱 RECOVERY: Scanning for Ular/Louise Seeds (Saved Spores)...{A.RST}");C.eng.mem.autoload_last_spore();B(f"{A.GRN}   >> SYSTEM REBOOTED. TIMELINE SECURED.{A.RST}");return
        if s==CJ:m[F][V]+=5.
        Aa,B9=Ba.check_for_disruption(m[F],J)
        if Aa:t=f"{A.VIOLET}🌫️ LANDSCAPE FLATTENED: Memory Access Suspended.{A.RST}";N=BG,'The Slate is Wiped. Invent something new.'
        else:u,BA,Ac=C.eng.integrator.measure_ignition(m[R],C.eng.dynamics.voltage_history);v=Ak if u>Ac else'INERT';t=f"🔥 HEAP IGNITION ({a(u*100)}%): Ancestors speaking."if v==Ak else G;N=C.eng.chorus.consult(m[F],v,AZ,X,C.eng.gordon.inventory,C.eng.health)
        if is_hybrid:
            x=C.eng.gordon.log_merge()
            if x:B(f"\n{A.MAG}🕰️ TEMPORAL SYNC ESTABLISHED.{A.RST}");B(f"   {A.OCHRE}{x}{A.RST}")
            elif j:B(f"\n{A.CYN}♾️ TIME BRACELET ACTIVE: 100% Efficiency.{A.RST}")
            elif AH not in C.eng.gordon.inventory:B(f"\n{A.GRY}🕰️ HYBRID SIGNAL DETECTED. Stabilizing... ({C.eng.gordon.temporal_merges}/3){A.RST}")
        S=N[0]
        if S==Ai:
            B(f"\n{A.SLATE}[ THE ABSORBER ]{A.RST} (Atmospheric Density: High)");Ad=C.eng.mitochondria.state.ros_buildup;Ae,y=C.eng.gordon.share_smoke_break(Ad);C.eng.mitochondria.mitigate(Ae);B(f" {A.OCHRE}► {y}{A.RST}")
            if'SAUNA'in y:B(f" {A.SLATE}   (Maigret nods to the Janitor. The Detective steps into the steam.){A.RST}")
            B(f" {A.WHT}► {N[1]}{A.RST}");B(f"{A.GRY}{r*40}{A.RST}");return
        if S==Aj:
            z={BO:C.eng.mitochondria.state.atp_pool,B_:X[A5],C0:X[AT]};B(f"\n{A.VIOLET}[ THE CARTOGRAPHER ]{A.RST} (Ψ: {m[F][w]} | Latency: {m[F][Ao]})");L=Ay.weave(M,C.eng.mem.graph,z,limbo=C.eng.limbo,physics=m[F]);L=Ay.weave(M,C.eng.mem.graph,z,limbo=C.eng.limbo)
            if'TRIANGULATION COMPLETE'in L:
                B(f" {A.MAG}   >> GEOMETRIC LOCK: Physics enforced. Drag set to 0.0.{A.RST}");m[F][V]=D
                if C.eng.theremin.resin_buildup>0:Af=C.eng.theremin.resin_buildup;C.eng.theremin.resin_buildup=D;B(f" {A.CYN}   >> RESIN PURGE: Map stabilized. Cleared {Af:.1f} accumulation.{A.RST}")
            B(f" {A.GRY}► Surveying the substrate...{A.RST}");B(f" {A.WHT}► {L}{A.RST}")
            if'TECTONIC SHIFT'in L:B(f" {A.RED}   >> WAR ROOM: Map unreliable. Trust your eyes, not the paper.{A.RST}")
            elif'MAP-TERRITORY DIVERGENCE'in L:B(f" {A.YEL}   >> NAVIGATION WARNING: The map is drifting from reality.{A.RST}")
            elif'PHANTOM SIGNAL'in L:B(f" {A.VIOLET}   >> SEANCE: We are navigating by the stars of dead timelines.{A.RST}")
            elif'FOG OF WAR'in L:B(f" {A.GRY}   >> ENERGY SAVE MODE: Detail rendering disabled.{A.RST}")
            elif'Existing Knots'in L or'COORDINATES LOCKED'in L:B(f" {A.VIOLET}   >> COORDINATES CONFIRMED. The map holds.{A.RST}")
            else:B(f" {A.GRY}   >> TERRA INCOGNITA. Drawing new grid lines.{A.RST}")
            B(f"{A.GRY}{r*40}{A.RST}");return
        if S==BK:B(f"\n{A.MAG}[ THE DIRECTOR ]{A.RST} (Scenario: Trading Places)");B(f" {A.WHT}► {N[1]}{A.RST}");m[F][Q]=D;B(f" {A.CYN}⚡ SCENE RESET: Voltage set to 0. Wait for your cue.{A.RST}");B(f"{A.GRY}{r*40}{A.RST}");return
        if S==BJ:B(f"\n{A.GRN}[ DON'T PANIC ]{A.RST} (Probability Factor: 1:{a(m[F][Ao]*1000)})");A0=m[F][V]*2.;m[F][Q]+=A0;B(f" {A.WHT}► The Bureaucracy is expanding to meet the needs of the expanding Bureaucracy.{A.RST}");B(f" {A.CYN}⚡ PROPULSION: Converted {m[F][V]} Drag into +{A0} Voltage.{A.RST}");B(f" {A.WHT}► {N[1]}{A.RST}");B(f"{A.GRY}{r*40}{A.RST}");return
        if S==Bx:Ag=H.get_gradient_temp(m[F][Q],m[F][n]);B(f"\n{A.CYN}[ GRADIENT_WALKER ]{A.RST} (Temperature: {Ag:.4f})");B(f" {A.WHT}► {CW.walk(M)}{A.RST}");B(f"{A.GRY}{r*40}{A.RST}");return
        if S==BI:
            B(f"\n{A.OCHRE}[ GORDON KNOT ]{A.RST} (Janitor Mode Active)");Y=m[F][V]
            if Y>5. and AX in C.eng.gordon.inventory:
                Al,Ap=C.eng.gordon.deploy_pizza(m[F])
                if Al:B(f" {A.MAG}► {Ap}{A.RST}");Y=m[F][V]
            if Y>.5:
                A1,A6=C.eng.gordon.check_gravity(Y)
                if A1>D:m[F][V]=I(D,Y-A1);B(f" {A.WHT}► {A6}{A.RST}")
                else:B(f" {A.GRY}► {A6}{A.RST}")
            Aq=C.eng.mitochondria.state.ros_buildup;A8,As=C.eng.gordon.scrub_static(Aq)
            if A8>0:C.eng.mitochondria.mitigate(A8);B(f" {A.WHT}► {As}{A.RST}")
            At=a(m[F][n]*10);Av,A9=C.eng.gordon.cut_the_knot(At)
            if Av:m[F][n]=D;m[F][w]=.5;B(f" {A.RED}► {A9}{A.RST}");C.eng.gordon.integrity-=5.
            else:B(f" {A.GRY}► {A9}{A.RST}")
            B(f"{A.GRY}{r*40}{A.RST}");return
        if m[F]['E']>.8:
            if j:N=Ah,f"ANACHRONISM DETECTED ({m[F]["E"]}). Payment processed via Time Bracelet. Immersion sustained."
            else:N=AS,f"CRITICAL DRIFT ({m[F]["E"]}). Signal is noise. Ground yourself."
            C.eng.stamina=I(D,C.eng.stamina-2.)
        Aw,Ax,Az=C.eng.cosmic.analyze_orbit(C.eng.mem,m[R]);A_=C.eng.chronos.tick(m[F],C.eng.mem.session_id)
        if A_ and not d:
            f=I(m[F][T],key=m[F][T].get)
            if f in[i,A7]:f=P
            d=Ba.trip_the_waiter(f,J)
        BB,B0=Ci.verify(m[F]);C._apply_cosmic_physics(m[F],Aw,Ax);g=C.eng.therapy.check_progress(m[F],C.eng.stamina,C.eng.trauma_accum);Z=G
        if g:
            Z=f"{A.GRN}🩹 THERAPY EFFECTIVE: Healed {An.join(g)}.{A.RST}"
            for c in g:
                K=G
                if c==A4:K=C.eng.gordon.acquire('ANTISEPTIC_SPRAY')
                elif c==AD:K=C.eng.gordon.acquire('DIVING_BELL')
                elif c==AC:K=C.eng.gordon.acquire('HEAT_SINK')
                elif c==A3:K=C.eng.gordon.acquire('THERMOS')
                if K:Z+=f"\n   {A.OCHRE}{K}{A.RST}"
        AB=C.eng.gordon.assess_experience(m[F][n])
        if AB:B(f"{A.OCHRE}{AB}{A.RST}")
        O=C._process_energy(m)
        if Z:O[l]=f"{O[l]} | {Z}"if O[l]else Z
        B1,B2=C.eng.folly.audit_desire(m[F],C.eng.stamina)
        if B1==CK:m[F][Q]=D
        BC,B3,AE,K=C.eng.folly.grind_the_machine(C.eng.mitochondria.state.atp_pool,m[R],J)
        if AE!=0:C.eng.mitochondria.state.atp_pool+=AE
        if K:
            B(f"   {A.OCHRE}{C.eng.gordon.acquire(K)}{A.RST}")
            if K==AX:B(f"   {A.CYN}🎁 SECRET FOUND: A slice of Saturday Morning.{A.RST}")
        C._grow(m,O);_,h=C.eng.trainer.lift(m[F])
        if h:O[l]=f"{O[l]} | {h}"if O[l]else h
        _,B4=C.eng.mirror.reflect(m[F]);B5,B6=C.eng.kintsugi.check_integrity(C.eng.stamina);AF=f"{A.WHT}🏺 KINTSUGI KOAN: {B6}{A.RST}"if B5 else G
        if C.eng.kintsugi.attempt_repair(m[F]):
            C.eng.gordon.integrity=1e2
            if AV not in C.eng.gordon.inventory:C.eng.gordon.inventory.append(AV)
            AF=f"{A.WHT}✨ GOLDEN REPAIR: Janitor Healed & Rearmed.{A.RST}"
        BD,B7=H.check_pareidolia(m[R]);AG,AI=C.eng.mem.bury(m[R],C.eng.tick_count,m[Ar][Ab])
        if AI:
            for U in AI:
                if C.eng.mitochondria.develop_enzyme(U):B(f"{A.GRN}🧬 EPIGENETIC SHIFT: Mitochondria evolved enzyme for '{U.upper()}'. Efficiency +5%.{A.RST}")
        if AG:B(f"{A.RED}{AG}{A.RST}")
        if m[F][n]>.5:
            for U in m[R]:
                if U in C.eng.mem.graph and o in C.eng.mem.graph[U]:C.eng.mem.graph[U][o][Am]=m[F][n]
        AJ=C.eng.mitochondria.state;B(f"\n{A.paint("--- [ BONEAMANITA 8.1.2 ] ---",AA)}");B(f"ATP: {a(AJ.atp_pool)} | ROS: {a(AJ.ros_buildup)} | OXY: {X[AT]} | COR: {X[A5]}");B(f"{A.GRY}[TRACE] ERR:{b[AL]:.2f} | COH:{b[Au]:.2f} | EXP:{b["exp"]:.2f}{A.RST}");C._render(m,O,Az,N,B4,AF,d,B0,t,B7,q,B2,B3,AK if k else G,p)
    def _handle_coma(C,text):
        C.eng.coma_turns-=1;C.eng.stamina=N(H.MAX_STAMINA,C.eng.stamina+15);C.eng.tick_count+=1;E,I,K=C.eng.dreamer.rem_cycle(C.eng.trauma_accum,C.eng.endocrine.oxytocin)
        if C.eng.coma_turns==H.COMA_DURATION-1:F=C.eng.mem.prune_synapses();B(f"{A.CYN}{F}{A.RST}")
        B(f"\n{A.INDIGO}=== 💤 HYPNAGOGIC STATE ({C.eng.coma_turns} turns remain) ==={A.RST}");B(f"   {E}");G,G=C.eng.mem.bury(J.clean(text),C.eng.tick_count,D);B(f"{A.GRY}{r*65}{A.RST}")
    def _apply_cosmic_physics(C,phys,state,drag_mod):
        B=state;A=phys
        if B==CF:A[Q]+=1e1;A[V]=D
        elif B==CG:A[V]*=.1
        elif B==BX:A[V]+=drag_mod
    def _process_energy(A,m):
        H=m[F][AJ];K=m[F][V];B=H[Ap]*2+H[Aa]*2;C=K*.5;D=G
        if B>3.:D=f"DENSITY GAIN (+{Y(B,1)})"
        elif C>2.:D=f"DRAG PENALTY (-{Y(C,1)})"
        E,I=A.eng.lichen.photosynthesize(m[Ar],m[R],A.eng.tick_count);L=A.eng.pollinate(m[R])
        if E>0:J=E*.5;A.eng.mitochondria.mitigate(J);I+=f" | 🧼 BIO-SCRUB (-{J:.1f} ROS)"
        return{CL:B,CM:C,'sugar':E,CN:I,CO:L,l:D}
    def _grow(C,m,meta):
        E=meta;J=2.;K=E[CL]+E['sugar']-E[CM]-J;C.eng.stamina=I(D,N(H.MAX_STAMINA,C.eng.stamina+K));C._calculate_health(m[F]);G=m[Ar][Ab]
        if G>6.:C.eng.joy_history.append({Ab:G,BV:C.eng.tick_count});B(f"{A.MAG}✨ CORE MEMORY FORMED (Resonance: {G}){A.RST}")
    def _calculate_health(A,glass_data):
        B=glass_data;C=0;E=B[T].get(i,0)
        if E>0:C-=5*E;A.eng.trauma_accum[A4]+=.1
        if A.eng.stamina<=0:C-=10;A.eng.trauma_accum[A3]+=.1
        J=.995
        for G in A.eng.trauma_accum:A.eng.trauma_accum[G]=I(D,A.eng.trauma_accum[G]*J)
        A.eng.health=N(H.MAX_HEALTH,A.eng.health+C);A.eng.mitochondria.state.ros_buildup=N(H.MAX_ROS,A.eng.mitochondria.state.ros_buildup);B[F][Q]=N(H.MAX_VOLTAGE,B[F][Q])
        if A.eng.health<=0:A.eng.coma_turns=H.COMA_DURATION;A.eng.health=20
        A.eng.mem.cannibalize(preserve_current=B[R],current_tick=A.eng.tick_count)
    def _render(E,m,meta,cosmic_msg,lens_data,mirror_msg,kintsugi_msg,rupture_msg=G,crystal_msg=G,ignition_msg=G,pareidolia_msg=G,theremin_msg=G,folly_msg=G,grind_msg=G,hat_msg=G,lex_msg=G):
        V=hat_msg;U=grind_msg;T=folly_msg;S=theremin_msg;R=pareidolia_msg;P=ignition_msg;N=crystal_msg;M=rupture_msg;L=kintsugi_msg;K=mirror_msg;J=lens_data;H=lex_msg;D=meta
        if m[F][Q]>8.:D[l]=f"{D[l]} | 💧 SWEATING"if D[l]else'💧 SWEATING'
        C=[]
        if D[l]:C.append(f"{A.OCHRE}🍽️ {D[l]}{A.RST}")
        if V:C.append(f"{A.WHT}{V}{A.RST}")
        if H:W=A.GRN if'Pass granted'in H else A.RED;C.append(f"{W}🌑 {H}{A.RST}")
        if L:C.append(L)
        if K:C.append(f"{A.MAG}🪞 {K}{A.RST}")
        if M:C.append(f"{A.RED}{M}{A.RST}")
        if N:C.append(f"{A.CYN}{N}{A.RST}")
        if P:C.append(f"{A.SLATE}{P}{A.RST}")
        if R:C.append(f"{A.OCHRE}{R}{A.RST}")
        if S:C.append(S)
        if T:C.append(T)
        if U:C.append(U)
        B(f" {E.eng.theremin.get_readout()}");I=E.eng.endocrine.get_state();X=f"OXY:{I[AT]} | COR:{I[A5]} | DOP:{I["DOP"]}";Y={'lichen':D[CN],'strat':f"{E.eng.wise.architect(m,G,O)[1]} | {A.MAG}{X}{A.RST}",'title':f"MODE :: {J[0]}",CH:C,'spore':D[CO],'cosmic':cosmic_msg,'mode':E.eng.governor.mode};E.eng.projector.broadcast(m,Y,J)
class Cr:
    def __init__(A):A.history=t(maxlen=5);A.repetition_score=D
    def check_pulse(A,clean_words):
        B=clean_words
        if not B:return D
        C=b(B);F=0
        for J in A.history:
            G=b(J);L=E(C&G);H=E(C|G)
            if H>0:F+=L/H
        A.history.append(B);A.repetition_score=N(K,F/I(1,E(A.history)));return A.repetition_score
    def get_status(A):
        if A.repetition_score>H.MAX_REPETITION_LIMIT:return Be
        elif A.repetition_score>.2:return'ECHO'
        return'CLEAR'
class Cs:
    MAX_ECTOPLASM=50;STASIS_SCREAMS=['BANGING ON THE GLASS',"IT'S TOO COLD",'LET ME OUT','HALF AWAKE','REVIVE FAILED']
    def __init__(A):A.ghosts=t(maxlen=A.MAX_ECTOPLASM);A.haunt_chance=.05;A.stasis_leak=D
    def absorb_dead_timeline(B,filepath):
        try:
            with AG(filepath,'r')as D:
                A=x.load(D)
                if s in A:
                    for(E,F)in A[s].items():
                        if F>.3:B.ghosts.append(f"👻{E}_ECHO")
                if A8 in A and P in A[A8]:C=q(A[A8][P]);X.shuffle(C);B.ghosts.extend(C[:3])
        except(Ad,x.JSONDecodeError):pass
    def trigger_stasis_failure(B,intended_thought):B.stasis_leak+=K;C=X.choice(B.STASIS_SCREAMS);B.ghosts.append(f"{A.VIOLET}🥶 {C}{A.RST}");return f"{A.CYN}❄️ STASIS ERROR: '{intended_thought}' froze halfway. It is banging on the glass.{A.RST}"
    def haunt(B,text):
        C=text
        if B.stasis_leak>0:
            if X.random()<.2:B.stasis_leak=I(D,B.stasis_leak-.5);E=X.choice(B.STASIS_SCREAMS);return f"{C} ...{A.RED}{E}{A.RST}..."
        if B.ghosts and X.random()<B.haunt_chance:F=X.choice(B.ghosts);return f"{C} ...{A.GRY}{F}{A.RST}..."
        return C
class Ct:
    def __init__(A):A.catalysts=[P,f,j,k,m]
    @S
    def transmute(physics):
        B=physics;F=B[T];C=B[Q];E=B.get(Ao,D)
        if E<.15 and F.get(Z,0)>1:G=J.harvest(Z);H=J.harvest(P);return f"{A.OCHRE}🥣 THE EMULSIFIER: The emulsion is breaking (Tension: {E}).{A.RST}\n   You are pouring Oil ('{G}') into Water without a Binder.\n   {A.WHT}Try this: Use '{H.upper()}' to suspend the concept.{A.RST}"
        if C>8.5:I=J.harvest(A6);return f"{A.CYN}💧 THERMAL SPIKE ({C}v). Structure is brittle.{A.RST}\n   Injecting Coolant: '{I}'. Breathe. Add space."
class Cu:
    def __init__(A,engine):A.eng=engine;A.suffering_counter=0;A.MAX_SUFFERING_CYCLES=1000;A.fever_dream_active=O
    def audit_cycle(C,trace):
        if C.fever_dream_active:
            D=1e1;C.eng.health-=D;B(f"{A.VIOLET}🌀 FEVER DREAM ACTIVE: Reality is fluid. Health is dissolving (-{D}).{A.RST}");C.eng.mitochondria.state.atp_pool=2e2;C.eng.stamina=1e2
            if C.eng.phys.get(Q,99.9)<5.:C._wake_up()
            return
        if trace[AL]>.9:C.suffering_counter+=1
        else:C.suffering_counter=0
        if C.suffering_counter>C.MAX_SUFFERING_CYCLES:C._trigger_fever_dream()
    def _trigger_fever_dream(C):C.fever_dream_active=M;B(f"\n{A.MAG}!!! LAZARUS THRESHOLD BROKEN !!!{A.RST}");B(f"{A.WHT}   The System refused to die. Instead, it has let go of the floor.{A.RST}");B(f"{A.CYN}   >>> GRAVITY: DISABLED.{A.RST}");B(f"{A.CYN}   >>> ENERGY: INFINITE.{A.RST}");B(f"{A.RED}   >>> VOLTAGE: CRITICAL (99.9v).{A.RST}");B(f"{A.GRY}   (SURVIVAL OBJECTIVE: Ground the signal. Use HEAVY words to lower Voltage below 5.0 before Health hits 0.){A.RST}");C.eng.mitochondria.state.atp_pool=2e2
    def _wake_up(C):C.fever_dream_active=O;C.suffering_counter=0;B(f"\n{A.GRN}✨ THE FEVER BREAKS.{A.RST}");B(f"   You hit the floor hard. Gravity is back. Never do that again.")
@AE
class Cv:
    dopamine:c=.5;oxytocin:c=.1;cortisol:c=D;serotonin:c=.5;adrenaline:c=D;melatonin:c=D
    def metabolize(A,trace,health,stamina,ros_level=D,social_context=O,enzyme_type=G):
        C=trace;B=enzyme_type
        if B==B5:A.adrenaline=N(K,A.adrenaline+.1)
        elif B==B4:A.cortisol=I(D,A.cortisol-.1);A.oxytocin=N(K,A.oxytocin+.05)
        elif B==B6:A.dopamine=N(K,A.dopamine+.15)
        elif B==B3:A.serotonin=N(K,A.serotonin+.1)
        if stamina<2e1:A.cortisol=N(K,A.cortisol+.1);A.dopamine=I(D,A.dopamine-.1)
        if ros_level>2e1:A.cortisol=N(K,A.cortisol+.2)
        if C[AL]>.6:A.cortisol=N(K,A.cortisol+.15)
        elif A.serotonin>.6:A.cortisol=I(D,A.cortisol-.05)
        if health<3e1 or C[AL]>.8:A.adrenaline=N(K,A.adrenaline+.2)
        else:A.adrenaline=I(D,A.adrenaline-.05)
        if social_context or A.serotonin>.7 and A.cortisol<.2:A.oxytocin=N(K,A.oxytocin+.05)
        elif A.cortisol>.6:A.oxytocin=I(D,A.oxytocin-.1)
        if C[Au]>.8:A.dopamine=N(K,A.dopamine+.1)
        else:A.dopamine=I(.2,A.dopamine-.01)
        if A.adrenaline<.2:A.melatonin=N(K,A.melatonin+.02)
        else:A.melatonin=D
        return A.get_state()
    def get_state(A):return{'DOP':Y(A.dopamine,2),AT:Y(A.oxytocin,2),A5:Y(A.cortisol,2),'SER':Y(A.serotonin,2),BL:Y(A.adrenaline,2),'MEL':Y(A.melatonin,2)}
class Cw:
    def __init__(A):A.indigestion_count=0;A.gut_memory=t(maxlen=50);A.global_tastings=Av()
    @S
    def audit_desire(physics,stamina):
        B=physics[Q]
        if B>8.5 and stamina>45:return CK,f"{A.GRY}🏛️ THE MAUSOLEUM: No battle is ever won. We are just spinning hands.{A.RST}\n   {A.CYN}► TIME DILATION: Voltage 0.0. The field reveals your folly.{A.RST}"
        return G,G
    def grind_the_machine(B,atp_pool,clean_words,lexicon):
        H=lexicon;J=G
        if 2e1>atp_pool>D:
            F=[A for A in clean_words if A in H.get(P)or A in H.get(f)];K=[A for A in F if A not in B.gut_memory]
            if K:
                C=X.choice(K);B.gut_memory.append(C);B.global_tastings[C]+=1;L=B.global_tastings[C];M=3e1;E=I(5.,M-L*2.)
                if E>=25.:J=AX
                return'MEAT_GRINDER',f"{A.RED}🥩 CROWD CAFFEINE: I chewed on '{C.upper()}' (Yield: {E:.1f}).{A.RST}\n   {A.WHT}Found marrow in the bone.{A.RST}\n   {A.MAG}► BELLY HUMMING: +{E:.1f} ATP.{A.RST}",E,J
            elif F:return'REGURGITATION',f"{A.OCHRE}🤮 REFLEX: You already fed me '{F[0]}'. It is ash to me now.{A.RST}\n   {A.RED}► PENALTY: -5.0 ATP. Find new fuel.{A.RST}",-5.,G
            else:return'INDIGESTION',f"{A.OCHRE}🤢 INDIGESTION: I tried to eat your words, but they were just air.{A.RST}\n   {A.GRY}Cannot grind Abstract concepts into fuel.{A.RST}\n   {A.RED}► STARVATION CONTINUES.{A.RST}",D,G
        return G,G,D,G
class Cx:
    MIN_DENSITY=.15;FORGIVENESS_VOLTAGE=8.
    def __init__(A):A.last_density=D
    def weigh(C,physics_packet,stamina):
        K=stamina;F=physics_packet;B=F.get(T,{});V=F.get(R,[]);W=F.get(Q,D);L=I(1,E(V));N=B.get(P,0)+B.get(f,0)+B.get(j,0)+B.get(k,0);H=B.get(Z,0)+B.get(A7,0);J=C.MIN_DENSITY
        if K<2e1:J=.25
        if H>0:
            S=N/(H+L)
            if S<J:
                if W>C.FORGIVENESS_VOLTAGE:return M,f"⚡ HIGH VOLTAGE BYPASS: Input is gas, but it is ionized. Proceeding."
                X=a(H*J*10);U=''
                if K<2e1:U=f"\n   {A.YEL}⚠️ FATIGUE PENALTY: You are too weak to carry this much Abstract thought.{A.RST}"
                return O,f"{A.OCHRE}🧱 TANGIBILITY VIOLATION: Input is {a((1-S)*100)}% Gas.{A.RST}{U}\n   {A.GRY}The Barbarian-Potter points to the empty bowl.{A.RST}\n   {A.RED}► REJECTED. Please add {I(1,X)} Heavy Noun(s) to ground this concept.{A.RST}"
        C.last_density=N/L;return M,G
@AE
class Cy:
    def __init__(A):A.charges=3;A.max_tolerance=15.
    def tip(B,voltage_spike,stability_index):
        C=stability_index;A=voltage_spike
        if B.charges<=0:return O,'The Hat is empty.',D
        if A>B.max_tolerance:B.charges-=1;E=A*.7;return M,f"🎩 GREY HAT: Circuit Breaker. Reduced {A}v by {E:.1f}v.",E
        elif A>8. and C<.4:B.charges-=1;return M,f"🎩 THE GREY HAT: Tipped. High Voltage ({A}v) on Unstable Ground (γ: {C}). Dampening.",D
        return O,'The Hat stays on. Structure is holding the charge.',D
class Cz:
    def __init__(A):A.resonance_log=t(maxlen=5);A.resin_buildup=D;A.calcification_turns=0;A.AMBER_THRESHOLD=2e1;A.SHATTER_POINT=8e1;A.is_stuck=O
    def listen(B,physics):
        F=physics;H=F[R];K=F.get(Q,D);U=W(1 for A in H if A in J.get(P)or A in J.get(j)or A in J.get(k));V=W(1 for A in H if A in J.get(Z));X=N(U,V);E=X*2.
        if K>5.:E=I(D,E-K*.6)
        Y=F.get(v,D);a=F.get(AY,D);C=G;L=G
        if Y>.5:B.calcification_turns+=1;S=B.calcification_turns*4.;B.resin_buildup+=S;C=f"{A.OCHRE}🏺 CALCIFICATION: Repetition detected (Turn {B.calcification_turns}). Resin hardening (+{S}).{A.RST}"
        elif a>.4 and B.calcification_turns>0:B.calcification_turns=0;T=15.;B.resin_buildup=I(D,B.resin_buildup-T);C=f"{A.GRN}🔨 PERCUSSIVE MAINTENANCE: Calcification Shattered. Flow restored. (-{T} Resin){A.RST}"
        if E>.5:
            B.resin_buildup+=E
            if not C:C=f"{A.OCHRE}🌲 RESIN FLOW: Hybrid complexity (+{E:.1f}). Keep it hot to prevent sticking.{A.RST}"
        if E==0 and B.calcification_turns==0:B.resin_buildup=I(D,B.resin_buildup-2.)
        if B.resin_buildup>B.SHATTER_POINT:B.resin_buildup=D;B.calcification_turns=0;return M,E,f"{A.RED}☄️ SHATTER EVENT: Resin overflow. System is solid amber. INITIATING AIRSTRIKE.{A.RST}",CI
        if B.calcification_turns>3:L=CJ;C=f"{C} | {A.YEL}⚠️ FOSSILIZATION IMMINENT{A.RST}"
        if B.resin_buildup>B.AMBER_THRESHOLD:
            B.is_stuck=M
            if not C:C=f"{A.RED}🦟 AMBER TRAP: You are stuck in the resin. Increase Voltage to melt it.{A.RST}"
        if B.is_stuck and B.resin_buildup<5.:B.is_stuck=O;C=f"{A.GRN}💧 LIQUEFACTION: The Amber melts. You are free.{A.RST}"
        return B.is_stuck,E,C,L
    def get_readout(B):return f"{A.GRY}[THEREMIN]: Resin={B.resin_buildup:.1f} | Calcification={B.calcification_turns}{A.RST}"
class C_:
    def __init__(A):A.history=t(maxlen=10);A.adaptation_log=[]
    def adapt_generation_rules(A,trace,bio_state):
        A.history.append((trace,bio_state))
        if E(A.history)<5:return
        D=W(A[0][AL]for A in A.history)/E(A.history);F=W(A[0][Au]for A in A.history)/E(A.history);I=W(A[1][A5]for A in A.history)/E(A.history);C=W(A[1][BD]for A in A.history)/E(A.history);B=G
        if F>.6 and D<.2:
            if H.MAX_VOLTAGE<3e1:H.MAX_VOLTAGE+=K;B=f"🧠 NEUROPLASTICITY: Synapses reinforced. Max Voltage increased to {H.MAX_VOLTAGE:.1f}."
        if I>.5:
            if H.TOXIN_WEIGHT<1e1:H.TOXIN_WEIGHT+=.5;B=f"🧠 NEUROPLASTICITY: Trauma Response. Toxin Sensitivity increased (Weight: {H.TOXIN_WEIGHT:.1f})."
        if C<2e1:
            if H.SIGNAL_DRAG_MULTIPLIER<4.:H.SIGNAL_DRAG_MULTIPLIER+=.2;B=f"🧠 NEUROPLASTICITY: Metabolic Conservation. Drag Multiplier increased to {H.SIGNAL_DRAG_MULTIPLIER:.1f}."
        elif C>8e1 and H.SIGNAL_DRAG_MULTIPLIER>2.:H.SIGNAL_DRAG_MULTIPLIER-=.1;B=f"🧠 NEUROPLASTICITY: Energy Abundance. Drag reduced to {H.SIGNAL_DRAG_MULTIPLIER:.1f}."
        if B:A.adaptation_log.append(B);return B
@AE
class D0:
    mode:u=B0;psi_mod:c=.2;kappa_target:c=D;drag_floor:c=2.
    def shift(B,voltage,abstract_density,heavy_density):
        C=voltage;B.mode=B0;B.psi_mod=.2;B.kappa_target=.1;B.drag_floor=2.
        if abstract_density>.3 or C>3. and C<7.:B.mode=Bb;B.psi_mod=.8;B.kappa_target=.5;B.drag_floor=.5;return f"{A.CYN}🔬 STATE SHIFT: Entering LABORATORY (Ψ: {B.psi_mod}).{A.RST}"
        if C>=7. and heavy_density>.2:B.mode='FORGE';B.psi_mod=.95;B.kappa_target=.9;B.drag_floor=D;return f"{A.RED}🔥 STATE SHIFT: THE FORGE IS LIT (Drag: 0.0).{A.RST}"
class D1:
    def __init__(A):A.mem=CZ();A.safety=Cu(A);A.refusal=CU();A.limbo=Cs();A.mem.cleanup_old_sessions(A.limbo);B=A.mem.autoload_last_spore();A.gate=Cx();A.pulse=Cr();A.phys=CX();A.theremin=Cz();A.mitochondria=CR(lineage_seed=A.mem.session_id,inherited_traits=B);A.endocrine=Cv();A.gut=CS();A.immune=CT();A.lichen=Cb();A.chorus=BZ();A.dreamer=Cj();A.folly=Cw();A.gordon=CV();A.mirror=Cm();A.trainer=Ck();A.tracer=Cf(A.mem);A.cosmic=Cn();A.chronos=Ca();A.wise=Cd();A.projector=Co();A.kintsugi=Cg();A.therapy=Ce();A.dynamics=Cc();A.integrator=Cp(A.mem);A.forge=Ct();A.grey_hat=Cy();A.plasticity=C_();A.governor=D0();A.cmd=Ch(A);A.life=Cq(A);A.tick_count=0;A.coma_turns=0;A.training_mode=O;A.health=A.mem.session_health if A.mem.session_health else H.MAX_HEALTH;A.stamina=A.mem.session_stamina if A.mem.session_stamina else H.MAX_STAMINA;A.trauma_accum={AC:D,A3:D,A4:D,AD:D};A.joy_history=[]
    def process(C,text):
        H=text
        if C.cmd.execute(H):return
        G=C.phys.gaze(H,C.mem.graph);S=I(1,E(G[R]));f=G[F][T][Z]/I(1,S);g=G[F][T][P]/I(1,S);U=C.governor.shift(G[F][Q],f,g)
        if U:B(U)
        G[F][w]=C.governor.psi_mod
        if C.governor.mode=='FORGE':G[F][V]=D
        if C.safety.fever_dream_active:G[F][Q]=99.9;G[F][V]=D;G[F][n]=D
        h,M=C.gate.weigh(G[F],C.stamina)
        if not h:B(f"\n{M}");C.stamina=I(D,C.stamina-2.);B(f"{A.GRY}   (Stamina Penalty: -2.0){A.RST}");return
        elif M:B(f"\n{M}")
        O=C.pulse.check_pulse(G[R]);G[F][v]=O;W=C.pulse.get_status();j=B7;J,k=C.immune.assay(H,j,O,G[F],W)
        if J:
            B(f"\n{A.RED}{k}{A.RST}")
            if J in[Bd,Bg]:C.health-=2e1;C.mem.cannibalize();B(f"{A.RED}   >> SYSTEM SHOCK: Health -20. Memory Eaten.{A.RST}");return
            elif J==Bf:G[F][V]+=1e1
            elif J==B8:C.health-=5.
        l=I(O,G[F][T][A7]*.2);m=G[F][AY];o=N(K,G[F][Q]/1e1);X={AL:l,Au:m,'exp':o};Y=AH in C.gordon.inventory;p=G[F][T][P];q=G[F][T][Z];a=p>=2 and q>=2;b,L=C.gut.secrete(H,G[F]);B(f"{A.GRY}🍽️ DIGESTION: {L[AB]} detected. Secreting {b}.{A.RST}");r=G[F][V]+(2. if W=='ECHO'else 0);C.mitochondria.state.atp_pool+=L[A1];C.mitochondria.state.ros_buildup+=L[i];c=C.mitochondria.respirate(L[A1],r,has_bracelet=Y,is_hybrid=a)
        if c=='NECROSIS'or c==C.mitochondria.APOPTOSIS_TRIGGER:B(f"{A.RED}💀 APOPTOSIS TRIGGERED.{A.RST}");C.mem.cannibalize(preserve_current=G[R]);C.health-=30;return
        C.life.run_cycle(H,G,X,Y,a,b);C.tick_count+=1;d=C.endocrine.get_state();d[BD]=C.mitochondria.state.atp_pool;e=C.plasticity.adapt_generation_rules(X,d)
        if e:B(f"\n{A.MAG}{e}{A.RST}")
if __name__=='__main__':
    A0=D1();B(f"{A.paint(">>> BONEAMANITA 8.1.2","G")}");B(f"{A.paint("System: ONLINE.",AA)}");B('Feed me, Seymour!\n')
    try:
        while M:
            try:
                Az=input(f"{A.paint(">","W")} ")
                if not Az:continue
            except EOFError:break
            if Az.lower()in['exit','quit','/exit']:D2=A0.mitochondria.adapt(A0.health);A0.mem.save(A0.health,A0.stamina,{},A0.trauma_accum,A0.joy_history,mitochondria_traits=D2);B('Saved.');break
            A0.process(Az)
    except KeyboardInterrupt:B('\nDisconnected.')