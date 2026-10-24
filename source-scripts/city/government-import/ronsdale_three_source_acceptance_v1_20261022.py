"""Bind complete current source, support and retained-neighbour evidence for Ronsdale."""
from pathlib import Path
import json,numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-three-source-acceptance-v1-20261022';DOC=BASE/BATCH
POD='landsd/233771:0';TOWERS=['landsd/256898:0','landsd/256702:0']
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def doc(n,f):return take(n,BASE/n/f)
 n='government-xl-ronsdale-three-source-runtime-v1-20261022';selection=doc(n,'selection.json.gz');metrics=doc(n,'metrics.json');runtime=take(n,HERE/'local'/n/'runtime-geometry.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert set(sources)==set(TOWERS+[POD]);geometry={r['uid']:r for r in runtime['rows']}
 for r in metrics['rows']:assert r['sourceSHA256']==sources[r['uid']] and not r.get('error') and r['missingTerrain']==0 and r['maxSamplerDelta']<=.004
 binding=doc('government-xl-ronsdale-three-world-binding-v1-20261022','binding.json');assert binding['allFourArraysIdentical'];world={r['uid']:r['worldSHA256ByMode']['literal']for r in binding['rows']}
 identities={TOWERS[0]:doc('government-xl-ronsdale-tower1-identity-review-v1-20261022','identity.json'),TOWERS[1]:doc('government-xl-remaining-forty-original-identity-v2-20261021','256702:0/identity.json'),POD:doc('government-xl-remaining-forty-podium-identity-v1-20261021','233771:0/identity.json')}
 for u,i in identities.items():assert i['passed'] and not i['reasons'] and i['sourceSHA256']==sources[u]
 assert all(sources[u]==h for u,h in identities[TOWERS[0]]['requiredSourceSHA256ByUid'].items())
 n='government-xl-ronsdale-three-source-support-v1-20261022';raw=doc(n,'support-checks.json.gz');foundations=doc(n,'summary.json')['rows'];accounts=[]
 names={TOWERS[0]:'government-xl-ronsdale-tower1-contact-attribution-v1-20261022',TOWERS[1]:'government-xl-ronsdale-tower2-contact-attribution-v2-20261022'}
 def witnesses(rows,key=None):return sorted(json.dumps(r[key]if key else r,sort_keys=True)for r in rows)
 for u in TOWERS:
  f=next(r['foundation']for r in foundations if r['uid']==u);assert f['completeTerrainTriangles']==f['triangles'] and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
  r=next(r for r in raw['rows']if r['uid']==u);proof=r['interface'];assert r['sourceSHA256']==sources[u] and r['supportSHA256']==sources[POD] and proof['wallIntersections']==0
  contacts=doc(names[u],'contacts.json.gz');assert contacts['sourceWorldSHA256']==world[u] and contacts['supportWorldSHA256']==world[POD];assert witnesses(contacts['targets'],'witness')==witnesses(proof['unresolved'])
  assert all(t['positiveContacts']and all(c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in t['positiveContacts'])for t in contacts['targets'])
  assert proof['strictContacts']+len(contacts['targets'])==proof['samples']
  accounts.append(dict(uid=u,samples=proof['samples'],strictContacts=proof['strictContacts'],finiteIncidentContacts=len(contacts['targets']),remainingUninterpretedWarnings=0,wholeFoundationFaces=f['triangles'],coordinateRepresentations=['original','literal','explicitLeftF32','explicitBalancedF32']))
 n='government-xl-ronsdale-inset-runtime-v2-20261022';old=take(n,HERE/'local'/n/'runtime-geometry.json.gz')['rows'][0];assert old['uid']==POD and np.array_equal(old['drawnGroundGeometry'],geometry[POD]['drawnGroundGeometry'])
 podiumReview=doc('government-xl-ronsdale-physical-review-v2-20261022','ROOT-PHYSICAL-REVIEW.json');assert podiumReview['sourceSpecificPhysicalInterpretationAccepted'] and podiumReview['sourceSHA256ByUid']=={POD:sources[POD]}
 forms=doc('government-xl-ronsdale-form-regression-v2-20261022','neighbour-checks.json');assert len(forms['rows'])==22;flagged={r['uid'] for r in forms['rows']if r['reasons']};assert flagged==set(TOWERS+['landsd/256900:0','landsd/307560:0'])
 basic=doc('government-xl-ronsdale-basic-support-v1-20261022','summary.json');small=next(r for r in basic['rows']if r['uid']=='landsd/256900:0');assert small['supportPassed'] and not small['unresolved'] and small['foundation']['fullyBuriedTriangles']==0
 n='government-xl-ronsdale-canopy-estimate-private-v1-20261022';canopy=doc(n,'summary.json');assert canopy['productionChanges']==canopy['governmentGeometryChanges']==0 and canopy['privateEstimatedBaseChanges']==1
 c=canopy['rows'][0];assert c['uid']=='landsd/307560:0' and c['supportPassed'] and c['strictContacts']==c['samples']==8 and c['completeFoundationFaces']==c['faces'] and c['buried']==c['upwardBuried']==0
 estimate=doc(n,'estimated-bases.json');assert len(estimate['buildings'])==1;assert estimate['buildings'][0]['baseSource']=='terrain-estimated' and estimate['buildings'][0]['surveyBase']is None and estimate['buildings'][0]['surveyTop']is None
 scope=doc('government-xl-ronsdale-regional-scope-v1-20261022','scope.json');assert scope['intersectingForms']==22 and not scope['touchingNativeUids'] and not scope['overlappingPatches'] and not scope['touchingPatchBoundaries']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,accounts=accounts,allFourWorldArraysIdentical=True,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,rawCanonicalFailuresPreserved=True,requiredEstimatedBaseUpdates=estimate['buildings'],requiredOriginalAssembly=sorted(sources),ordinaryNeighbourForms=22,retainedNativeNeighbours=0,publicationApproved=False,installationApproved=False,visualAcceptance=False,sourceGeometryChanges=0,sourcePoseChanges=0,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),qualification='Both exact original towers and podium must be installed together with the separately guarded unsurveyed canopy base estimate. Every complete source foundation is clear; all raw tower contacts have strict or exact positive finite contacts. Full four-coordinate arrays are identical and fresh warning sets are bound exactly. The podium-specific original wall-ground review remains scoped. All22forms accounted for: replaced towers use their complete original proofs; small retained tower strict support passes; private unsurveyed canopy correction strict support/foundation passes. Loader, staged/live visual/picking/collision/failure recovery, full-neighbour publication rebinding and guarded installation remain required.')
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',result);module('ronsdale_three_acceptance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-three-source-and-neighbour-interpretation',refs,result);print(dict(models=3,towerWarningsExplained=sum(r['finiteIncidentContacts']for r in accounts),ordinaryForms=22,installationApproved=False),flush=True)
if __name__=='__main__':main()
