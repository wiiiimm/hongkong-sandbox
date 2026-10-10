"""Every actual original boundary edge vs complete rooted finite façade scope.
No single-opening/orientation inference, visual role or structural root credit.
"""
import importlib.util,json,uuid
from pathlib import Path
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify
BATCH='xl-terrain-recovery-20261010-mei-yat-all-boundary-euclidean-diagnostic-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;assert not DOC.exists()
PHYS=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010';SUP=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-mei-yat-complete-original-support-v1';g=read(SUP/'diagnostic.json.gz');receipt=read(SUP/'result.json')
with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
r=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());assert digest(t.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
rooted=set(g['resolvedOriginalComponents']);un=sorted(set(range(len(g['components'])))-rooted);hosts=sorted(i for k in rooted for i in g['components'][k]['globalOriginalFaces']);results=[];claim=reservations.claim('mei-yat-exact-boundary-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
try:
 for k in un:
  ids=g['components'][k]['globalOriginalFaces'];edges=defaultdict(list)
  for i in ids:
   v=list(map(tuple,t[i]))
   for a,b in zip(v,v[1:]+v[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
  boundary=[inc[0] for edge,inc in sorted(edges.items()) if len(inc)==1];rawbad=[dict(edge=list(edge),incidence=inc) for edge,inc in edges.items() if len(inc)>2 or len(inc)==2 and inc[0][1:]!=inc[1][1:][::-1]];proofs=[]
  for i,a,b in boundary:
   q=verify(np.array([a,b]),t[hosts]);proofs.append(dict(originalBoundaryFace=i,completeOriginalEdge=[list(a),list(b)],completeRootedHostIndexMap=hosts,finiteDistanceBand=q))
  row=dict(component=k,completeOriginalFaces=ids,completeBoundaryEdges=len(boundary),allOriginalBoundaryProofs=proofs,rawOriginalTopologyConflicts=rawbad,allBoundariesFiniteFacadeBandPassed=bool(boundary) and all(p['finiteDistanceBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for p in proofs),visualRoleAccepted=False,structuralRootCredit=False);results.append(row);save(DOC/'partial-diagnostic.json.gz',dict(uids=[r['uid']],complete=False,results=results));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(component=k,edges=len(boundary),passed=row['allBoundariesFiniteFacadeBandPassed'],topologyConflicts=len(rawbad))),flush=True)
 refs=[ref(p) for p in [Path(__file__),asset,SUP/'diagnostic.json.gz',SUP/'result.json',PHYS/'selection.json.gz',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py',HERE/'exact_original_perpendicular_edge_facet_band_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']]
 save(DOC/'diagnostic.json.gz',dict(uids=[r['uid']],completeOriginalFaces=len(t),completeOriginalComponents=len(g['components']),rootedOriginalComponents=sorted(rooted),allUnresolvedOriginalComponents=un,results=results,evidenceRefs=refs,completeOriginalWorldSHA256=digest(t.tobytes()),sourceGeometryChanges=0,structuralRootCredit=False,visualRoleAccepted=False,installationApproved=False))
 spec=importlib.util.spec_from_file_location('freeze_boundary',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'whole-original-boundary-exact-finite-euclidean-fixed-band-diagnostic-v1',[ROOT/p['path'] for p in refs],dict(uids=[r['uid']],sourceGeometryChanges=0,diagnosedComponents=len(un),finiteBoundaryBandPassingComponents=[q['component'] for q in results if q['allBoundariesFiniteFacadeBandPassed']],visualRoleAccepted=False,structuralRootCredit=False))
finally:assert reservations.release(lease)['ok']
