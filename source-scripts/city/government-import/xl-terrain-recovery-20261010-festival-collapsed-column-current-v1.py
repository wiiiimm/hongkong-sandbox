"""Fresh finite-column refinement of all26 frozen podium paired negatives."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import refine
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'xl-terrain-recovery-20261010-festival-podium-current-paired-finite-clearance-v1'
PHYS=BASE/'government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010'
BATCH='xl-terrain-recovery-20261010-festival-collapsed-column-current-v1';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD/'diagnostic.json.gz');receipt=read(OLD/'result.json')
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 selection=read(PHYS/'selection.json.gz');row=next(r for r in selection['rows'] if r['uid']=='landsd/91827:0');asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];original=decode_original_world_triangles(raw)
 runtime=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';r=next(r for r in read(runtime)['rows'] if r['uid']==row['uid']);world=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);cached=old['rows'][0]
 assert digest(original.tobytes())==cached['completeOriginalWorldSHA256'] and digest(world.tobytes())==cached['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==cached['completeGroundSHA256']
 final=[]
 for c in cached['allFaces']:
  i=c['sourceFace'];assert c['priorCoarseBoundProofVerbatim']['completeOriginal']['sourceFaceSHA256']==digest(original[i].tobytes()) and c['priorCoarseBoundProofVerbatim']['actualRendered']['sourceFaceSHA256']==digest(world[i].tobytes())
  a=None if c['completeOriginalBoundProved'] else refine(original[i],ground,c['pairedExactOriginalFiniteBound']);b=None if c['completeActualRenderedBoundProved'] else refine(world[i],ground,c['pairedExactActualRenderedFiniteBound'])
  final.append(dict(sourceFace=i,priorCompletePairedProofVerbatim=c,exactOriginalColumnRefinement=a,exactActualRenderedColumnRefinement=b,completeOriginalBoundProved=c['completeOriginalBoundProved'] or bool(a and a['existingOrdinaryClearanceBoundProved']),completeActualRenderedBoundProved=c['completeActualRenderedBoundProved'] or bool(b and b['existingOrdinaryClearanceBoundProved'])))
  if a or b:print(json.dumps(dict(face=i,original=a['exactCertifiedLowerClearanceM'] if a else None,rendered=b['exactCertifiedLowerClearanceM'] if b else None,coverage=a['groundProjectionCovered'] if a else None)),flush=True)
 refs=[ref(p) for p in [Path(__file__),OLD/'diagnostic.json.gz',OLD/'result.json',PHYS/'selection.json.gz',PHYS/'result.json',runtime,asset,HERE/'exact_original_paired_finite_clearance_v2_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'test_exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 unresolved=[r['sourceFace'] for r in final if not r['completeOriginalBoundProved'] or not r['completeActualRenderedBoundProved']];save(DOC/'diagnostic.json.gz',dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(original),completeOriginalWorldSHA256=digest(original.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),allFaces=final,unprovedFaces=unresolved,rawPriorFailuresRetained=True,sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False,evidenceRefs=refs));spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-current-finite-column-refinement-v1',[ROOT/r['path'] for r in refs],dict(uids=[row['uid']],completeOriginalFaces=len(original),unprovedFaces=unresolved,rawPriorFailuresRetained=True,sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False));print(unresolved,flush=True)
if __name__=='__main__':main()
