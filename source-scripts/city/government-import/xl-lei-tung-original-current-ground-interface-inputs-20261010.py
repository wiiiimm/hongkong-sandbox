"""All original parts vs complete fresh actually drawn ground, no support waiver."""
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from lei_tung_lower_platform_current_bound_identity_20261010 import DOC as INPUT,UID,PLATFORM
DOC=INPUT.parent/'government-xl-lei-tung-original-current-ground-interfaces-20261010'
PHYSICAL=INPUT.parent/'government-xl-lei-tung-paired-original-literal-parent-physical-20261010'
RUNTIME=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==read(INPUT/'current-inputs.json.gz')['manifestSHA256'];runtime=read(RUNTIME)['rows'];rows=[];refs=[Path(__file__),INPUT/'selection.json.gz',RUNTIME,PHYSICAL/'result.json',PHYSICAL/'foundation.json',manifest,HERE/'support-interface.mjs',HERE/'source_closed_components.py',HERE/'exact_packed_world_geometry_20261009.py']
 for r in read(INPUT/'selection.json.gz')['rows']:
  path=ROOT/r['candidate']['path'];raw=path.read_bytes();assert digest(raw)==r['sourceSHA256'];a=decode_original_world_triangles(raw);geom=next(v for v in runtime if v['uid']==r['uid']);assert geom['sourceSHA256']==r['sourceSHA256'];ground=np.asarray(geom['drawnGroundGeometry']).reshape(-1,3);parts=[]
  for i,c in enumerate(components(a)['components']):
   v=a[c['faceIndices']];parts.append({'component':i,'bottomHKPD':float(v[:,:,1].min()),'originalFaceIds':c['faceIndices'],'position':v.reshape(-1).tolist(),'index':list(range(v.size//3)),'worldBounds':[v.min((0,1)).tolist(),v.max((0,1)).tolist()]})
  rows.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'worldTriangleSHA256':digest(a.astype('<f8').tobytes()),'wholeOriginalFaces':len(a),'parts':parts,'terrain':{'position':ground.reshape(-1).tolist(),'index':list(range(len(ground))),'worldTriangleSHA256':digest(ground.astype('<f8').tobytes()),'actualDrawnGround':geom['drawnGround']}});refs.append(path)
 save(DOC/'complete-original-current-footing-inputs.json.gz',{'rows':rows,'basis':'fresh-complete-actual-runtime-drawn-ground','manifestSHA256':msha,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs},'sourceGeometryChanges':0,'physicalAccepted':False});print({'parts':sum(len(v['parts']) for v in rows),'sourceFaces':sum(v['wholeOriginalFaces'] for v in rows)},flush=True)
if __name__=='__main__':main()
