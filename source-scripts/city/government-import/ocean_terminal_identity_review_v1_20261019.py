"""Exact source identity decision, separate from physical/publication acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-identity-review-v1-20261019';DOC=BASE/BATCH
SRC=BASE/'government-xl-ocean-terminal-landward-context-v1-20261019';WHOLE=BASE/'government-xl-ocean-terminal-source-views-v1-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,WHOLE]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 p=read(SRC/'identity.json');overlap=read(SRC/'overlaps.json');assert p['uid']=='landsd/205767:0' and p['sourceSHA256']=='2fbf7665466f9cd015b00d263913002e3de6dc268d9c590f9815853d182eea89'
 assert p['originalOwnership']['sourceGraphVerified'] and p['exactCurrentComponentRoute']['qualified'] and p['exactWholeCellCoverage']['covered'] and p['geographicCell']['targetCoversWholeCell']
 projection=p['originalOwnership']['fullProjection'];assert projection['exactObjectAndCSUID'] and projection['targetCoveredBySourceProjection']>.998
 assert set(p['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
 assert {r['uid']:len(r['sourceFaceIds'])for r in overlap['rows']}=={'landsd/215934:0':96,'landsd/231469:0':139,'landsd/234188:0':71}
 images=sorted(SRC.glob('*.png'))+[WHOLE/(n+'.png')for n in ['whole','whole-reverse','landward']];assert len(images)==9
 decision=dict(uid=p['uid'],sourceSHA256=p['sourceSHA256'],sourceFormSHA256=p['sourceFormSHA256'],worldTrianglesSHA256=p['worldTrianglesSHA256'],reviewer='Codex ROOT',identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=p,rawReasonsRetained=p['reasons'],imagesActuallyInspected=[dict(path=str(q.relative_to(ROOT)),sha256=digest(q.read_bytes()))for q in images],reviewBasis=[
 'The exact government ObjectID/CSUID, unchanged source graph, current component route and complete one-metre GeoRef cell bind the full source to Ocean Terminal. Source projection covers over99.8percent of its footprint.',
 'Whole-source and both landward directions show one long pier/terminal with circular access structure, escalator and landward edge extensions. The highlighted96/139/71-face groups lie on the landward edge and associated access/roof/wall portions of this same original source. They do not form a second hotel tower or a separate complete neighbouring building.',
 'The neighbour footprint intersections are121.423754,47.031489 and4.216755square metres respectively. Whole intersecting faces are highlighted through occlusion; the red area is not the clipped intersection area and does not establish collision clearance.',
 'These overlaps do not negate source identity. Keep the complete source and all neighbouring models. Do not delete faces, suppress neighbours, enlarge global tolerances or convert this decision into placement/publication approval.'
 ],installationApproved=False,publicationApproved=False,physicalAcceptancePending=True,modelGeometryChanges=0)
 save(DOC/'205767:0-review.json',decision)
 refs.extend(images+[SRC/'identity.json',SRC/'overlaps.json'])
 module('ocean_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-exact-original-identity-review',list(dict.fromkeys(refs)),dict(uids=[p['uid']],identityOnlyApproved=True,installationApproved=False))
if __name__=='__main__':main()
