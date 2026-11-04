"""Reconcile full terrain-neighbour results with exact unchanged installed reviews."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-neighbour-review-v2-20261021';DOC=BASE/BATCH
NAMES=dict(neighbours='government-xl-grandiose-proposed-scene-neighbours-v11-20261021',physical='government-xl-grandiose-physical-review-v1-20261021',scope='government-xl-grandiose-regional-scope-v2-20261021')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,name in NAMES.items():
   d=BASE/name;r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(k,file):
  p=BASE/NAMES[k]/file;key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key];refs.append(p);used[key]=pins[k][key];return read(p)
 near=take('neighbours','neighbour-checks.json');native=take('neighbours','native-neighbour-checks.json');scope=take('scope','scope.json');physical=take('physical','ROOT-PHYSICAL-REVIEW.json');inputs=take('neighbours','neighbour-inputs.json.gz')
 assert physical['sourceSpecificPhysicalInterpretationAccepted'];candidate=set(physical['uids']);towers=candidate-{'landsd/246824:0'}
 flagged={r['uid']for r in near['rows']if r['reasons']};assert flagged=={'landsd/81008:0','landsd/81151:0','landsd/81678:0'}
 for r in near['rows']:
  if r['uid']in candidate:assert not r['reasons']
  elif r['uid']in scope['touchingNativeUids']:assert not r['reasons']or r['reasons']==['existing-native-neighbour-requires-full-mesh-check','increased-neighbour-ground-gap']
  else:assert not r['reasons']
 assert set(scope['touchingNativeUids'])=={r['uid']for r in native['rows']}and len(native['rows'])==10
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath);entries={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']in scope['touchingNativeUids']:assert e['uid']not in entries;entries[e['uid']]=e;refs.append(p)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];refs.append(pointer);ledger=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid,e in entries.items():
   state=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone();assert state==('installed-verified',e['sha256']);ledger.append(dict(uid=uid,state=state[0],sourceSHA256=state[1]))
 for r in native['rows']:
  terrain=r['terrain'];assert r['passed']and terrain['newlyWhollyBuried']==terrain['newlyUpwardWhollyBuried']==0
 for report in [near,native]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=sorted(candidate),currentSnapshotId=snapshot,ordinaryForms=len(inputs['rows']),checkedNativeUids=sorted(entries),verifiedInstalledSources=ledger,remainingNeighbourFailures=[],rawFlagsRetained=True,maximumReportedBurialIncrease=max(r['terrain']['maximumBurialIncrease']for r in native['rows']),sourceSpecificNeighbourInterpretationAccepted=True,installationApproved=False,reviewer='Codex ROOT',basis='Both proposed originals are included in the conditional scene; the replaced roof fallback is excluded from ordinary-neighbour obligations. Its complete original physical checks remain required. Three footprint-only flags concern existing detailed originals and are resolved by their full actual-source before/after checks. All ten affected installed originals pass with zero new wholly buried faces and exact installed source hashes verified in Neon. The measured maximum burial increase is retained explicitly above. Every other ordinary neighbour has no flag. Raw flags remain preserved; visual, failure fallback, identity and publication checks remain independent.')
 save(DOC/'ROOT-NEIGHBOUR-REVIEW.json',result);module('yoho_neighbour_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-terrain-neighbour-exact-source-review-reconciliation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
