"""Record bounded ROOT source-role interpretation; never publish or rewrite raw guards."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-oi-sin-original-boundary-review-v1-20261017';DOC=BASE/BATCH;PHYS=BASE/'government-xl-oi-sin-qualified-terrain-pair-v2-20261017';BOUND=BASE/'government-xl-oi-sin-four-world-boundary-v2-20261017';FOUND=BASE/'government-xl-oi-sin-four-world-foundations-v2-20261017';ROLE=BASE/'government-xl-oi-sin-certified-host-roles-v1-20261017';NEAR=BASE/'government-xl-oi-sin-original-interfaces-v1-20261017';EDGE=BASE/'government-xl-oi-sin-original-edges-v1-20261017'
T='landsd/256280:0';P='landsd/91128:0';EXPECTED={T:'3c20ebb504b2dd4aab88286955d418fee94dacd76c9d7315b8e5e94dbaecc014',P:'a92c4a41c69fe91f76a02f55845bdf09f845d2978f475f0ebc6741aa5778cb37'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYS,BOUND,FOUND,ROLE,NEAR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    # The earlier nearest-point packet includes historical manifest/count references.
    # Only its immutable sample output is needed here, with its exact saved hash.
    if folder==NEAR and e['path']!=str((NEAR/'nearest.json.gz').relative_to(ROOT)):continue
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(PHYS/'selection.json.gz')['rows'];assert {r['uid']:r['sourceSHA256']for r in rows}==EXPECTED
 spatial=read(PHYS/'pair-spatial.json');assert spatial['spatialBoundsPass'] and spatial['sourceSHA256ByUid']==EXPECTED
 identities={r['uid']:r for r in read(PHYS/'identity-proofs.json')['rows']};allowed={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
 for uid,r in identities.items():
  assert r['sourceSHA256']==EXPECTED[uid] and not(set(r['reasons'])-allowed)
  assert r['geographicCell']['targetCoversWholeCell'] and r['geographicCell']['originalProjectionCoversWholeCell']
  assert r['exactWholeCellCoverage']['covered']
 contact=read(PHYS/'support-checks.json.gz')['rows'][0];raw=contact['interface'];assert contact['sourceSHA256']==EXPECTED[T]and contact['supportSHA256']==EXPECTED[P];assert raw['samples']==2034 and raw['strictContacts']==1965 and raw['wallIntersections']==0 and len(raw['unresolved'])==69
 previous=read(NEAR/'nearest.json.gz')['rows'];assert sorted(x['position']for x in previous)==sorted(x['position']for x in raw['unresolved'])
 edges=read(EDGE/'edges.json.gz');assert edges['summary']['samplesAccounted']==69 and not edges['summary']['unaccountedSamples'] and len(edges['rows'])==92
 assert read(BOUND/'summary.json')['allModesComplete'] and read(FOUND/'foundations.json')['allModesPassed']
 images=[BASE/'government-xl-oi-sin-interface-role-views-v1-20261017/interface-context.png',BASE/'government-xl-oi-sin-assembly-coverage-v1-20261017/assembly-source-context.png']
 decision=dict(sourceSHA256ByUid=EXPECTED,sourceRoleReviewed=True,sourceSpecificBoundaryInterpretationAccepted=True,rawStrictInterfacePassed=raw['passed'],rawUnresolved=raw['unresolved'],strictContacts=1965,totalContacts=2034,exactAffectedOriginalEdges=92,sourceIdentityAssemblyQualified=True,rawIndividualIdentityReasons={u:r['reasons']for u,r in identities.items()},spatialEvidence=spatial,reviewer='Codex ROOT',review='The exact same-parent original tower and podium form one continuous building assembly. The affected low edges follow the authored facade/podium deck perimeter; all69 raw samples are accounted by92 complete original edges within0.1m of the corresponding originally horizontal finite podium surfaces in all captured source-coordinate modes. Complete original and current-rendered foundations remain clear, with1965 strict contacts. The small source boundary overhang is interpreted as authored facade/interface detail on the otherwise supported tower, not a detached unsupported model. This exact-source applicability review does not assert that the canonical projected vertical-contact tests pass and must not transfer to other sources or revisions.',imageInspection=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),inspectedByRoot=True)for p in images],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=0,fullAcceptance=False,publicationApproved=False,remaining=['current complete basic/native neighbour regression over changed terrain domain','staged/live browser and fallback acceptance','guarded installation with exact dependency and review binding'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',decision);refs.extend(images)
 out=module('oi_boundary_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-exact-original-boundary-and-assembly-review-v1',list(set(refs)),dict(uids=[T,P],sourceSpecificBoundaryInterpretationAccepted=True,sourceIdentityAssemblyQualified=True,rawStrictInterfacePassed=False,fullAcceptance=False,publicationApproved=False,nextStep='Run remaining current complete neighbour and browser gates; preserve raw checks and bind exact source-specific interpretation at guarded publication.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
