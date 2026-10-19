"""Source-specific IFC column/grade interpretation; runtime publication remains separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ifc-mall-original-column-review-v2-20261019';DOC=BASE/BATCH
UID='landsd/64856:0';SHA='d0cf990103d9c85bd3adc101d015de2eeed97314cfaaed14b88e0dd8d87c7b5f'
def folder(name):return BASE/('government-xl-ifc-mall-'+name+'-20261019')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 names=['identity-review-v1','unchanged-ground-v1','unchanged-four-mode-foundations-v1','unchanged-full-grade-context-v1','current-original-grade-comparison-v1','grade-views-v1']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   d=folder(name);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 ids=list(range(6121,6168))+[26239];bindings=[]
 for mode,fmode in [('original','original'),('literal','literal'),('left','explicitLeftF32'),('balanced','explicitBalancedF32')]:
  g=read(folder('unchanged-full-grade-context-v1')/('64856:0-'+mode+'.json.gz'));cmp=read(folder('current-original-grade-comparison-v1')/(mode+'.json.gz'));f=read(folder('unchanged-four-mode-foundations-v1')/('64856:0-'+fmode+'.json'))
  assert g['sourceSHA256']==cmp['sourceSHA256']==f['sourceSHA256']==SHA
  assert g['wholeSourceFaces']==cmp['wholeSourceFaces']==f['foundation']['completeTerrainTriangles']==36305
  assert g['continuousNegativeFaceIds']==ids and not g['negativeUpwardFaceIds'] and not g['negativeWithoutExposedWitness'] and not g['uncoveredFaces']
  assert cmp['allVertical']and cmp['allOriginalCovered']and cmp['allOriginalHaveExposedWitness']and cmp['failedFaces']==48
  assert cmp['maximumMinimumGapDifferenceM']<.031875
  assert all(d['originalTerrain']['minimum']['minimumGapM']<-.5 and d['originalTerrain']['maximumObservedGapM']>0 for d in cmp['details']), 'Every flagged current face must already cross original terrain and remain exposed'
  assert len([d for d in cmp['details']if d['minimumGapDifferenceM']<0])==15
  assert cmp['wholeWorldSHA256']==g['completeWorldSHA256']==f['wholeWorldSHA256']
  assert f['strictFoundationAccepted'] and f['foundation']['fullyBuriedTriangles']==0
  bindings.append(dict(mode=fmode,sourceSHA256=SHA,wholeWorldSHA256=f['wholeWorldSHA256'],completeFaces=36305))
 details=read(folder('current-original-grade-comparison-v1')/'original.json.gz')['details'];vertices=[set(map(tuple,d['triangle']))for d in details];seen=set();todo=[0]
 while todo:
  i=todo.pop()
  if i in seen:continue
  seen.add(i);todo.extend(j for j,v in enumerate(vertices)if j not in seen and len(v&vertices[i])>=2)
 assert len(seen)==48
 metrics=read(folder('unchanged-ground-v1')/'metrics.json');metric=metrics['rows'][0];identity=read(folder('identity-review-v1')/'64856:0-review.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==SHA
 assert not read(folder('unchanged-ground-v1')/'terrain-candidates.json')
 assert metric['sourcePreserved']and metric['missingTerrain']==0 and metric['maxSamplerDelta']<.004
 policy=module('ifc_raw_policy',HERE/'acceptance-policy.py');raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=identity['identityProof']),metric,metrics['profiles']['mobile']);assert raw==['terrain-intersects-source-over-0.5m'],raw
 images=[folder('grade-views-v1')/(n+'.png')for n in ['grade-side','grade-reverse']]
 review=dict(uids=[UID],reviewer='Codex ROOT',sourceSHA256=SHA,sourceSpecificGradeInterpretationAccepted=True,sourceFaces=ids,sourceBindings=bindings,oneExactSharedEdgeComponent=True,sourceCurrentDepthDifferences=[dict(faceId=d['faceId'],differenceM=d['minimumGapDifferenceM'])for d in details],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],rawPolicyReasons=raw,rawNumericMetrics=metric,strictTerrainIntersectionCheckPassed=False,observations=[
 'ROOT inspected both marker-free exports. The side view exposes the highlighted round vertical column beneath the source side extension; the reverse view is occluded and is not independent proof of its shape. Numeric exact shared-edge analysis binds all48faces, including26239, into this one column surface.',
 'The complete36305face analysis in all4coordinate modes finds precisely48negative verticalfaces, no negative upwardface, no wholly buriedface, no missingterrain, and exposed portions on every flaggedface.',
 'Every one of these48faces already crosses authentic government terrain by more than0.5m and has an exposed portion there. Current terrain differs:15faces are up to0.025415864m deeper and33are shallower by up to0.031874037m. These signed differences are retained explicitly; current terrain is not claimed identical or uniformly shallower. The review identifies the same exact original vertical column termination, with no newly buried floor or wholly buried face, rather than accepting a numeric tolerance increase.',
 'The raw0.5m terrain-intersection check remains failed. This source-specific review covers only these48faces and exact source/world/currentterrain bindings. It is not a generic tolerance increase.',
 'The V1 draft failed an incorrect uniformly-shallower assertion and never approved placement. This corrected source-role review relies on exact common crossing-face identity, the visible column, and exposed original/current portions; signed minima remain recorded.',
 'No terrain replacement is proposed. Legacy tower strict-support failures are preserved and not relabelled. Final loader, collision, picking, fallback and staged/live browser validation remain required.'
 ],modelGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
 save(DOC/'ROOT-GRADE-REVIEW.json',review)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(HERE/'acceptance-policy.py')
 module('ifc_column_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ifc-exact-original-column-grade-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
