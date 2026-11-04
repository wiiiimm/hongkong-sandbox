"""Exact full relevant-ground and BASIC equality across the Apex installation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-wave-verdant-multicore-ground-capture-v4-20261017';NEW=BASE/'government-xl-wave-verdant-current-ground-capture-v5-20261018'
BATCH='government-xl-wave-verdant-current-ground-equivalence-v5-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();receipts=[read(p/'result.json')for p in [OLD,NEW]];refs=[Path(__file__),OLD/'result.json',NEW/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in receipts[1]['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 files=['before-ground.json.gz','after-ground.json.gz','basic-actors.json.gz','capture-report.json.gz'];oldpins={e['path']:e['sha256']for e in receipts[0]['evidenceRefs']}
 for f in files:
  p=OLD/f;assert digest(p.read_bytes())==oldpins[str(p.relative_to(ROOT))];refs.append(p)
 ground=[]
 for phase in ['before','after']:
  a,b=[read(p/(phase+'-ground.json.gz'))for p in [OLD,NEW]]
  assert a['domain']==b['domain']and a['roi']==b['roi']
  assert a['allDrawnFacetsIncludingVerticalAndDegenerateRetained']and b['allDrawnFacetsIncludingVerticalAndDegenerateRetained']
  assert a['completeRelevantDrawnTriplets']==b['completeRelevantDrawnTriplets']
  ground.append(dict(phase=phase,allRelevantDrawnFacesIdentical=True,faces=len(b['completeRelevantDrawnTriplets']),oldWholeMapFaces=a['totalDrawnFaces'],currentWholeMapFaces=b['totalDrawnFaces']))
 a,b=[read(p/'basic-actors.json.gz')for p in [OLD,NEW]];assert a['rows']==b['rows']and len(b['rows'])==44
 a,b=[read(p/'capture-report.json.gz')for p in [OLD,NEW]];assert a['closures']==b['closures'];assert b['strictExteriorUnchanged']and b['startEndAllInputsVerified']
 result=dict(currentNativeActors=6684,completeCurrentForms=b['completeCurrentForms'],basicActorsExactlyIdentical=44,productionModuleClosuresExactlyIdentical=True,ground=ground,currentStrictExteriorUnchanged=True,fullAcceptance=False,qualification='Exact equality of all relevant drawn triangles including vertical/degenerate faces and all44complete BASIC actor records permits reuse of prior geometry calculations on these exact inputs. Whole-map exterior changed with Apex; no old exterior hash or overall placement approval is transferred. Source identity, unresolved301562 support interpretation and full assembly browser/fallback checks remain required.')
 save(DOC/'equivalence.json',result);out=module('wave_current_equivalence_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-complete-current-ground-basic-exact-equivalence-v5',list(set(refs)),dict(uids=['landsd/275510:0','landsd/275511:0'],summary=result,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True);print(result,flush=True)
if __name__=='__main__':main()
