import sys, os, collections, traceback
sys.path.insert(0,'/home/gordonk/PycharmProjects/BoneAmanita'); os.chdir('/home/gordonk/PycharmProjects/BoneAmanita')
from engine import struts
_orig = struts.safe_get
hits=collections.Counter(); misses=collections.Counter(); mock_frames=collections.Counter()
def spy(obj, key, default=None):
    r=_orig(obj,key,default)
    stack=traceback.extract_stack()
    # direct caller of safe_get = frame just below spy
    caller=stack[-2]
    site=f"{os.path.relpath(caller.filename)}:{caller.lineno}"
    via_mock=any('mock_generation' in fr.name or 'hallucinate' in fr.name for fr in stack)
    keys=key if isinstance(key,(list,tuple)) else (key,)
    present=False
    if obj is not None:
        for k in keys:
            v=obj.get(k) if isinstance(obj,dict) else getattr(obj,k,None)
            if v is not None: present=True; break
    tag=f"{site} {keys}"
    if via_mock: mock_frames[tag]+= 1
    elif present: hits[tag]+=1
    else: misses[tag]+=1
    return r
struts.safe_get=spy
for name,mod in list(sys.modules.items()):
    if hasattr(mod,'safe_get') and getattr(mod,'safe_get') is _orig: setattr(mod,'safe_get',spy)
from main import BoneAmanita
for name,mod in list(sys.modules.items()):
    if hasattr(mod,'safe_get') and getattr(mod,'safe_get') is _orig: setattr(mod,'safe_get',spy)
eng=BoneAmanita({"provider":"mock","model":"mock","user_name":"T","boot_mode":"CONVERSATION"})
for msg in ["hello there, how is the weather in your head today?",
            "I keep circling the same thought and cannot land it."]:
    eng.process_turn(msg)
eng.orchestrator.shutdown()
h,m,mk=sum(hits.values()),sum(misses.values()),sum(mock_frames.values())
print(f"\nexcluding mock/hallucinate frames ({mk} calls there):")
print(f"  safe_get calls: {h+m}   resolved: {h}   fell to default: {m}  ({100*m/max(1,h+m):.0f}%)")
print("\nSites that ALWAYS fall through (never once resolved), by volume:")
n=0
for k,v in misses.most_common(40):
    if k not in hits:
        print(f"  {v:5d}x  {k}"); n+=1
    if n>=18: break
