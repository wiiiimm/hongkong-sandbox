"""Bounded unchanged government terminal/TIN review; no publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-source-relationship-review-v1-20261019';DOC=BASE/BATCH;UID='landsd/263423:0';SHA='44839b47ec51db17f72eca474516b1f7a960476f4426990e180c7f8dafe3e341'
def folder(n):return BASE/('government-xl-kai-tak-cruise-'+n+'-20261019')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in ['all-contact-ground-attribution-v1','low-rim-views-v1','contact-faces-v1','four-mode-foundations-v1','identity-review-v1']:
   r=read(folder(n)/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder(n)/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 attribution=read(folder('all-contact-ground-attribution-v1')/'attribution.json');faces=read(folder('contact-faces-v1')/'faces.json');identity=read(folder('identity-review-v1')/'263423:0-review.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==SHA
 ids=sorted(set(faces['lowRimFaceIds'])|set(faces['intersectingFaceIds']));assert len(ids)==143 and [f['faceId']for f in attribution['faces']]==ids and attribution['summary']['sourceSHA256']==SHA;assert attribution['summary']['maximumTerrainDifferenceMetres']<.000005;assert attribution['summary']['candidateFullyBuriedIds']==attribution['summary']['originalTerrainFullyBuriedIds']==[]
 checks=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  f=read(folder('four-mode-foundations-v1')/('263423:0-'+mode+'.json'));assert f['sourceSHA256']==SHA and f['strictFoundationAccepted']and f['foundation']['triangles']==f['foundation']['completeTerrainTriangles']==45925 and f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0;checks.append(dict(mode=mode,wholeWorldSHA256=f['wholeWorldSHA256'],foundation=f['foundation']))
 images=[folder('low-rim-views-v1')/(name+'.png')for name in ['rim-front','rim-reverse','rim-context']]+[folder('contact-faces-v1')/'contact-faces.png']
 decision=dict(uid=UID,sourceSHA256=SHA,reviewer='Codex ROOT',originalSurveyedRelationshipAccepted=True,rawStrictGroundContactPassed=False,rawStrictFoundationPassed=True,geometryOrPoseChanges=0,aiGeometryModelling=False,checks=checks,reviewedFaceIds=ids,rawContactSummary=attribution['summary'],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],basis=[
 'The immutable terminal mesh is independently bound to its exact government identity and original surveyed coordinate frame. Preserve all45925source faces at1xscale and unchanged placement.',
 'All143 faces nominated by either the global low-rim band or terrain intersection diagnostics reproduce the untouched adjoining government TIN relationship to within0.000005m. This is a measured reproduction bound, not a new contact tolerance. Raw ground-contact failures remain false.',
 'ROOT viewed all three low-rim exports and the terrain/contact diagnostic. Highlighted faces span vertical wall portions through several levels; the global minimum is not an adequate contact census. These overlays are attribution evidence, not visibility or engineering proof.',
 'Complete four-mode foundation checks cover every source face with zero wholly buried or upward buried faces.324unique source vertices lie within0.1mof candidate terrain; these are contact candidates, not certified structural load paths.',
 'Accept preservation of this exact supplied model/terrain relationship. No face is removed, warped, rescaled or translated. Current native replacement, neighbour checks, full assembly browser review and publication checks remain mandatory.'
 ],installationApproved=False,publicationApproved=False)
 save(DOC/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json',decision);refs.extend(images)
 module('kai_ground_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-original-surveyed-model-terrain-relationship-review',list(dict.fromkeys(refs)),dict(uids=[UID],originalSurveyedRelationshipAccepted=True,installationApproved=False))
if __name__=='__main__':main()
