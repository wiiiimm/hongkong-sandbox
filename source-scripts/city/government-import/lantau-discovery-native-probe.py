"""Probe a bounded source TIN patch for one Discovery Bay roof buried by coarse terrain."""
import gzip,hashlib,importlib.util,json,shutil,subprocess
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE='government-discovery-bay-1103-20260921';BATCH='government-lantau-discovery-native-probe-20260921';UID='landsd/176056:0'
LOCAL=HERE/'local'/SOURCE;STAGE=HERE/'local'/BATCH;DOC=ROOT/'docs/astra-city/government-import'/BATCH
spec=importlib.util.spec_from_file_location('resolve',HERE/'resolve-pass.py');resolve=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolve)
def read(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def main():
 source=read(ROOT/'docs/astra-city/government-import/government-lantau-final-14-20260921/selection.json.gz')
 row=json.loads(json.dumps(next(x for x in source['rows'] if x['uid']==UID)));entry=row['candidate']['entry']
 exact=next(x for x in read(ROOT/'docs/astra-city/government-import'/SOURCE/'exact-pass-results.json.gz')['rows'] if x['uid']==UID)
 roof=next(x for x in read(ROOT/'docs/astra-city/government-import'/SOURCE/'remaining-roof-visibility.json')['rows'] if x['uid']==UID)
 assert exact['identity']['exactObjectAndCSUID'] and exact['identity']['officialOverlapOfSmallerFootprint']>.98
 assert roof['fullyVisibleUpwardAreaM2']==roof['upwardAreaM2'] and roof['minimumUpwardGapM']>=2.4
 assert exact['foundation']['completeTerrainTriangles']==exact['foundation']['triangles'] and exact['foundation']['minimumGapM']>=-2
 parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path);cells=resolve.rectangle_for(entry['worldBounds'],parent)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 assert all(not resolve.terrain.overlap(cells,p['coarseCells']) for p in (read(ROOT/'3d-viewer'/e['url']) for e in manifest['terrainPatches']))
 sheet=exact['sourceSheet'];src=read(ROOT/'docs/astra-city/government-import'/SOURCE/'source-terrain.json');proof=next(x for x in src['sheets'] if x['sheet']==sheet)
 for member in proof['members']:assert sha(ROOT/member['path'])==member['sha256']
 triangles=np.concatenate([resolve.context.triangles(p) for p in sorted((LOCAL/'source-terrain'/sheet/'decoded').rglob('*.gltf'))])
 bb=resolve.extent(cells,parent);hit=triangles[(triangles[:,:,0].max(axis=1)>=bb[0])&(triangles[:,:,0].min(axis=1)<=bb[2])&(triangles[:,:,2].max(axis=1)>=bb[1])&(triangles[:,:,2].min(axis=1)<=bb[3])]
 assert len(hit)>0
 native_sources=[{k:proof[k] for k in ('sheet','revisionDate','sourceETag','directorySHA256','compactArchiveSHA256')}]
 group={'uids':[UID],'cells':cells}
 patch=resolve.make_patch(group,parent,hit,native_sources,parent_url='city/data/terrain.json',parent_sha256=sha(parent_path),allow_native_below_clamp=True,terrain_triangle_budget=50000)
 terrain=STAGE/'government-native-176056-0.json';save(terrain,patch)
 entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=False,proceduralWindows=False,retainsBasicForm=True,placementReview='Exact government object and Building CSUID, unchanged source mesh and native source TIN terrain within a bounded 70m parent-cell patch. Full roof visible above native source terrain. Script validation only.')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert sha(asset)==entry['sha256'];row['candidate']['path']=str(asset)
 template=read(ROOT/'3d-viewer/city/data/official-models/government-discovery-bay-compute-20260921/catalogue.json');template.update(area='Discovery Bay native terrain probe',counts={'packedModels':1},models=[entry]);save(STAGE/'catalogue.json',template);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 save(DOC/'source-forms.json',{UID:row['source']});save(DOC/'selection.json.gz',{'batch':BATCH,'rows':[row],'manifestSHA256':sha(ROOT/'3d-viewer/city/data/manifest.json'),'aiCalls':0})
 save(DOC/'terrain-candidates.json',[{'path':rel(terrain),'sha256':sha(terrain)}]);save(DOC/'native-proof.json',{'uid':UID,'sourceSHA256':entry['sha256'],'sourceTerrainMembers':proof['members'],'sourceTerrainSheet':sheet,'cells':cells,'patchSHA256':sha(terrain),'patchTriangles':len(patch['nativeMesh']['index'])//3,'roofVisibility':roof,'aiCalls':0,'modelGeometryChanges':0})
 subprocess.run(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')],cwd=ROOT,check=True)
 subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(DOC/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT,check=True)
 m=read(DOC/'metrics.json')['rows'][0];v=read(DOC/'validation.json')['results'][0]
 print(json.dumps({'patchTriangles':len(patch['nativeMesh']['index'])//3,'metrics':{k:m.get(k) for k in ('error','minSurfaceGap','minLowGap','maxLowGap','maxSamplerDelta','missingTerrain')},'validation':{k:v.get(k) for k in ('outcome','concerns','error')}}))
if __name__=='__main__':main()
