"""Bind unchanged stadium sources to canonical physical checks and scoped identity review."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-physical-review-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(batch,name):
 p=BASE/batch/name;_,ps=authenticate(BASE/batch);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/batch/'result.json',p]);return read(p)
rn='government-xl-mongkok-inset-pair-runtime-v1-20261021';selection=take(rn,'selection.json.gz');metrics=take(rn,'after-metrics.json');sources={r['uid']:r['sourceSHA256']for r in selection['rows']}
for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
identity=take('government-xl-mongkok-source-identity-review-v1-20261021','ROOT-IDENTITY-REVIEW.json');assert identity['identityAccepted'] and identity['sourceSpecificIdentityReviewAccepted'] and identity['sourceSHA256']==sources['landsd/240332:0']
foundations=take('government-xl-mongkok-four-world-foundations-v1-20261021','summary.json');assert foundations['allFourWorldFoundationsPassed'] and len(foundations['rows'])==8
loader=take('government-xl-mongkok-loader-v1-20261021','validation.json');assert loader['loaderAccepted']==loader['checksPassed']==2 and loader['exceptions']==0
terrain=take('government-xl-mongkok-local-inset-v4-20261021','summary.json');assert terrain['terrainValidationPassed']
forms=take('government-xl-mongkok-form-regression-v1-20261021','summary.json');assert forms['forms']==66 and not forms['flagged'] and forms['ordinaryFlagged']==0
manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
policy=module('stadium_canonical_policy',HERE/'acceptance-policy.py');results=[]
for row in selection['rows']:
 uid=row['uid'];entry=row['candidate']['entry'];form=row['source']['building'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
 assert entry['objectId']==form['objectId'] and entry['buildingCSUID']==form['buildingCSUID'] and entry['uid']==form['uid']==uid
 matches=[b for b in read(tile)['buildings']if b['uid']==uid];assert matches==[form]
 if uid=='landsd/240332:0':assert identity['sourceFormTileSHA256']==row['source']['tileSHA256']
 else:
  found=[]
  for url in m['officialModelCatalogues']:
   cp=ROOT/'3d-viewer'/url
   for e in read(cp)['models']:
    if e['uid']==uid:found.append(e);refs.append(cp)
  assert found==[entry] and entry['identityReviewApproved'] is True and entry['publicationApproved'] is True
 proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
 metric=next(r for r in metrics['rows']if r['uid']==uid);reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=proof),metric,metrics['profiles']['mobile']);assert reasons==[],(uid,reasons)
 f=take('government-xl-mongkok-four-world-foundations-v1-20261021',uid.split('/')[1]+'-literal.json');f.update(sourceSHA256=sources[uid],strictFoundationAccepted=True)
 resolution=resolve_global_bottom_warning(next(r for r in loader['results']if r['uid']==uid),metric,f);assert resolution['resolved']==['sampled-terrain-above-model-bottom'] and not resolution['remaining']
 results.append(dict(uid=uid,canonicalReasons=reasons,identityProof=proof,globalBottomWarningResolution=resolution))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,canonicalChecks=results,rawIdentityReasons=identity['rawIdentityReasons'],rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False,qualification='Both unchanged stadium originals pass canonical contact, coverage, sampler and mobile asset budgets. Eight complete foundations contain no buried triangles; all66 neighbouring forms pass. New stand identity relies on the exact scoped source review, with raw extent flags retained. Existing opposite stand retains its current accepted identity and unchanged catalogue entry. Browser visual acceptance and guarded publication remain required.')
save(DOC/'ROOT-PHYSICAL-REVIEW.json',review);refs.extend([HERE/'acceptance-policy.py',HERE/'terrain_diagnostic_resolution.py']);module('stadium_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'canonical-original-stadium-physical-review',list(dict.fromkeys(refs)),review)
