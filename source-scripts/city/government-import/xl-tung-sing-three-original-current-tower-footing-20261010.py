"""Fresh actual drawn-ground full-rim anchor for the complete original platform."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
BATCH='government-xl-tung-sing-three-original-current-tower-footing-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=DOC.parent/'government-xl-tung-sing-three-original-literal-parent-physical-20261010';RUNTIME=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';UID='landsd/53800:0'
def main():
 assert not DOC.exists();s=read(PHYSICAL/'selection.json.gz');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==s['manifestSHA256'];r=next(v for v in s['rows'] if v['uid']==UID);raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];a=decode_original_world_triangles(raw);part=components(a)['components'][361];ids=part['faceIndices'];t=a[ids];g=next(v for v in read(RUNTIME)['rows'] if v['uid']==UID);assert g['sourceSHA256']==r['sourceSHA256'];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3)
 paths=[Path(__file__),PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',RUNTIME,ROOT/r['candidate']['path'],ROOT/'3d-viewer/city/data/manifest.json',HERE/'support-interface.mjs',HERE/'exact_packed_world_geometry_20261009.py',HERE/'source_closed_components.py'];save(DOC/'complete-current-original-platform-anchor-input.json.gz',{'uid':UID,'sourceSHA256':r['sourceSHA256'],'worldTriangleSHA256':digest(a.astype('<f8').tobytes()),'manifestSHA256':s['manifestSHA256'],'part':{'component':361,'originalFaceIds':ids,'position':t.reshape(-1).tolist(),'index':list(range(t.size//3)),'bottomHKPD':float(t[:,:,1].min())},'terrain':{'position':ground.reshape(-1).tolist(),'index':list(range(len(ground))),'worldTriangleSHA256':digest(ground.astype('<f8').tobytes())},'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in paths},'physicalAccepted':False})
if __name__=='__main__':main()
