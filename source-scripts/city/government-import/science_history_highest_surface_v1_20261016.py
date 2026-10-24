"""Verify actual highest-surface semantics for unchanged shared museum terrain."""
from pathlib import Path
import copy,subprocess
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-history-highest-surface-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-science-history-overlap-diagnostic-v1-20261016';CAND=BASE/'government-xl-science-history-combined-private-terrain-v2-20261016'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not LOCAL.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={q['path']:q['sha256'] for q in r['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 patch=read(CAND/'pre-validation-terrain.json');patch['id']=BATCH;parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);DOC.mkdir();LOCAL.mkdir();raw=DOC/'unapproved-terrain.json';save(raw,patch)
 rows=read(PRIOR/'overlap-pairs.json.gz')['rows'];assert len(rows)==38;proofs=[];count=0;maxerror=0
 for row in rows:
  poly=shapely.from_geojson(row['intersectionGeoJSON']);coords=shapely.get_coordinates(poly);errors=[]
  for face in np.asarray(row['faceVertices']):
   a,b,c=face;u=b-a;v=c-a;delta=coords-a[[0,2]];det=u[0]*v[2]-u[2]*v[0];assert det!=0;s=(delta[:,0]*v[2]-delta[:,1]*v[0])/det;t=(u[0]*delta[:,1]-u[2]*delta[:,0])/det;bary=a[1]+s*u[1]+t*v[1];n=np.cross(u,v);plane=a[1]-(n[0]*delta[:,0]+n[2]*delta[:,1])/n[1];errors.append(float(np.max(np.abs(bary-plane))));count+=len(coords)
  maxerror=max(maxerror,*errors);proofs.append(dict(faces=row['faces'],perFaceEquationErrorBoundM=errors,overlapHeightDifferenceRetainedM=row['maximumHeightDifferenceM']))
 assert maxerror<.01
 m=patch['nativeMesh'];t=np.asarray(m['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];polys=shapely.polygons(t[:,:,[0,2]]);areas=shapely.area(polys);ps=polys[areas>1e-10];excess=float(shapely.area(ps).sum()-shapely.union_all(ps).area)
 sourcefiles=[raw,HERE/'resolve-pass.py',HERE/'science_history_combined_private_terrain_v2_20261016.py',PRIOR/'overlap-pairs.json.gz']
 for item in patch['meta']['source']['nativeSources']:
  p=ROOT/item['path'];assert ref(p)['sha256']==item['sha256'];sourcefiles += [q for q in p.parent.iterdir() if q.suffix in ['.gltf','.bin']]
 audit=dict(stagedGeometrySha256=ref(raw)['sha256'],nativeProjectedExcessM2=excess,float32HighestRayAgreement=dict(samples=count,maxError=maxerror,rows=proofs,method='Complete positive overlap polygons; affine barycentric and plane height equations agree at every polygon vertex. MAX difference is bounded by the largest per-face equation error. This proves the height equations, not browser or GPU acceptance.'),source=dict(files=[ref(p) for p in dict.fromkeys(sourcefiles)]),qualification='Distinct overlapping surface heights are allowed by existing highest-native-surface contract. The previous four-millimetre pair-height diagnostic is retained but is not sampler-versus-renderer error. No facets or heights removed, flattened or moved.')
 evidence=DOC/'highest-surface-proof.json';save(evidence,audit);m['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=excess,evidencePath=ref(evidence)['path'],evidenceSHA256=ref(evidence)['sha256']);helper=module('museum_highest_validator',HERE/'resolve-pass.py');helper.validate_patch(patch,parent);save(DOC/'private-terrain.json',patch)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);oldurl='city/data/government-xl-history-museum-private-browser-v1-20261016-terrain.json';oldpath=ROOT/'3d-viewer'/oldurl;assert any(p['url']==oldurl for p in manifest['terrainPatches']);candidate=dict(path=ref(DOC/'private-terrain.json')['path'],sha256=ref(DOC/'private-terrain.json')['sha256'],replaces=dict(url=oldurl,sha256=ref(oldpath)['sha256'],retainedUids=['landsd/4759:0']))
 save(DOC/'terrain-candidates.json',[candidate]);science=read(BASE/'government-xl-science-museum-current-ground-v1-20261016/selection.json.gz')['rows'][0];history=copy.deepcopy(read(BASE/'government-xl-history-museum-current-ground-v1-20261016/selection.json.gz')['rows'][0]);selection=[science,history]
 for row in selection:
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==row['uid'])==row['source']['building'];row['source']['tileSHA256']=ref(tile)['sha256']
 save(DOC/'selection.json.gz',dict(rows=selection,manifestSHA256=ref(manifestpath)['sha256']));tool=HERE/'acceptance-metrics-retained-group-parent.mjs';rel=lambda p:str(p.relative_to(ROOT));cmd=['node',str(tool),'--selection',rel(DOC/'selection.json.gz'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]
 # Each frozen row points to its exact existing asset; the metrics worker uses row.candidate.path.
 with (DOC/'worker.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 metrics=read(DOC/'metrics.json');assert not any(row.get('error') for row in metrics['rows']);summary=dict(validatorPassed=True,sourceFaces=len(t),all38OverlapPairsProved=True,equationErrorM=maxerror,metrics=metrics['rows'],sourceBuildingGeometryChanges=0,terrainFacetChanges=0,neighbourChecksPending=True,fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs += [parentpath,oldpath,*sourcefiles,LOCAL/'runtime-geometry.json.gz',HERE.parent/'island-detail-integration/native_terrain_validation.py']
 r=module('museum_highest_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'shared-museum-unchanged-highest-surface-and-production-metrics-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/80343:0','landsd/4759:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
