"""Exact-source human-readable role review; retains canonical failures, no publication."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-oi-sin-carpark-source-review-v1-20261017';DOC=BASE/BATCH
PHASES=['four-originals-physical-v2','four-originals-foundations-v3','carpark-world-rim-v1','carpark-rim-topology-v1','carpark-junction-sections-v1','assembly-coverage-v2','four-originals-world-capture-v2','four-originals-browser-v3']
def main():
 assert not DOC.exists();refs=[Path(__file__)];folders={p:BASE/('government-xl-oi-sin-'+p+'-20261017')for p in PHASES};pins={}
 for d in folders.values():
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 phys=folders['four-originals-physical-v2'];sources=read(phys/'selection.json.gz')['rows'];byuid={s['uid']:s for s in sources};U='landsd/256457:0';S='landsd/254867:0'
 assert all(s['source']['building']['parent']=='way/111529738'for s in sources)
 ids={r['uid']:r for r in read(phys/'identity-proofs.json')['rows']};assert ids[U]['passed'];assert set(ids[S]['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
 cov={r['uid']:r for r in read(folders['assembly-coverage-v2']/'coverage.json')['rows']};assert cov[S]['assemblyCoverageFraction']>.99
 foundations=read(folders['four-originals-foundations-v3']/'foundations.json')['rows']
 for row in foundations:
  r=foundations[row['reusedRow']]if 'reusedRow'in row else row;b=r['bareGroundFoundation'];f=r['foundation']
  assert b['completeTerrainTriangles']==b['triangles'] and b['fullyBuriedTriangles']==0
  if row['uid']==U:assert f['fullyBuriedTriangles']==2 and f['fullyBuriedUpwardTriangles']==0
  else:assert r['strictFoundationAccepted']
 assert read(folders['carpark-world-rim-v1']/'world-rim.json.gz')['summary']['passed']==32
 topo=read(folders['carpark-rim-topology-v1']/'topology.json')['summary'];assert topo['samplesOnSelectedBoundary']==topo['unresolvedContactSamples']==19
 worlds=read(folders['four-originals-world-capture-v2']/'world-triangles.json.gz');faceEvidence=[]
 for mode,w in worlds.items():
  t=np.asarray(w[U])
  for fi in [68,69]:
   face=t[fi];normal=np.cross(face[1]-face[0],face[2]-face[0]);assert normal[1]==0 and np.linalg.norm(normal)>0
   adjacent=[]
   for a,b in zip(face,np.roll(face,-1,axis=0)):
    matches=[j for j,u in enumerate(t)if j!=fi and any(np.array_equal(a,x)for x in u)and any(np.array_equal(b,x)for x in u)];assert matches;adjacent.append(matches)
   faceEvidence.append(dict(mode=mode,face=fi,vertices=face.tolist(),edgeAdjacentFaces=adjacent,areaM2=float(np.linalg.norm(normal)/2)))
 raw=next(r['interface']for r in read(phys/'support-checks.json.gz')['rows']if r['uid']==U)
 image=folders['carpark-junction-sections-v1']/'sections.png'
 review=dict(reviewer='Codex ROOT',sourceSHA256ByUid={s['uid']:s['sourceSHA256']for s in sources},sourceRoleReviewed=True,sourceSpecificJunctionInterpretationAccepted=True,rawStrictInterfacePassed=False,rawStrictFoundationPassed=False,rawInterface=raw,rawFoundationRows=[r for r in foundations if r['uid']==U],faceEvidence=faceEvidence,imageInspection=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()),inspectedByRoot=True),review='The two exact vertical triangles68/69 are connected wall-junction facets of the original rounded carpark core where it meets its same-parent original podium. Every edge has original same-model adjacent geometry in all four captured modes. All complete source faces clear bare terrain; the two failures are against the maximum podium roof, not buried terrain or upward floor surfaces. Six inspected source sections show the narrow wall junction. All19 raw low-rim failures are accounted by8 actual perimeter edges, each completely within the unchanged finite0.1m podium band in all4 modes, alongside94 strict contacts. Interpret this as an authored connection within the complete original assembly. This is an exact-source functional review, not a claim that the canonical highest-surface foundation/interface tests pass, not a distance-threshold waiver, and not transferable to another source or revision.',smallCarparkIdentity=dict(uid=S,sourceSpecificAssemblyIdentityAccepted=True,rawReasons=ids[S]['reasons'],perTargetCoverage=cov[S],basis='Exact current government identifier and shared parent; the missing own projection is supplied by the unchanged podium in the same complete assembly. The small source has30/30 strict contacts and clear complete compound foundations.'),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=0,fullAcceptance=False,publicationApproved=False,remaining=['fresh four-original ordinary-neighbour checks with all other forms retained','bind both source-specific reviews in guarded installer','live installation verification and commit/push'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 r=module('oi_carpark_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-exact-original-carpark-junction-source-review-v1',list(set(refs)),dict(uids=[U,S],sourceSpecificJunctionInterpretationAccepted=True,rawStrictInterfacePassed=False,rawStrictFoundationPassed=False,fullAcceptance=False,nextStep='Proceed to complete four-original neighbour and guarded publication gates, retaining raw strict failures and exact source-specific review bindings.'));print(r['jobId'],flush=True)
if __name__=='__main__':main()
