"""ALL207 unresolved original bodies; finite open-loop/closed-face census only.

Host bodies have source-only geometric paths to five nonvisual original podium
bodies, not independent physical roots. Every raw zero contact remains. No
source/visual/root/bridge/current/native/foreign/installation acceptance.
"""
from pathlib import Path
from collections import defaultdict,deque
import importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_band
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-mount-verdant-complete-original-edge-contact-graph-v1';PROBE=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006';UID='landsd/261717:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(GRAPH/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(GRAPH/'diagnostic.json.gz')in receipt['evidenceRefs'];graph=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz');worlds=[];assets=[]
 for uid,count in [(UID,14938),('landsd/75782:0',641)]:
  row=next(p for p in selected['rows']if p['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(count,3,3);worlds.append(world);assets.append(asset)
 world=np.concatenate(worlds);nodes=graph['components'];assert len(nodes)==973 and len(world)==15579;adj=defaultdict(set)
 for e in graph['oneExactPositiveWitnessPerContactingBodyPair']:
  assert e['exactContact']['dimension']in[1,2];a,b=e['components'];adj[a].add(b);adj[b].add(a)
 seeds={i for i,n in enumerate(nodes)if n['actorUID']=='landsd/75782:0'and len(n['globalOriginalFaces'])in[576,10]and 14938+270 not in n['globalOriginalFaces']};assert seeds=={966,968,969,970,971};seen=set(seeds);queue=deque(seeds)
 while queue:
  for j in adj[queue.popleft()]-seen:seen.add(j);queue.append(j)
 missing=[i for i,n in enumerate(nodes)if n['actorUID']==UID and i not in seen];assert len(missing)==207 and sum(len(nodes[i]['globalOriginalFaces'])for i in missing)==2682
 hostids=sorted(fi for i in seen for fi in nodes[i]['globalOriginalFaces']);assert not set(hostids)&{fi for i in missing for fi in nodes[i]['globalOriginalFaces']};host=world[hostids]
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs=[ref(p)for p in [Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',PROBE/'selection.json.gz',*assets,*[HERE/n for n in helpers]]]
 binding=dict(complete15579WorldSHA256=digest(world.tobytes()),completeHostGlobalFaceIDs=hostids,graphReceipt=ref(GRAPH/'result.json'),producer=ref(Path(__file__)),helpers=[ref(HERE/n)for n in helpers]);claim=reservations.claim('mount207-immutable-back-census-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();partial=LOCAL/'partial.json.gz';saved=read(partial)if partial.exists()else None;assert saved is None or saved['binding']==binding;rows=[]if saved is None else saved['rows'];assert [r['originalBody']for r in rows]==missing[:len(rows)]
 try:
  for component in missing[len(rows):]:
   ids=nodes[component]['globalOriginalFaces'];edges=defaultdict(list)
   for fi in ids:
    points=[tuple(float(x)for x in p)for p in world[fi]]
    for a,b in zip(points,points[1:]+points[:1]):edges[tuple(sorted((a,b)))].append(dict(sourceFace=fi,directedVertices=[a,b]))
   boundary=[(edge,records)for edge,records in edges.items()if len(records)==1];conflicts=[edge for edge,records in edges.items()if len(records)==2 and records[0]['directedVertices']==records[1]['directedVertices']];nonmanifold=[edge for edge,records in edges.items()if len(records)>2];assert not conflicts and not nonmanifold
   record=dict(originalBody=component,completeOriginalGlobalFaceIDs=ids,completeOriginalTrianglesSHA256=digest(world[ids].tobytes()),rawOriginalGraphZeroPositiveContactsPreserved=component not in seen,originalIncidenceOneBoundaryEdges=[list(edge)for edge,_ in boundary],completeAllEdgeIncidenceRecords=[dict(originalEdge=[list(p)for p in edge],records=records)for edge,records in edges.items()],originalWindingConflicts=conflicts,originalNonmanifoldEdges=nonmanifold)
   if len(ids)==10:
    assert len(boundary)==4;degree=defaultdict(int)
    for edge,_ in boundary:
     for p in edge:degree[p]+=1
    assert len(degree)==4 and set(degree.values())=={2};proofs=[dict(completeOriginalEdge=[list(p)for p in edge],proof=edge_band(np.asarray(edge),host))for edge,_ in boundary];record.update(openBack10FaceFourEdgeLoop=True,completeBoundaryEdgeProofs=proofs,completeBoundaryWithinFixedBand=all(p['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in proofs))
   else:
    assert len(ids)==28 and not boundary;proofs=[dict(originalGlobalSourceFace=fi,proof=facet_band(world[fi],host))for fi in ids];record.update(closed28FaceCompleteFacetCensus=True,all28WholeFacetHostBandProofs=proofs,wholeFacetBandPositiveFaceIDs=[p['originalGlobalSourceFace']for p in proofs if p['proof']['wholeFacetAssociated']])
   rows.append(record)
   if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();save(partial,dict(binding=binding,rows=rows));print(json.dumps(dict(bodies=len(rows),total=207)),flush=True)
  assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/p['path'])==p for p in refs);save(partial,dict(binding=binding,rows=rows,complete=True));positive=[p['originalBody']for p in rows if p.get('completeBoundaryWithinFixedBand')];save(DOC/'diagnostic.json.gz',dict(uid=UID,complete14938OriginalTowerFacesRetained=True,complete15579PairWorldSHA256=digest(world.tobytes()),sourceOnlyGeometricNonvisualPodiumSeeds=sorted(seeds),completeHostGlobalFaceIDs=hostids,all207Bodies2682Faces=rows,completeOpenBackBoundaryBandPositiveBodies=positive,completeClosed28BodyWholeFacetOnlyPositiveInventory=True,unqualifiedHostGroundingAndMountRoleStillRequired=True,sourceOnly=True,freshCurrentAcceptance=False,visualRoleAccepted=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs))
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'all207-original-tower-bodies-complete-open-back-loops-closed-face-census-diagnostic-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz',partial],dict(uids=[UID],all207BodiesAccounted=True,openBackLoopPositiveBodies=positive,sourceOnly=True,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(complete207=True,openBackLoopPositive=len(positive))),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
