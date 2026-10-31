"""Audit reciprocal spatial mismatches against archived government glTF bytes."""
from pathlib import Path
import zipfile,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-reciprocal-source-audit-v1-20261020';DOC=BASE/BATCH;REC=BASE/'government-xl-plaza-ascot-assembly-original-recovery-v1-20261020';MATRIX=BASE/'government-xl-plaza-ascot-spatial-matrix-v1-20261020'
UIDS=['landsd/163911:0','landsd/163908:0','landsd/164116:0','landsd/163696:0']
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [REC,MATRIX]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=take(REC,REC/'recovery.json')['rows'];matrix=take(MATRIX,MATRIX/'matrix.json')['rows'];helper=module('ascot_original_raw_decode',HERE/'xl-second-pass.py');refs.append(HERE/'xl-second-pass.py');out=[]
 for row in rows:
  if row['uid'] not in UIDS:continue
  sheet=row['native']['sheet'];folder=HERE/'local'/REC.name/'sheets'/sheet;archive=folder/'original'/(sheet+'.zip');assert digest(archive.read_bytes())==pins[REC][str(archive.relative_to(ROOT))];refs.append(archive);source=row['native']['model']['sourceEntry'];path=folder/'decoded'/source;gltf=read(path)
  with zipfile.ZipFile(archive) as z:
   assert z.read(source)==path.read_bytes();refs.append(path)
   for buffer in gltf['buffers']:
    uri=buffer['uri'];p=path.parent/uri;name=str(Path(source).parent/uri);assert p.resolve().is_relative_to(folder.resolve());assert z.read(name)==p.read_bytes();refs.append(p)
  original=helper.context.triangles(path);asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);packed=decode_original_world_triangles(asset.read_bytes());assert original.shape==packed.shape;delta=float(np.abs(original-packed).max());assert delta<.002
  spatial=next(r for r in matrix if r['uid']==row['uid']);out.append(dict(uid=row['uid'],modelId=row['modelId'],sourceSHA256=row['sourceSHA256'],archiveSHA256=digest(archive.read_bytes()),rawGLTFSHA256=digest(path.read_bytes()),maximumRawToPackedCoordinateDeltaM=delta,rawBounds=[original.min((0,1)).tolist(),original.max((0,1)).tolist()],packedBounds=spatial['sourceBounds'],recordedTarget=spatial['recordedTarget'],intersectingForms=spatial['intersectingForms'],sourceMetadata={k:gltf.get(k)for k in ['asset','extras','scene']},sourceNodes=gltf.get('nodes'),installationApproved=False))
 summary=dict(uids=UIDS,rows=out,sourceGeometryChanges=0,identityReassignmentApproved=False,installationApproved=False,qualification='Archived raw glTF and referenced buffers byte-verified; source-order coordinates reproduce packed placement within measured precision. Apparent reciprocal identity mismatch predates this capture. No ID reassignment or source transform change authorized by overlap alone.')
 save(DOC/'audit.json',summary);module('ascot_reciprocal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'archived-raw-source-reciprocal-spatial-audit',list(dict.fromkeys(refs)),summary);print([(r['uid'],r['maximumRawToPackedCoordinateDeltaM'])for r in out],flush=True)
if __name__=='__main__':main()
