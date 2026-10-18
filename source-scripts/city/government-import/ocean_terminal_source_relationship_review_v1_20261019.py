"""Review exact original model/TIN relationship; no source changes or installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-source-relationship-review-v1-20261019';DOC=BASE/BATCH
UID='landsd/205767:0';SHA='2fbf7665466f9cd015b00d263913002e3de6dc268d9c590f9815853d182eea89'
def folder(name):return BASE/('government-xl-ocean-terminal-'+name+'-20261019')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['source-views-v1','low-rim-views-v2','low-rim-ground-attribution-v1','original-ground-attribution-v1','four-mode-foundations-v1','identity-review-v1','retained-sampler-v1']:
   p=folder(name)/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rim=read(folder('low-rim-ground-attribution-v1')/'attribution.json');burial=read(folder('original-ground-attribution-v1')/'attribution.json');low=read(folder('low-rim-views-v2')/'low-rim.json');identity=read(folder('identity-review-v1')/'205767:0-review.json')
 assert rim['summary']['sourceSHA256']==burial['summary']['sourceSHA256']==low['sourceSHA256']==identity['sourceSHA256']==SHA
 assert identity['identityOnlyApproved'];assert rim['summary']['flaggedFacesCompared']==len(low['sourceFaceIds'])==106
 assert [f['faceId']for f in rim['faces']]==low['sourceFaceIds'];assert rim['summary']['maximumTerrainDifferenceMetres']==0
 assert burial['summary']['originalTerrainFullyBuriedIds']==burial['summary']['candidateFullyBuriedIds']==[27545,27546,27547,27548]
 assert burial['summary']['maximumTerrainDifferenceMetres']<2e-7
 modes=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  f=read(folder('four-mode-foundations-v1')/('205767:0-'+mode+'.json'));assert f['sourceSHA256']==SHA and f['foundation']['completeTerrainTriangles']==40299
  assert not f['strictFoundationAccepted'] and f['foundation']['fullyBuriedUpwardTriangles']==0 and [x['faceId']for x in f['buriedFaces']]==[27545,27546,27547,27548]
  modes.append(dict(mode=mode,wholeWorldSHA256=f['wholeWorldSHA256'],rawStrictFoundationAccepted=False,buriedFaceIds=[27545,27546,27547,27548]))
 images=[folder('source-views-v1')/(n+'.png')for n in ['whole','whole-reverse','landward','buried-front','buried-reverse']]+[folder('low-rim-views-v2')/(n+'.png')for n in ['rim-front','rim-reverse','rim-context']]
 decision=dict(uid=UID,sourceSHA256=SHA,reviewer='Codex ROOT',sourceTerrainRelationshipReviewed=True,originalSurveyedRelationshipAccepted=True,geometryOrPoseChanges=0,aiGeometryModelling=False,rawStrictGroundContactPassed=False,rawStrictFoundationPassed=False,checks=modes,lowRimFaceIds=low['sourceFaceIds'],buriedFaceIds=[27545,27546,27547,27548],rawLowRimSummary=rim['summary'],rawBurialSummary=burial['summary'],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],basis=[
 'The complete unchanged government source and its adjoining government TIN use the same surveyed coordinate frame. Exact identity is separately reviewed; source geometry, scale and pose remain immutable.',
 'All106 low-rim faces lie at the circular landward access structure and its outer support assembly. Their source-to-terrain offsets are exactly reproduced by the candidate. This review accepts preservation of that supplied relationship, not a claim that every lowest vertex physically touches terrain.',
 'Four downward source faces at the escalator-base underside remain buried in the original TIN and the candidate. Every full40299-face arithmetic mode identifies exactly these four faces and no upward buried face. No source face is removed or moved.',
 'The full model contains237 candidate vertices within0.1m of terrain. These are evidence against treating the global minimum as a complete support census; they are not engineering load paths or independent structural certification.',
 'Render overlays ignore depth and serve face-location attribution only. The front source view shows the escalator, the reverse low-rim view shows the circular structure/support assembly; occluded regions are not invented. V1 low-rim caption was reused incorrectly; corrected V2 exports are the reviewed low-rim evidence.',
 'This is a source-specific original-representation decision. Preserve numerical failures and require current terrain routing, neighbour, collision, staged/live visual and publication checks. Do not generalise a clearance waiver to other sources.'
 ],installationApproved=False,publicationApproved=False,stagedAndLiveReviewRequired=True)
 save(DOC/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json',decision);refs.extend(images)
 module('ocean_relationship_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-original-surveyed-relationship-review',list(dict.fromkeys(refs)),dict(uids=[UID],originalSurveyedRelationshipAccepted=True,rawStrictGroundContactPassed=False,rawStrictFoundationPassed=False,installationApproved=False))
if __name__=='__main__':main()
