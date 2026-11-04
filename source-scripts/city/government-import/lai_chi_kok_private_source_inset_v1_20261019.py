"""Private source-terrain diagnostic; model and viewer files are untouched."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import inset_faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-private-source-inset-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-lai-chi-kok-exposed-source-nomination-v2-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),SRC/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 selection=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz';row=next(x for x in read(selection)['rows']if x['uid']=='landsd/281463:0');asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw)
 source=read(SRC/'surface-nomination.json.gz');nominees=np.asarray(source['triangles']);assert abs(source['summary']['projectedOverlapM2'])<1e-6
 groundpath=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/281463:0-ground.json.gz';terrain=np.asarray(read(groundpath)['completeAdjoiningTerrain']);lo,hi=tri.min((0,1)),tri.max((0,1));mask=(terrain[:,:,0].max(1)>=lo[0]-2)&(terrain[:,:,0].min(1)<=hi[0]+2)&(terrain[:,:,2].max(1)>=lo[2]-2)&(terrain[:,:,2].min(1)<=hi[2]+2);terrain=terrain[mask]
 out,proof=inset_faces(terrain,nominees);save(DOC/'inset-proof.json.gz',proof);save(LOCAL/'private-source-terrain.json.gz',dict(triangles=out.tolist(),sourceGeometryChanges=0,viewerChanged=False))
 for i,lineage in enumerate(proof['lineage']):
  if lineage['kind']=='unchanged-terrain':assert np.array_equal(out[i],terrain[lineage['face']])
 helper=module('lai_inset_foundation',HERE/'xl-final-script-pass.py');b=row['source']['building'];foundation=helper.foundation_context(tri,out,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 oldpath=ROOT/'3d-viewer/city/data/government-native-273000-0.json';old=repair._faces(read(oldpath));retained_out,retained_proof=inset_faces(old,nominees);save(DOC/'retained-terrain-impact.json.gz',dict(retainedTerrainSHA256=digest(oldpath.read_bytes()),proof=retained_proof,diagnosticOnly=True,retainedActorReacceptanceRequired=True))
 summary=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],originalGroundFaces=len(terrain),privateGroundFaces=len(out),changedGroundFaces=len(proof['changedTerrainFaceIndices']),insetAreaM2=proof['removedProjectedAreaM2'],retainedTerrainChangedFaces=len(retained_proof['changedTerrainFaceIndices']),retainedTerrainInsetAreaM2=retained_proof['removedProjectedAreaM2'],foundation={k:v for k,v in foundation.items()if k!='components'},sourceGeometryChanges=0,viewerChanged=False,installationApproved=False)
 save(DOC/'summary.json',summary);refs.extend([LOCAL/'private-source-terrain.json.gz',HERE/'source_surface_inset.py',HERE/'test_source_surface_inset.py',HERE/'xl-final-script-pass.py',HERE/'native_patch_resolution.py'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 module('lai_inset_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-private-original-source-terrain-inset-diagnostic',refs,dict(uids=[row['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
