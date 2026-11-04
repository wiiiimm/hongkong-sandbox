"""Source identity only: preserve the complete original terminal end extension."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-identity-review-v1-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-kai-tak-cruise-extent-views-v1-20261019';WHOLE=BASE/'government-xl-remaining-three-source-views-v2-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [SRC,WHOLE]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 p=read(SRC/'identity.json');e=read(SRC/'extent.json');assert p['uid']=='landsd/263423:0'and p['sourceSHA256']=='44839b47ec51db17f72eca474516b1f7a960476f4426990e180c7f8dafe3e341'
 assert p['originalOwnership']['sourceGraphVerified']and p['exactCurrentComponentRoute']['qualified']and p['exactWholeCellCoverage']['covered']and p['geographicCell']['targetCoversWholeCell']
 projection=p['originalOwnership']['fullProjection'];assert projection['exactObjectAndCSUID']and projection['targetCoveredBySourceProjection']>.998
 assert set(p['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
 assert len(e['faceIds'])==27 and 15.25<e['maximumDistanceM']<15.251 and e['sourceSHA256']==p['sourceSHA256']and e['wholeWorldSHA256']==p['worldTrianglesSHA256']
 assert all(r['sameParent']and r['sharedOsmReference']for r in projection['intersectingForms'])
 images=[SRC/(n+'.png')for n in ['whole','extent-front','extent-reverse']]+[WHOLE/('263423-0-'+n+'.png')for n in ['whole','reverse']]
 decision=dict(uid=p['uid'],sourceSHA256=p['sourceSHA256'],sourceFormSHA256=p['sourceFormSHA256'],worldTrianglesSHA256=p['worldTrianglesSHA256'],reviewer='Codex ROOT',identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=p,rawReasonsRetained=p['reasons'],reviewedExtentFaceIds=e['faceIds'],imagesActuallyInspected=[dict(path=str(q.relative_to(ROOT)),sha256=digest(q.read_bytes()))for q in images],reviewBasis=['Exact government object/CSUID, unchanged source graph, current component route and complete GeoRef cell bind this source to the cruise terminal. More than99.8percent of the target footprint is covered.','All intersected forms in the fresh source projection share the same parent and OSM reference. This establishes compound identity context, not permission to suppress other components.','ROOT inspected five exported views. The27 outlying faces are the small narrow extension attached to the terminal end structure, not a detached neighbouring building. The reverse closeup shows its connection to the adjoining end structure. Preserve all original faces.','The overlay highlights complete faces through occlusion; it does not establish collision clearance. No neighbour suppression or numeric threshold change is authorized by this identity-only decision.'],installationApproved=False,publicationApproved=False,physicalAcceptancePending=True,modelGeometryChanges=0)
 save(DOC/'263423:0-review.json',decision);refs.extend(images+[SRC/'identity.json',SRC/'extent.json'])
 module('kai_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-original-identity-review',list(dict.fromkeys(refs)),dict(uids=[p['uid']],identityOnlyApproved=True,installationApproved=False))
if __name__=='__main__':main()
