"""All15 unchanged podium parts against historical complete actual v5 ground.

A raw failed component remains failed. No source contact, tolerance or root credit
is substituted, and this diagnostic is not current acceptance or publication.
"""
from pathlib import Path
import json,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_mesh_components import face_components
BATCH='government-xl-one-peking-podium-original-and-literal-component-footings-diagnostic-v1-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYS=DOC.parent/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010';RUNTIME=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';UID='landsd/233985:0'
def main():
 assert not DOC.exists();s=read(PHYS/'selection.json.gz');row=next(r for r in s['rows'] if r['uid']==UID);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];a=decode_original_world_triangles(raw);parts=face_components(a);assert len(parts)==15
 rt=next(r for r in read(RUNTIME)['rows'] if r['uid']==UID);assert rt['sourceSHA256']==row['sourceSHA256'];literal=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry']).reshape(-1,3,3);assert literal.shape==a.shape and np.isfinite(ground).all()
 results=[]
 for kind,tri in [('completeOriginal',a),('actualLiteralRendered',literal)]:
  for i,ids in enumerate(parts):
   part=tri[ids];path=DOC/(kind+'-part-'+str(i)+'.json.gz');save(path,dict(part=dict(component=i,originalFaceIds=list(map(int,ids)),position=part.reshape(-1).tolist(),index=list(range(part.size//3)),bottomHKPD=float(part[:,:,1].min())),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(ground.size//3))),representation=kind,physicalAccepted=False))
   result=json.loads(subprocess.check_output(['node',str(HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'),str(path)],cwd=ROOT,text=True))
   results.append(dict(representation=kind,part=i,completePartFaces=len(ids),worldBounds=[part.min((0,1)).tolist(),part.max((0,1)).tolist()],strictWholePartFootingResult=result));print(kind,i,result['passed'],result['samples'],len(result['unresolved']),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uid=UID,sourceSHA256=row['sourceSHA256'],historicalManifestSHA256=s['manifestSHA256'],completeOriginalFaces=len(a),completeOriginalParts=15,completeOriginalWorldSHA256=digest(a.tobytes()),completeLiteralWorldSHA256=digest(literal.tobytes()),completeHistoricalDrawnGroundSHA256=digest(ground.tobytes()),rows=results,completeOriginalFacesAccounted=sum(len(ids) for ids in parts),physicalAccepted=False,groundRootsAccepted=False,installationApproved=False,qualification='Independent unchanged strict JS whole-rim footing for every original and actual literal podium part. All raw fails retained, no model/source edits or tolerance changes. Historic v5 candidate ground only; full standalone current foreign/basic/native/whole-facet/role/browser acceptance remains required.'))
 refs=[Path(__file__),PHYS/'result.json',PHYS/'selection.json.gz',RUNTIME,ROOT/row['candidate']['path'],HERE/'exact_mesh_components.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs',HERE/'support-interface.mjs',HERE/'support-contact.mjs',HERE/'triangle-point-index.mjs']
 m=importlib.util.spec_from_file_location('peking_part_footing_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(m);m.loader.exec_module(f);f.freeze(BATCH,'all15-original-and-literal-podium-parts-strict-historical-full-rim-footing-diagnostic-v1',refs,dict(uids=[UID],completeOriginalParts=15,strictFootingPassedParts={kind:[r['part'] for r in results if r['representation']==kind and r['strictWholePartFootingResult']['passed']] for kind in ['completeOriginal','actualLiteralRendered']},physicalAccepted=False,groundRootsAccepted=False,qualification='Complete historical candidate-source footing diagnostic, no current identity/physical/install credit.'))
if __name__=='__main__':main()
