"""Independent full finite vertex-bound clearance, preserving raw diagnostics.

No import acceptance is granted. Every actual original and rendered triangle
gets exact projection coverage and a separate conservative finite height bound.
"""
import argparse,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);a=p.parse_args();doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();physical=ROOT/a.physical;geometry=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(geometry);selection=read(physical/'selection.json.gz');rows=[];refs=[ref(p) for p in [Path(__file__),geometry,physical/'selection.json.gz',physical/'result.json',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'test_exact_projection_coverage_v2_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']]
 claim=reservations.claim('complete-conservative-clearance-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for row in selection['rows']:
   asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
   faces=[]
   for i,(original,rendered) in enumerate(zip(tri,world)):
    first=verify(original,ground);second=first if np.array_equal(original,rendered) else verify(rendered,ground);faces.append(dict(sourceFace=i,completeOriginal=first,actualRendered=second))
    if i%200==0:assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(uid=row['uid'],completeFacesChecked=i,total=len(tri))),flush=True)
   refs.append(ref(asset));rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),completeOriginalFaces=len(tri),allFaces=faces,unprovedOriginalFaceBounds=[r['sourceFace'] for r in faces if not r['completeOriginal']['existingOrdinaryClearanceBoundProved']],unprovedActualRenderedFaceBounds=[r['sourceFace'] for r in faces if not r['actualRendered']['existingOrdinaryClearanceBoundProved']]))
  result=dict(rows=rows,allWholeOriginalAndRenderedBoundsProved=all(not r['unprovedOriginalFaceBounds'] and not r['unprovedActualRenderedFaceBounds'] for r in rows),rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('conservative_clearance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-original-rendered-conservative-finite-clearance-exact-disjoint-pruning-diagnostic-v2',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in rows],completeOriginalFaces=sum(r['completeOriginalFaces'] for r in rows),allWholeOriginalAndRenderedBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedFaces={r['uid']:r['unprovedOriginalFaceBounds'] for r in rows},rawPriorDiagnosticChanged=False,fullAcceptance=False))
  print(json.dumps(dict(allWholeOriginalAndRenderedBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedOriginal={r['uid']:r['unprovedOriginalFaceBounds'] for r in rows},unprovedRendered={r['uid']:r['unprovedActualRenderedFaceBounds'] for r in rows})),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
