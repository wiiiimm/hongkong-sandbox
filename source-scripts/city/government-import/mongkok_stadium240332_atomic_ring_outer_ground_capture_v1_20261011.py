"""DRAFT complete outer-neighbour and affected-actor inventory for frozen151 ring.
Read-only production terrain; no triangulation/apron/candidate or acceptance.
Execute only after ROOT full-read and under supervised canonical reservation.
"""
from pathlib import Path
import importlib.util,json,subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import'
ATOMIC=B/'government-xl-mongkok-stadium240332-atomic-domain-one-ring-inventory-v1-20261011'
OLD=B/'government-xl-mongkok-stadium240332-causal55-original-tin-domain-seam-diagnostic-v1-20261011'
DOC=B/'government-xl-mongkok-stadium240332-atomic-ring-outer-ground-capture-v1-20261011'
JS=HERE/'mongkok_stadium240332_atomic_ring_outer_ground_capture_v1_20261011.mjs'
PIN='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(sorted(uids),)).fetchall()
def main():
 assert not DOC.exists();refs=[ref(Path(__file__)),ref(JS)]
 for folder in [ATOMIC,OLD]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  refs.append(ref(folder/'result.json'))
 a=read(ATOMIC/'diagnostic.json.gz');o=read(OLD/'complete-domain-actual-ground-provenance.json.gz');assert not a['terrainProposalCreated']and a['completeCausalDomainFacets']==55
 core=[dict(actualTriangle=np.asarray(r['actualTriangle'],float).reshape(3,3).tolist(),productionGlobalIdentity={k:r[k]for k in ['meshOrdinal','originalMeshFacet']})for r in o['completeClosedDomainAABBActualGroundFacets']if r['causalCapturedFacetId']is not None]
 rows=core+a['completeOneProjectedPositiveEdgeRingFaces'];assert len(core)==55 and len(rows)==151
 lo,hi=a['completeWholeDomainAndRingXZBounds'];bounds=[lo[0],lo[1],hi[0],hi[1]];tri=np.asarray([r['actualTriangle']for r in rows]);assert tri.shape==(151,3,3)and np.isfinite(tri).all();assert np.array_equal(tri[:,:,[0,2]].min((0,1)),lo)and np.array_equal(tri[:,:,[0,2]].max((0,1)),hi)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==PIN
 # Complete form tile query for the genuine whole151 bounds; no arbitrary domain expansion.
 spec=importlib.util.spec_from_file_location('stadium_ring_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);forms=m.load_forms(bounds);form_rows=[dict(building=f,tile=t)for f,_,t in forms];refs.extend(ref(ROOT/'3d-viewer'/t)for _,_,t in forms)
 native=[]
 for catalogue in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/catalogue;refs.append(ref(path))
  for e in read(path)['models']:
   p,q=e['worldBounds']
   if e['uid']=='landsd/240527:0'or not(q[0]<lo[0]or p[0]>hi[0]or q[2]<lo[1]or p[2]>hi[1]):
    asset=path.parent/e['asset'];assert ref(asset)['sha256']==e['sha256'];refs.append(ref(asset));native.append(dict(catalogue=ref(path),entry=e,actualAsset=ref(asset),protectionDischarged=False))
 assert any(r['entry']['uid']=='landsd/240527:0'for r in native)
 uids={'landsd/240332:0','landsd/240527:0'}|{r['entry']['uid']for r in native}|{f['uid']for f,_,_ in forms};before=state(uids)
 refs.extend([ref(manifest),ref(ATOMIC/'diagnostic.json.gz'),ref(OLD/'complete-domain-actual-ground-provenance.json.gz'),ref(HERE/'xl-final-script-pass.py')]);save(DOC/'inputs.json.gz',dict(uid='landsd/240332:0',currentManifest=start,completeFrozenWholeDomainAndRingFacets=rows,exactWholeDomainAndRingXZBounds=bounds,evidenceRefs=refs))
 output=DOC/'complete-outer-current-ground.json.gz';subprocess.run(['node',str(JS),str((DOC/'inputs.json.gz').relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,check=True);g=read(output);assert g['startEndAllInputsVerified']and g['all151UniqueOriginalGlobalProvenance']
 matches=g['all151FrozenDomainRingFacetMatches'];assert len(matches)==151
 for r in matches:assert r['completeExactGlobalMatches']==[rows[r['frozenDomainRingFace']]['productionGlobalIdentity']]
 allfaces=g['completeClosedDomainAABBActualGroundFacets'];assert sum(r['frozenDomainRingFace']is not None for r in allfaces)==151
 refs.extend([ref(DOC/'inputs.json.gz'),ref(output)]);refs.extend(dict(path=p,sha256=h)for p,h in g['inputHashes'].items());assert ref(manifest)==start and state(uids)==before and all(ref(ROOT/r['path'])==r for r in refs)
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',currentManifest=start,sourceOnly=True,currentAcceptance=False,terrainProposalCreated=False,sourceGeometryChanges=0,terrainGeometryChanges=0,completeFrozenCoreRingFaces=151,completeWholeRingBounds=bounds,completeGlobalActualFacetsTraversed=g['completeGlobalActualFacetsTraversed'],completeOuterNeighbourBroadphase=True,completeRelevantActualGroundFaces=len(allfaces),completeOutsideRetainedNeighbourFaces=len(allfaces)-151,allAffectedCurrentForms=form_rows,allAffectedInstalledNativeEntries=native,allProtectedReviewUIDs=sorted(uids),protectedReviewStateUnchanged=True,allPriorAtomic3DNegativesPreserved=True,apronTriangulationCreated=False,protectedActorRegressionsDischarged=False,evidenceRefs=list({(r['path'],r['sha256']):r for r in refs}.values()),qualification='Complete closed whole151-facet ring bounds traversed against all actual production terrain, with original core/ring tuple and global identities pinned. Expanded BASIC/native/installed actors and exact assets are protection obligations only; no support/ground/identity acceptance. Existing current3D cracks and source/core two-cycle negatives remain historical diagnostic facts, not waived. No generated apron or candidate is produced. Outer edge exact seams, deterministic positive finite generated pieces, full original-source core/F32 internal and external incidence, and complete affected-actor ordinary/strict/grade/body/foreign/native regressions remain mandatory.'))
 print(json.dumps(dict(wholeCoreRingFaces=151,relevantActualGroundFaces=len(allfaces),outsideRetainedNeighbours=len(allfaces)-151,affectedForms=len(form_rows),protectedNativeEntries=len(native),currentAcceptance=False)))
if __name__=='__main__':main()
