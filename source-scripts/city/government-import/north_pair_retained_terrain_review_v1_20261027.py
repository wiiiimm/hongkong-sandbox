"""Exact proposal-terrain review; raw existing support failures stay unapproved."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from west_kowloon_pair_physical_review_v1_20261027 import P,SOURCES
PAIRS={'landsd/20270:0':'landsd/159422:0','landsd/177605:0':'landsd/177604:0'}
BATCH=P+'retained-terrain-review-v2-20261027'
def terrain_rows(n,contexts,current):
 rows=n['nativeRows'];required=n['requiredNativeUids']
 assert len(rows)==len(required)==len(set(required))==67 and {r['uid']for r in rows}==set(required)
 assert n['forms']==786 and n['basicFlags']==[]
 assert {r['uid']for r in rows if not r['passed']}==set(PAIRS)==set(contexts)
 result=[]
 for raw in rows:
  u=raw['uid'];t=raw['terrain'];assert raw['triangles']>0 and raw['vertices']>0
  assert t['newlyWhollyBuried']==t['newlyUpwardWhollyBuried']==0
  if u in PAIRS:
   c=contexts[u];assert c['nativeUid']==u and c['supportUid']==PAIRS[u]
   assert c['proposalTerrainNonRegressionProved']is True and c['existingNativeReaccepted']is False and c['rawSupportPolicyPassed']is False
   assert c['rawNativeRegression']==raw and len(c['rows'])==2 and {r['uid']for r in c['rows']}=={u,PAIRS[u]}
   assert t['maximumBurialIncrease']==0 and t['minimumGapAfter']==t['minimumGapBefore']
   assert t['whollyBuriedAfter']==t['whollyBuriedBefore'] and t['upwardWhollyBuriedAfter']==t['upwardWhollyBuriedBefore']
   for proof in c['rows']:
    assert proof['sourceSHA256']==current[proof['uid']]['sha256']
    assert proof['exactRenderedTerrainMultisetUnchanged']is True and proof['rootCoarseMaskUnchangedAcrossCompleteBounds']is True
  result.append(dict(uid=u,passed=True,terrain=deepcopy(t),reviewScope='proposal-terrain-nonregression-only',rawMeshAndSupportReview=deepcopy(raw),existingSupportReapproved=False,existingSourceReapproved=False))
 return result

def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(suffix):
  batch=P+suffix+'-20261027';pins[batch]=authenticate(base/batch)[1];path=base/batch/'summary.json'
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.extend([base/batch/'result.json',path]);return read(path)
 physical=take('physical-source-review-v1');visual=take('visual-qualification-v1');surface=take('three-member-surface-v2')
 assert physical['physicalAcceptance'] and visual['visualAcceptance']
 assert physical['sourceSHA256ByUid']==visual['sourceSHA256ByUid']==surface['sourceSHA256ByUid']==SOURCES
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==surface['currentManifest']['sha256']==visual['currentManifestSHA256'];refs.append(manifest)
 current={}
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for row in read(path)['models']:
   assert row['uid']not in current;current[row['uid']]=row
 assert len(current)==6989 and not set(SOURCES)&set(current)
 neighbours=take('three-member-neighbours-v2');contexts={u:take('retained-'+u.split('/')[1].replace(':','-')+'-context-v2')for u in PAIRS}
 checks=out/'full-mesh-terrain-checks.json';save(checks,dict(rows=terrain_rows(neighbours,contexts,current),aiCalls=0,modelGeometryChanges=0,reviewScope='proposal-terrain-nonregression-only',originalCombinedSupportNegatives=sorted(PAIRS),existingNativeReaccepted=False))
 reviews=[]
 for m in surface['members']:
  candidate=ROOT/m['candidate']['path'];old=ROOT/'3d-viewer'/m['replaces']['url'];refs.extend([candidate,old])
  assert digest(candidate.read_bytes())==m['candidate']['sha256'] and digest(old.read_bytes())==m['replaces']['sha256']
  assert set(m['replaces']['retainedUids'])<=set(neighbours['requiredNativeUids'])
  path=out/(m['member']+'-native-review.json')
  save(path,dict(status='approved-for-integration',supersededURL=m['replaces']['url'],supersededSHA256=m['replaces']['sha256'],replacementSHA256=m['candidate']['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=m['replaces']['retainedUids'],replacementTargetUids=read(candidate)['meta']['targetUids'],fullMeshCheck=dict(path=str(checks.relative_to(ROOT)),sha256=digest(checks.read_bytes())),reviewScope='proposal-terrain-nonregression-only',existingNativeReaccepted=False))
  reviews.append(dict(member=m['member'],path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
 summary=dict(uids=sorted(SOURCES),retainedNativeActors=67,basicForms=786,members=reviews,rawSupportNegativesPreserved=sorted(PAIRS),existingNativeReaccepted=False,proposalTerrainNonRegressionPassed=True,sourceSHA256ByUid=SOURCES,installationApproved=False,publication=False)
 save(out/'summary.json',summary)
 module('north_retained_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-three-member-retained-terrain-only-review',refs,summary)
if __name__=='__main__':main()
