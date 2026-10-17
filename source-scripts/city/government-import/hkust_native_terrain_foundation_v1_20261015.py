"""Acquire exact government sheet terrain and diagnose both unchanged HKUST originals."""
from pathlib import Path
import zipfile,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hkust-native-terrain-foundation-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PACKET=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014';CACHE=HERE/'local/government-xl-eight-further-original-closures-20261008/sheets/12-NW-6A/directory'
def main():
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim('hkust-native-'+str(uuid.uuid4()),['original-terrain-acquisition:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);f=module('hkust_existing_native_pipeline',HERE/'xl-final-script-pass.py');f.s.LOCAL=LOCAL
  directory=read(CACHE/'result.json');assert digest((CACHE/'zip-directory.bin').read_bytes())==directory['directorySHA256'];directory['models']=[]
  acquired=f.s.acquire(directory,CACHE/'zip-directory.bin',LOCAL/'original',include_terrain=True);save(DOC/'acquisition.json',acquired)
  paths=[Path(__file__),CACHE/'result.json',CACHE/'zip-directory.bin',LOCAL/'original/download.json'];terrain=[]
  with zipfile.ZipFile(LOCAL/'original/12-NW-6A.zip') as z:
   for name in z.namelist():
    if name.startswith('TERRAIN') and name.endswith(('.gltf','.bin')):
     p=LOCAL/'terrain'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));paths.append(p)
     if name.endswith('.gltf'):terrain.append(p)
  assert terrain;ground=np.concatenate([f.s.terrain_triangles(p) for p in terrain]);assert np.isfinite(ground).all();save(DOC/'native-ground.json.gz',{'completeOriginalTerrainTriangles':ground.tolist(),'terrainPaths':[str(p.relative_to(ROOT)) for p in terrain],'terrainGeometryChanges':0})
  prior=read(BASE/'government-xl-hkust-uncovered-target-partition-v1-20261015/result.json');pins={r['path']:r['sha256'] for r in prior['evidenceRefs']};reportp=PACKET/'two-original-scope-interface-output-v1/result.json';assert digest(reportp.read_bytes())==pins[str(reportp.relative_to(ROOT))];report=read(reportp);forms={x['uid']:x for x in report['currentAllSixFormsVerbatim']};rows=[];paths += [reportp,BASE/'government-xl-hkust-uncovered-target-partition-v1-20261015/result.json']
  for ref in report['arrayRefs']:
   p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];a=read(p);s=a['sourceTuple'];asset=ROOT/s['originalAssetPath'];assert digest(asset.read_bytes())==s['sourceSHA256'];tri=np.asarray(a['completeOrderedOriginalTriangles']);assert len(tri)==s['originalFaces'];foot=f.form_polygon(forms[s['uid']]);foundation=f.foundation_context(tri,ground,foot);rows.append({'uid':s['uid'],'sourceSHA256':s['sourceSHA256'],'originalFaces':len(tri),'nativeTerrainFaces':len(ground),'foundation':foundation});paths += [p,asset];assert reservations.heartbeat(lease,ttl=3600)['ok'];print(s['uid'],foundation,flush=True)
  save(DOC/'foundation.json',{'rows':rows,'qualification':'Existing source-native foundation diagnostic only, no live terrain, complete-continuous/four-world or neighbour acceptance.'});paths.extend(p for p in (LOCAL/'terrain-repairs').rglob('*') if p.is_file())
  module('hkust_native_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hkust-original-native-terrain-foundation-v1',paths,{'uids':report['uids'],'rows':rows,'sourceGeometryChanges':0,'nextStep':'If native ground resolves burial, prepare a source-preserving private patch with full affected-parent scope; otherwise attribute concrete remaining source/native failures. Identity gap and support review remain independent.'})
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
