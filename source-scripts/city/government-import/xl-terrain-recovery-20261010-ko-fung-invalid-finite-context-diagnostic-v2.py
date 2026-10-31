"""Validate reported diagnostic minima against actual finite source bounds.

Preserves every raw diagnostic value and source/context bytes. This only records
mathematically impossible face positions; grants no clearance or acceptance.
"""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='xl-terrain-recovery-20261010-ko-fung-invalid-finite-context-diagnostic-v2'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 doc=ROOT/'docs/astra-city/government-import'/BATCH;assert not doc.exists();base=ROOT/'docs/astra-city/government-import';physical=base/'government-xl-terrain-recovery-ko-fung-original-pair-current-physical-v3-20261010';runtime_path=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(runtime_path);selection_path=physical/'selection.json.gz';selected=read(selection_path);results=[];refs=[ref(Path(__file__)),ref(runtime_path),ref(selection_path)]
 for row in selected['rows']:
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];source=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];assert source.shape==world.shape and np.max(np.abs(source-world))<=1e-9
  context_path=base/f"xl-terrain-recovery-20261010-ko-fung-{row['uid'].split('/')[1].split(':')[0]}-complete-context-v1"/'diagnostic.json.gz';contexts=read(context_path)['faces'];assert len(contexts)==len(source);refs.extend([ref(asset),ref(context_path)])
  for i,c in enumerate(contexts):
   if c['minimum'] is None:continue
   point=np.asarray(c['minimum']['position'],float);bounds=np.array([world[i].min(axis=0),world[i].max(axis=0)])
   if point[1]<bounds[0,1] or point[1]>bounds[1,1]:
    results.append(dict(uid=row['uid'],sourceFace=i,completeOriginalVertices=source[i].tolist(),actualRenderedVertices=world[i].tolist(),actualRenderedFaceHeightInterval=bounds[:,1].tolist(),reportedDiagnosticMinimumVerbatim=c['minimum'],reportedPositionOutsideOriginalFiniteHeightInterval=True,rawContextChanged=False,clearanceAccepted=False))
 result=dict(completeSourceFacesChecked=sum(r['native']['model']['triangles'] for r in selected['rows']),invalidFiniteMinimumPositions=results,rawContextChanged=False,sourceGeometryChanges=0,clearanceAccepted=False,fullAcceptance=False,installationApproved=False,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('finite_minimum_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-finite-source-diagnostic-position-validation-v1',[ROOT/r['path'] for r in refs],dict(uids=[r["uid"] for r in selected["rows"]],completeFacesChecked=result['completeSourceFacesChecked'],invalidFiniteDiagnosticPositions=len(results),sourceGeometryChanges=0,rawContextChanged=False,clearanceAccepted=False,fullAcceptance=False))
 print(dict(uids=[r["uid"] for r in selected["rows"]],completeFacesChecked=result['completeSourceFacesChecked'],invalidFinitePositions=len(results),clearanceAccepted=False))
if __name__=='__main__':main()
