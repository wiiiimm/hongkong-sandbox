"""Complete source-bound finite wall contexts; no role or installation credit.

Retain old coarse/paired failures and the exact collapsed-column refinements.
Every original face is accounted for, including upward and collapsed geometry.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_bound_facet_wall_context_20261010 import canonical
from original_bound_facet_wall_context_v3_20261010 import contexts
from xl_source_stream_binding_20261009 import source_stream_binding
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
from original_coplanar_exterior_continuation_20261009 import diagnose
BASE=ROOT/'docs/astra-city/government-import'
PHYSICAL=BASE/'government-xl-man-fuk-complete-retained-original-physical-v5-20261010'
FINITE=BASE/'government-xl-man-fuk-v5-complete-paired-finite-clearance-20261010'
BATCH='government-xl-man-fuk-v5-complete-finite-wall-contexts-v3-20261010';DOC=BASE/BATCH
UID='landsd/266062:0';SOURCE='22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 receipt=read(FINITE/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 selection=read(PHYSICAL/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE;tri=decode_original_world_triangles(raw);assert tri.shape==(10661,3,3)
 runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows'][0];assert runtime['uid']==UID
 world=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
 all_finite=read(FINITE/'diagnostic.json.gz');assert len(all_finite['rows'])==1;finite=all_finite['rows'][0];assert finite['uid']==UID and finite['sourceSHA256']==SOURCE
 assert digest(tri.tobytes())==finite['completeOriginalWorldSHA256'] and digest(world.tobytes())==finite['completeActualRenderedWorldSHA256'] and digest(ground.tobytes())==finite['completeGroundSHA256']
 assert [r['sourceFace'] for r in finite['allFaces']]==list(range(len(tri)))
 normalized=finite['allFaces']
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical(normalized))
 ctx=contexts(tri,ground,normalized,expected_binding=binding,current_binding=binding)
 affected=[i for i,c in enumerate(ctx) if c['minimum']['minimumGapM']<-.5]
 path_binding={**source_stream_binding(raw),**binding,'decodedWorldTrianglesSHA256':digest(tri.tobytes()),'drawnGroundSHA256':digest(ground.tobytes())}
 paths=original_open_paths(tri,ctx,affected,range(len(tri)),expected_binding=path_binding,current_binding=path_binding)
 below=[r['sourceFace'] for r in paths['faces'] if r['reasons']==['no-exposed-wall-witness']]
 continuation=diagnose(tri,ctx,below) if below else {'rows':[],'wholeOriginalFacesAccounted':len(tri),'diagnosticOnly':True}
 n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(tri)),where=length>0)
 upward=[i for i in affected if ratio[i]>.25]
 refs=[ref(p) for p in [Path(__file__),FINITE/'diagnostic.json.gz',FINITE/'result.json',PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',runtime_path,asset,HERE/'original_bound_facet_wall_context_20261010.py',HERE/'test_original_bound_facet_wall_context_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'test_original_bound_facet_wall_context_v3_20261010.py',HERE/'test_original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'unchanged_open_exterior_paths_v2_20261009.py',HERE/'original_coplanar_exterior_continuation_20261009.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py']]
 result=dict(uid=UID,sourceSHA256=SOURCE,binding=binding,completeOriginalFaces=len(tri),completeCertifiedLowerBoundContexts=ctx,normalizedFiniteProofRows=normalized,normalizationQualification='Use all complete original paired finite certificates verbatim; no failure, ground candidate or source face omitted.',rawFiniteRowsSHA256=canonical(finite['allFaces']),affectedOriginalFaces=affected,buriedUpwardOriginalFaces=upward,originalWallPaths=paths,exactCoplanarContinuation=continuation,unexposedIndividualWallFaces=below,rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,roleAccepted=False,rootOrContactCredit=False,fullAcceptance=False,installationApproved=False,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-man-fuk-finite-wall-contexts-v1',[ROOT/r['path'] for r in refs],dict(uids=[UID],sourceSHA256=SOURCE,completeOriginalFaces=len(tri),affectedOriginalFaces=affected,buriedUpwardOriginalFaces=upward,unexposedIndividualWallFaces=below,coplanarContinuationAvailable=[r['sourceFace'] for r in continuation['rows'] if r['hasActualAboveGroundExteriorContinuation']],rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,fullAcceptance=False))
 print(json.dumps(dict(affected=len(affected),buriedUpward=upward,unexposedIndividualWalls=below,positiveOriginalContinuation=[r['sourceFace'] for r in continuation['rows'] if r['hasActualAboveGroundExteriorContinuation']])),flush=True)
if __name__=='__main__':main()
