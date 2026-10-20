"""Complete original and actual-renderer tower-pair separation, no model changes."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-neighbour-clearance-v1-20261020';DOC=BASE/BATCH;APP=BASE/'government-xl-heya-aqua-current-applicability-v2-20261020';SUP=BASE/'government-xl-heya-aqua-current-support-v3-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [APP,SUP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 app=take(APP/'applicability.json');assert {r['uid']for r in app['touchingNativeActors']}=={'landsd/184285:0','landsd/184286:0'};sources=take(SUP/'support-inputs.json')['sources'];target=next(r for r in sources if r['uid']=='landsd/184287:0');other=next(r for r in app['touchingNativeActors']if r['uid']=='landsd/184286:0');catpath=ROOT/other['catalogue'];cat=take(catpath);entry=next(e for e in cat['models']if e['uid']==other['uid']);assert entry==other['entry'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(manifestpath);forms=[]
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];data=read(p);found=[b for b in data['buildings']if b['uid']==other['uid']]
  if found:refs.append(p);forms.extend(found)
 assert len(forms)==1;otherpath=catpath.parent/entry['asset'];assert digest(otherpath.read_bytes())==entry['sha256'];refs.append(otherpath)
 rows=[dict(uid=target['uid'],entry=target['candidate']['entry'],building=target['source']['building'],path=target['candidate']['path']),dict(uid=other['uid'],entry={**entry,'rootTranslation':cat['rootTranslation']},building=forms[0],path=str(otherpath.relative_to(ROOT)))]
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.append(pointer)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(read(pointer)['snapshotId'],other['uid'])).fetchone()==('installed-verified',entry['sha256'])
 save(DOC/'input.json.gz',dict(rows=rows,currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in manifest['officialModelCatalogues']],evidenceRefs=[ref(p)for p in refs]))
 tool=HERE/'heya_aqua_neighbour_attributes_v1_20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);cap=read(DOC/'attributes.json.gz');assert len(cap['rows'])==2 and not cap['rejected'];refs.extend([tool,HERE/'exact_packed_world_geometry_20261009.py']);modes={'original':{r['uid']:decode_original_world_triangles((ROOT/r['path']).read_bytes())for r in rows}}
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:modes[mode]={r['uid']:np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in cap['rows']}
 results=[]
 for mode,tri in modes.items():
  projections=[unary_union([p for t in tri[r['uid']]if(p:=Polygon(t[:,[0,2]])).area>0])for r in rows];intersection=projections[0].intersection(projections[1]).area;distance=projections[0].distance(projections[1]);assert intersection==0 and distance>0
  results.append(dict(mode=mode,projectionIntersectionM2=intersection,minimumHorizontalSeparationM=distance,completeFacesByUid={u:len(t)for u,t in tri.items()}))
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=[r['uid']for r in rows],rows=results,allCurrentNativeActorsNominated=6781,touchingActorsAccounted=['landsd/184285:0','landsd/184286:0'],retainedTowerInstalledVerified=True,retainedGeometryChanges=0,terrainChanges=0,installationApproved=False)
 save(DOC/'clearance.json',result);module('heya_neighbour_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-representation-neighbour-original-separation',list(dict.fromkeys(refs)),result);print(results,flush=True)
if __name__=='__main__':main()
