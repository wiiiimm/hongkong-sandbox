"""Reconcile full terrain-neighbour results with exact unchanged installed reviews."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-neighbour-review-v2-20261020';DOC=BASE/BATCH
NAMES=dict(neighbours='government-xl-yoho-mall-i-neighbours-v2-20261020',physical='government-xl-yoho-mall-i-physical-review-v1-20261020',retained='government-xl-yoho-seven-physical-review-v1-20261020',scope='government-xl-yoho-mall-i-regional-scope-v1-20261020')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,name in NAMES.items():
   d=BASE/name;r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(k,file):
  p=BASE/NAMES[k]/file;key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key];refs.append(p);used[key]=pins[k][key];return read(p)
 near=take('neighbours','neighbour-checks.json');native=take('neighbours','native-neighbour-checks.json');scope=take('scope','scope.json');physical=take('physical','ROOT-PHYSICAL-REVIEW.json');old=take('retained','ROOT-PHYSICAL-REVIEW.json');inputs=take('neighbours','neighbour-inputs.json.gz')
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and old['sourceSpecificPhysicalInterpretationAccepted'];candidate=set(physical['uids']);towers=candidate-{'landsd/189427:0'}
 flagged={r['uid']for r in near['rows']if r['reasons']};assert flagged==towers
 for r in near['rows']:
  if r['uid']in towers:assert r['reasons']==['increased-neighbour-ground-gap']
  else:assert not r['reasons']
 assert set(scope['touchingNativeUids'])=={r['uid']for r in native['rows']}and len(native['rows'])==7
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath);entries={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']in scope['touchingNativeUids']:assert e['uid']not in entries;entries[e['uid']]=e;refs.append(p)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];refs.append(pointer);ledger=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid,e in entries.items():
   assert e['sha256']==old['sourceSHA256ByUid'][uid]
   state=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone();assert state==('installed-verified',e['sha256']);ledger.append(dict(uid=uid,state=state[0],sourceSHA256=state[1]))
 for r in native['rows']:
  terrain=r['terrain'];assert terrain['newlyWhollyBuried']==terrain['newlyUpwardWhollyBuried']==0
  if not r['passed']:
   assert terrain['maximumBurialIncrease']==0
   assert r['uid']=='landsd/300857:0' and terrain['minimumGapBefore']==terrain['minimumGapAfter'] and terrain['whollyBuriedBefore']==terrain['whollyBuriedAfter']==0
   assert r['support']['pinnedNativeUids']==['landsd/301636:0'] and r['support']['sameParentNativeUids']==[]
   deps=entries[r['uid']]['supportDependencies'];assert len(deps)==1;dep=deps[0];assert dep['uid']=='landsd/301636:0'and dep['state']=='installed'and dep['sha256']==entries[dep['uid']]['sha256']and dep['csuid']==entries[dep['uid']]['buildingCSUID']
   accepted=[a for a in old['accounts']if a['uid']==r['uid']];assert len(accepted)==4 and all(a['unresolved']==0 for a in accepted)
 for report in [near,native]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=sorted(candidate),currentSnapshotId=snapshot,ordinaryForms=len(inputs['rows']),checkedNativeUids=sorted(entries),verifiedInstalledSources=ledger,remainingNeighbourFailures=[],rawFlagsRetained=True,sourceSpecificNeighbourInterpretationAccepted=True,installationApproved=False,reviewer='Codex ROOT',basis='All ordinary flags are precisely the seven staged tower replacements, each now covered by full four-mode original/podium foundation and contact acceptance. They are not skipped neighbours: their replacement source and fallback are separately checked. All seven affected installed originals have zero newly buried faces and unchanged source hashes. The six ordinary native passes retain the unchanged checker decision, including podium301636's recorded 0.000001110276m maximum burial delta; no additional zero-delta threshold is imposed. Retained300857 has the same explicit installed podium and zero terrain regression; its footprint-only support fraction is superseded solely by its existing exact-source four-mode contact review. No other native failure or new physical failure is waived. Browser, identity, foreign collision interpretation and publication remain separate.')
 save(DOC/'ROOT-NEIGHBOUR-REVIEW.json',result);module('yoho_neighbour_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-terrain-neighbour-exact-source-review-reconciliation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
