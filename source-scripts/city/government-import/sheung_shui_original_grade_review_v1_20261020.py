"""Bounded original stair/panel grade interpretation; no publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-original-grade-review-v1-20261020';DOC=BASE/BATCH
UID='landsd/56054:0';SHA='76ee08f0c71b97728e943666840654123f2efa7856b66bec551eed15496b8867'
def folder(name):return BASE/('government-xl-sheung-shui-'+name+'-20261020')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 names=['identity-review-v1','candidate-runtime-v2','four-mode-foundations-v1','candidate-grade-context-v2','float32-grade-context-v1','current-original-grade-comparison-v1','whole-components-v1','crossing-observations-v1','isolated-groups-v1','neighbours-v2','loader-v1']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in names:
   d=folder(name);r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 groups=read(folder('whole-components-v1')/'groups.json')['groups'];assert len(groups)==10
 ids=sorted(i for g in groups for i in g['flaggedSourceFaceIds']);assert len(ids)==len(set(ids))==68
 assert all(g['maximumObservedGapM']>0 for g in groups)
 bindings=[];differences=[]
 for mode,fmode in [('original','original'),('runtime','literal'),('left','explicitLeftF32'),('balanced','explicitBalancedF32')]:
  g=read(folder('float32-grade-context-v1'if mode in ['left','balanced']else 'candidate-grade-context-v2')/('56054:0-'+mode+'.json.gz'))
  c=read(folder('current-original-grade-comparison-v1')/(mode+'.json.gz'));f=read(folder('four-mode-foundations-v1')/('56054:0-'+fmode+'.json'))
  assert g['sourceSHA256']==c['sourceSHA256']==f['sourceSHA256']==SHA
  assert g['completeWorldSHA256']==c['wholeWorldSHA256']==f['wholeWorldSHA256']
  assert g['wholeSourceFaces']==c['wholeSourceFaces']==f['foundation']['completeTerrainTriangles']==19911
  assert sorted(g['continuousNegativeFaceIds'])==ids and not g['negativeUpwardFaceIds']and not g['uncoveredFaces']
  assert len(g['negativeWithoutExposedWitness'])==8
  assert c['allOriginalCovered']and c['maximumMinimumGapDifferenceM']<.00001
  assert all(d['originalTerrain']['minimum']['minimumGapM']<-.5 for d in c['details'])
  assert f['strictFoundationAccepted']and f['foundation']['fullyBuriedTriangles']==0 and f['foundation']['fullyBuriedUpwardTriangles']==0
  bindings.append(dict(mode=fmode,sourceSHA256=SHA,wholeWorldSHA256=f['wholeWorldSHA256'],completeFaces=19911,completeDrawnGroundSHA256=g['completeDrawnGroundSHA256']))
  differences.append(dict(mode=mode,details=[dict(faceId=d['faceId'],differenceM=d['minimumGapDifferenceM'],originalMaximumGapM=d['originalTerrain']['maximumObservedGapM'],candidateMaximumGapM=d['candidateTerrain']['maximumObservedGapM'])for d in c['details']]))
 identity=read(folder('identity-review-v1')/'56054:0-review.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==SHA
 metrics=read(folder('candidate-runtime-v2')/'metrics.json');metric=metrics['rows'][0]
 policy=module('sheung_shui_raw_policy',HERE/'acceptance-policy.py');raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=identity['identityProof']),metric,metrics['profiles']['mobile']);assert raw==['terrain-intersects-source-over-0.5m'],raw
 images=[folder('isolated-groups-v1')/('group-'+str(i)+'-terrain.png')for i in range(1,11)]
 review=dict(uids=[UID],reviewer='Codex ROOT',sourceSHA256=SHA,sourceSpecificGradeInterpretationAccepted=True,sourceFaces=ids,sourceBindings=bindings,sourceCurrentDepthDifferences=differences,imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],rawPolicyReasons=raw,rawNumericMetrics=metric,strictTerrainIntersectionCheckPassed=False,observations=[
 'Previously inspected exact source groups1,3,5,7,8 are exterior stairs with lowest terminal edges entering authentic terrain;2,4,6,9,10 are tall panels whose bases enter terrain. Group IDs bind all68 flagged faces; group membership is not a new structural-support requirement.',
 'All19911faces are covered in original, literal and both explicit Float32 arithmetic modes. No negative upward-facing triangle and no fully buried triangle under the existing foundation contract occurs. Eight flagged faces have no exposed witness above zero: these are retained explicitly, not described as exposed; they belong to the inspected exposed assemblies.',
 'All68candidate crossing faces also cross authentic original government terrain by over0.5m. Maximum signed-minimum difference magnitude is less than0.00001m in each mode. This establishes that the proposed ground preserves the authored local base-crossing configuration to the recorded arithmetic accuracy; exact terrain equality is not claimed.',
 'Accept only these original base terminations in these exact source/world/ground bindings. The strict numeric terrain-intersection gate remains failed; no general tolerance is changed. This review does not authorise new buried floors, source movement, or geometry editing.',
 'The candidate terrain has independent constructor and neighbour evidence; identity has its own approval. Final composition, collision, fallback and staged/live browser acceptance remain separate. No adjacent basic structure suppression or publication is approved.'
 ],modelGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
 save(DOC/'ROOT-GRADE-REVIEW.json',review)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(HERE/'acceptance-policy.py')
 module('sheung_shui_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'sheung-shui-exact-original-stair-panel-grade-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
