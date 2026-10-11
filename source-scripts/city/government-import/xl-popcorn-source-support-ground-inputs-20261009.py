"""Exact whole-original mall and original source terrain contact inputs, no edits."""
import importlib.util,numpy as np
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009'
terrain=read(ROOT/'docs/astra-city/government-import/government-xl-popcorn-complete-original-source-terrain-20261009/all-original-source-terrain-foundation.json.gz')
sp=importlib.util.spec_from_file_location('grounddecode',HERE/'xl-second-pass.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
paths=[ROOT/p for s in terrain['sourceSheets'] for p in s['terrainPaths']]
t=np.concatenate([m.terrain_triangles(p) for p in paths])
source=next(r for r in read(PRIOR/'exact-original-contact-inputs.json.gz')['rows'] if r['uid']=='landsd/295538:0')
terrainrow={'uid':'source-terrain:11-NE-25B','position':t.flatten().tolist(),'index':list(range(len(t)*3)),
            'triangles':len(t),'worldTriangleSHA256':digest(t.astype('<f8').tobytes()),
            'worldBounds':[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()]}
save(DOC/'exact-original-mall-ground-contact-inputs.json.gz',{'source':source,'terrain':terrainrow,
     'terrainProvenance':terrain['sourceSheets'],'geometryChanges':0,'physicalSupportAccepted':False})
print({'originalMallTriangles':source['triangles'],'originalTerrainTriangles':len(t)})
