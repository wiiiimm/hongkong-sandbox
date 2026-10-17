"""Exact actual-vertex exposure refines coarse wall bounds; no source changes."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v3_20261011 import verify
from original_bound_facet_wall_context_20261010 import canonical,down
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-esplanade-exact-wall-exposure-v1-20261015';DOC=BASE/BATCH;PREV=BASE/'government-xl-esplanade-certified-grade-roles-v1-20261015';PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';LOCAL=HERE/'local'/PHYSICAL.name

def main():
 assert not DOC.exists();receipt=read(PREV/'result.json')
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 row=next(r for r in read(PHYSICAL/'selection.json.gz')['rows']if r['uid']=='landsd/309385:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];original=decode_original_world_triangles(raw);rt=next(r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']if r['uid']==row['uid']);literal=np.asarray(rt['position'],float).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);results=[]
 for mode,tri in [('original',original),('literal',literal)]:
  before=read(PREV/(mode+'.json.gz'));assert before['binding']['completeOriginalWorldTrianglesSHA256']==digest(tri.tobytes())and before['groundSHA256']==digest(ground.tobytes());ctx=before['contexts'];witnesses=[]
  for i in before['capPaths']['affectedOriginalWallFaces']:
   vertex=int(np.argmax(tri[i,:,1]));point=tri[i,vertex];proof=verify(np.repeat(point[None,:],3,axis=0),ground);assert proof['groundProjectionCovered'];bound=F(proof['exactCertifiedLowerClearanceM']);ctx[i]={**ctx[i],'coarseExposureBoundVerbatim':ctx[i]['maximumObservedGapM'],'maximumObservedGapM':down(bound),'exposureQualification':'Exact finite-column lower bound at unchanged original highest vertex; point is an exposure witness only, never support/graph bridge','exactVertexExposureLowerBoundM':str(bound)};witnesses.append(dict(sourceFace=i,vertex=vertex,position=point.tolist(),proof=proof))
  binding={**before['binding'],'completeCurrentFacetContextsSHA256':canonical(ctx)};paths=cap_paths(tri,ctx,[],expected_binding=binding,current_binding=binding)
  save(DOC/(mode+'.json.gz'),dict(binding=binding,contexts=ctx,vertexExposureProofs=witnesses,capPaths=paths,gradeInterfaces=before['gradeInterfaces'],installationApproved=False));results.append(dict(mode=mode,affected=paths['affectedOriginalWallFaces'],allHaveCapPaths=paths['allAffectedHavePaths'],exposureFailures=paths['rawExposureFailures'],positiveVertexWitnesses=sum(F(w['proof']['exactCertifiedLowerClearanceM'])>0 for w in witnesses)))
 paths=[Path(__file__),PREV/'result.json',PREV/'original.json.gz',PREV/'literal.json.gz',PHYSICAL/'selection.json.gz',LOCAL/'runtime-geometry.json.gz',ROOT/row['candidate']['path']]+[HERE/n for n in ['exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','original_bound_facet_wall_context_20261010.py']]
 spec=importlib.util.spec_from_file_location('esplanade_exposure_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'original-literal-exact-vertex-exposure-cap-path-v1',paths,dict(uids=[row['uid']],rows=results,fullAcceptance=False,qualification='Certified wall exposure and cap paths; no point-root credit, structural claim or whole-model acceptance.'));print(results,flush=True)
if __name__=='__main__':main()
