"""Exact terrain-only consolidation and fresh highest-surface evidence; no publication."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_runtime_coplanar_consolidation_20261010 import consolidate
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-exact-terrain-validation-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-folkland-flatten-native-parent-v1-20261020';LOCAL=BASE/'government-xl-folkland-native-parent-candidate-v1-20261020';AUDIT=BASE/'government-xl-folkland-parent-overlap-audit-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,LOCAL,AUDIT]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 patch=consume(SRC/'unapproved-complete-parent.json');local=consume(LOCAL/'unapproved-local-surface.json');context=consume(AUDIT/'summary.json');assert context['crossBoundaryPairs']==0
 allfaces=repair._faces(patch);oldlocal=repair._faces(local);assert np.array_equal(allfaces[-len(oldlocal):],oldlocal)
 out,proof=consolidate(oldlocal);assert proof['allOriginalFacesAccounted'];tri=np.concatenate([allfaces[:-len(oldlocal)],out]);assert np.array_equal(tri[:-len(out)],allfaces[:-len(oldlocal)])
 DOC.mkdir();save(DOC/'exact-local-consolidation.json.gz',proof);patch['nativeMesh']['position']=tri.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(tri)*3));patch['nativeMesh']['source']['folklandExactConsolidation']=dict(proofPath=str((DOC/'exact-local-consolidation.json.gz').relative_to(ROOT)),proofSHA256=digest((DOC/'exact-local-consolidation.json.gz').read_bytes()),terrainOnly=True)
 raw=DOC/'unapproved-terrain.json';save(raw,patch);refs.append(raw)
 sourcefiles=[]
 for p in [ROOT/'3d-viewer/city/data/terrain/unnamed147996-private-v1.json',LOCAL/'unapproved-local-surface.json',SRC/'unapproved-complete-parent.json',DOC/'exact-local-consolidation.json.gz']:
  if p!=DOC/'exact-local-consolidation.json.gz':consume(p)
  sourcefiles.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 audit=repair.approve_original_overlap(patch,raw,DOC/'native-overlap.json',sourcefiles);repair.finalize_overlap_evidence(patch,DOC/'native-overlap.json');path=DOC/'candidate-terrain.json';save(path,patch)
 builder=module('folkland_final_validate',HERE/'resolve-pass-indexed-parent-clipping.py');root=ROOT/'3d-viewer/city/data/terrain.json';builder.validate_patch(patch,read(root))
 result=dict(uids=['landsd/264677:0','landsd/225387:0'],terrainValidatorPassed=True,sourceBuildingGeometryChanges=0,priorParentFaces=len(allfaces),finalParentFaces=len(tri),localFacesSaved=proof['savedFaces'],withinExisting100000FaceBudget=len(tri)<=100000,exactLocalSurfaceCertified=True,allOtherParentFacesUnchanged=True,overlapSamples=audit['float32HighestRayAgreement']['samples'],maxRayErrorM=audit['float32HighestRayAgreement']['maxError'],installationApproved=False,nextStep='Full affected-domain and retained-actor/current BASIC neighbour acceptance, four runtime modes and browser verification remain mandatory.')
 save(DOC/'summary.json',result);refs.extend([path,root,HERE/'native_patch_resolution.py',HERE/'exact_runtime_coplanar_consolidation_20261010.py',HERE/'exact_coplanar_boundary_census_20261010.py',HERE/'resolve-pass-indexed-parent-clipping.py'])
 module('folkland_exact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-terrain-consolidation-and-native-validation',refs,result);print(result,flush=True)
if __name__=='__main__':main()
