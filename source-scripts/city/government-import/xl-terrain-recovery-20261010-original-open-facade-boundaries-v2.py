"""Replay complete unresolved original boundaries, diagnosis only."""
import argparse,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_open_facade_boundary_band_diagnostic_20261010 import diagnose
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--historical-manifest');p.add_argument('--support',required=True);p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);a=p.parse_args();doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();support=ROOT/a.support;physical=ROOT/a.physical
 graph=read(support/'diagnostic.json.gz');receipt=read(support/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:
  if r['path']=='3d-viewer/city/data/manifest.json' and ref(ROOT/r['path'])!=r:
   assert a.historical_manifest and digest((ROOT/a.historical_manifest).read_bytes())==r['sha256'],'Exact original manifest archive required'
  else:assert ref(ROOT/r['path'])==r
 selected=read(physical/'selection.json.gz');assets=[ROOT/r['candidate']['path'] for r in selected['rows']];assert all(digest(p.read_bytes())==r['sourceSHA256'] for p,r in zip(assets,selected['rows']));tri=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 rooted=set(graph['resolvedOriginalComponents']);rootfaces=sorted(i for k in rooted for i in graph['components'][k]['globalOriginalFaces']);wanted=sorted(set(range(len(graph['components'])))-rooted);results=[]
 claim=reservations.claim('original-open-facade-diagnostic-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for k in wanted:
   row=diagnose(tri,graph['components'][k]['globalOriginalFaces'],rootfaces);row.update(component=k,actorUID=graph['components'][k]['actorUID']);results.append(row);save(doc/'partial-diagnostic.json.gz',dict(completeProof=False,results=results,installationApproved=False));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(component=k,completeBoundaryEdges=len(row['completeOriginalDirectedBoundaryEdges']),sourceOnlyBoundaryBandPassed=row['sourceOnlyBoundaryBandPassed'],reasons=row['reasons'])),flush=True)
  refs=([ref(ROOT/a.historical_manifest)] if a.historical_manifest else [])+[ref(p) for p in [Path(__file__),support/'result.json',support/'diagnostic.json.gz',physical/'selection.json.gz',HERE/'original_open_facade_boundary_band_diagnostic_20261010.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]]
  result=dict(uids=[r['uid'] for r in selected['rows']],completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),resolvedOriginalStructuralComponents=sorted(rooted),allUnresolvedOriginalComponents=wanted,results=results,evidenceRefs=refs,sourceOnlyPassedComponents=[r['component'] for r in results if r['sourceOnlyBoundaryBandPassed']],sourceGeometryChanges=0,structuralRootCredit=False,visualRoleAccepted=False,installationApproved=False);save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('facade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-original-open-facade-boundary-fixed-band-diagnostic-v2',[ROOT/r['path'] for r in refs],dict(uids=result['uids'],sourceComponentsDiagnosed=len(results),sourceOnlyPassedComponents=result['sourceOnlyPassedComponents'],scriptFullAcceptancePassed=False,structuralRootCredit=False,visualRoleAccepted=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
