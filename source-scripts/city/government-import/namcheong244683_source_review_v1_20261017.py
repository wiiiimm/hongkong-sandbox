"""Review exact original walkway, grade walls and existing interfaces; no geometry edits."""
from pathlib import Path
import shutil,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-namcheong244683-source-review-v1-20261017';DOC=BASE/BATCH;UID='landsd/244683:0';SHA='5716298309776020bd7fb92cdc609dada531dbc0b45e326b15ad2c08e5f599ff'
def folder(n):return BASE/('government-xl-namcheong244683-'+n+'-20261017')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__),HERE/'acceptance-policy.py']
 names=['current-capture-v1','current-identity-runtime-v1','private-browser-v1','private-browser-v2','neighbour-contacts-v1','baseline-contacts-v1','interface-views-v1','authoritative-identity-v1','provider-extent-context-v1','assembly-four-world-v1','grade-face-context-v2','assembly-four-foundations-v1']
 for name in names:
  d=folder(name);r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']] == e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(folder('current-capture-v1')/'selection.json.gz')['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SHA
 raw=read(folder('authoritative-identity-v1')/'identity.json')['proof'];assert raw['originalOwnership']['sourceGraphVerified']and raw['exactWholeCellCoverage']['covered']and raw['sourceSHA256']==SHA
 expected=['exact-officialCandidates','exact-officialMatches','fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','fresh-exact-component-route-not-unique-or-differs','full-source-maximum-extent','full-source-unrelated-overlap','unique-viewerMatches'];assert raw['reasons']==expected
 provider=read(folder('provider-extent-context-v1')/'context.json');assert all(provider['stableFields'].values())and provider['providerObjectId']==244476 and provider['viewerObjectId']==244683 and provider['footprintHausdorffM']<.001 and len(provider['extentFaces'])==1439
 identity=read(folder('current-identity-runtime-v1')/'identity-context.json');assert identity['exactObjectAndCSUID']and identity['targetCoveredBySourceProjection']>.999 and identity['sourceExcessCoveredByUnrelatedFormsM2']<5.521
 worlds=read(folder('assembly-four-world-v1')/'world-triangles.json.gz');assert set(worlds)=={'original','literal','left','balanced'};grade=[];faceids=None
 for mode in sorted(worlds):
  d=read(folder('grade-face-context-v2')/('244683:0-'+mode+'.json.gz'));tri=np.asarray(worlds[mode][UID],dtype='<f8');assert len(tri)==20645 and digest(tri.tobytes())==d['completeWorldSHA256'];assert not d['uncoveredFaces']and not d['negativeUpwardFaceIds']and not d['negativeWithoutExposedWitness'];ids=d['continuousNegativeFaceIds'];assert len(ids)==52
  if faceids is None:faceids=ids
  else:assert faceids==ids
  assert all(abs(d['faces'][i]['normalYRatio'])<.005 and d['faces'][i]['maximumObservedGapM']>0 for i in ids)
  grade.append(dict(mode=mode,completeWorldSHA256=d['completeWorldSHA256'],sourceFaceIds=ids))
 f=read(folder('assembly-four-foundations-v1')/'summary.json');assert f['allModesPassed']and len(f['rows'])==4
 v=read(folder('current-identity-runtime-v1')/'validation.json');assert v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0 and not v['concerns']
 for name in ['private-browser-v1','private-browser-v2']:
  b=read(folder(name)/'staged-browser.json');assert b['passed']and not b['errors'];refs.append(folder(name)/'ROOT-IMAGE-INSPECTION.json')
 baseline=read(folder('baseline-contacts-v1')/'summary.json')['rows'];assert len(baseline)==4 and all(r['existingInterfacePresent']for r in baseline);assert {r['uid']:r['originalContacts']for r in baseline}=={'landsd/108916:0':25,'landsd/146595:0':10,'landsd/233291:0':53,'landsd/271037:0':0}
 metrics=read(folder('current-capture-v1')/'metrics.json');policy=module('nam_review_policy',HERE/'acceptance-policy.py');rawreasons=policy.reasons(dict(row,state='runtime-validated-awaiting-acceptance'),metrics['rows'][0],metrics['profiles']['mobile']);assert rawreasons==['terrain-intersects-source-over-0.5m','strict-identity-fit']
 DOC.mkdir();shutil.copyfile('/tmp/namcheong-original-extent.png',DOC/'original-walkway-extent.png');images=[DOC/'original-walkway-extent.png',folder('provider-extent-context-v1')/'extent-plan.png',*folder('interface-views-v1').glob('*.png'),*folder('private-browser-v2').glob('base-context-*.png'),*folder('private-browser-v1').glob('*.png')];assert len(images)==12
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 decision=dict(uid=UID,sourceSHA256=SHA,reviewer='Codex ROOT',originalSourceReviewAccepted=True,identityAccepted=True,placementAccepted=True,rawPolicyReasons=rawreasons,rawIdentityReasons=expected,sourceSpecificResolutions=['stable-provider-record-continuity-without-viewer-ID-rewrite','authored-original-low-walkway-extent','original-lower-wall-grade-intersections'],gradeEvidence=grade,policyReasons=[],inspectedImages=[ref(p)for p in images],observations=['Unique active provider record retains exact stable CSUID, BuildingID, type, date, GeoRef and heights; current OBJECTID244476 differs from historical viewer244683. Footprints differ by less than0.001m. The missing explicit viewerMatches in the fresh converter call is not proof of a second source; current catalogue form and exact stable record identify this source. No viewer/provider ID rewritten.','Original graph ownership and complete GeoRef-cell coverage pass. The1439 faces outside10m are an authored roofed walkway with columns, seen in the isolated original-face rendering at y6.348..10.344m. The main carpark retains >99.9% target coverage. This named original component explains the18.908m extent; no geometry cut, invented replacement, or global threshold widening.','All52 terrain-warning faces are near-vertical lower walls retaining exposed portions in every captured mode. No affected upward face, uncovered face or wholly buried foundation. Close west/south views show lower walls meeting the slope.','Existing four BASIC neighbours already interact with this podium. Exact source contact counts25/10/53/0 and all changed height ranges remain recorded. Two inspected interface views locate interactions at the Fu Yee tower corner above podium level and the shopping-centre elevated connection/supports. These are retained original/fallback interfaces, not evidence to suppress neighbours or invent support dependencies. No claim of identical intersection volume.','Whole-source desktop/mobile day/night and failed-download fallback pass. No terrain change or neighbour geometry change.'],limitations=['Source-specific original acceptance only; not optimisation approval or engineering certification.','Raw numerical diagnostics remain unchanged. Explicit coordinate calculations are not a guarantee for every GPU.'],sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,newlyInstalled=0)
 save(DOC/'ROOT-SOURCE-REVIEW.json',decision);refs.extend([*[ROOT/p for p in pins],*images]);out=module('nam_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong-exact-original-source-acceptance-review-v1',refs,dict(uids=[UID],originalSourceReviewAccepted=True,rawPolicyReasons=rawreasons,publication=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
