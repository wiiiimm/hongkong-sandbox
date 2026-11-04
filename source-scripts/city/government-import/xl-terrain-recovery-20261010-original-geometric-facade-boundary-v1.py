"""Complete explicit graph-actor local facade planes; source-only diagnostic."""
import argparse,importlib.util,json,time,uuid
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_geometric_finite_facade_boundary_diagnostic_20261010 import prepare_hosts,diagnose
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--support',required=True);p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);a=p.parse_args();doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();support=ROOT/a.support;physical=ROOT/a.physical
 graph=read(support/'diagnostic.json.gz');receipt=read(support/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selected=read(physical/'selection.json.gz');by_uid={r['uid']:r for r in selected['rows']};actor_uids=[r['uid'] for r in graph['actors']];assert len(actor_uids)==len(set(actor_uids)) and set(actor_uids)<=set(by_uid);selected={**selected,'rows':[by_uid[u] for u in actor_uids]};assert all(r['sourceSHA256']==actor['sourceSHA256'] for r,actor in zip(selected['rows'],graph['actors']));assets=[ROOT/r['candidate']['path'] for r in selected['rows']];assert all(digest(p.read_bytes())==r['sourceSHA256'] for p,r in zip(assets,selected['rows']));tri=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 roots=set(graph['resolvedOriginalComponents']);rootfaces=sorted(i for k in roots for i in graph['components'][k]['globalOriginalFaces']);wanted=sorted(set(range(len(graph['components'])))-roots);prepared=prepare_hosts(tri,rootfaces);results=[]
 claim=reservations.claim('original-local-facade-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 try:
  for k in wanted:
   row=diagnose(prepared,graph['components'][k]['globalOriginalFaces']);row.update(component=k,actorUID=graph['components'][k]['actorUID']);results.append(row)
   if time.monotonic()-last>20 or len(results)%8==0:
    save(doc/'partial-diagnostic.json.gz',dict(completeProof=False,results=results,installationApproved=False));assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(done=len(results),total=len(wanted),passed=sum(r['sourceOnlyBoundaryBandPassed'] for r in results))),flush=True)
  refs=[ref(p) for p in [Path(__file__),support/'result.json',support/'diagnostic.json.gz',physical/'selection.json.gz',HERE/'original_geometric_finite_facade_boundary_diagnostic_20261010.py',HERE/'test_exact_original_edge_finite_facade_distance_band_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py',HERE/'exact_original_perpendicular_edge_facet_band_20261010.py',HERE/'test_exact_original_perpendicular_edge_facet_band_20261010.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]]
  result=dict(uids=[r['uid'] for r in selected['rows']],completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),resolvedOriginalStructuralComponents=sorted(roots),allUnresolvedOriginalComponents=wanted,results=results,evidenceRefs=refs,sourceOnlyPassedComponents=[r['component'] for r in results if r['sourceOnlyBoundaryBandPassed']],sourceGeometryChanges=0,structuralRootCredit=False,visualRoleAccepted=False,installationApproved=False);save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('local_facade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-explicit-graph-actor-geometric-finite-facade-boundary-diagnostic-v1',[ROOT/r['path'] for r in refs],dict(uids=result['uids'],sourceComponentsDiagnosed=len(results),sourceOnlyPassedComponents=result['sourceOnlyPassedComponents'],scriptFullAcceptancePassed=False,structuralRootCredit=False,visualRoleAccepted=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
