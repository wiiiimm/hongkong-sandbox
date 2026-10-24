"""Complete station foundation and continuous minima across all captured coordinate modes."""
from pathlib import Path
import uuid,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_original_projected_uncovered_regions_20261010 import diagnose
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-four-world-ground-v1-20261015';DOC=BASE/BATCH
CAP=BASE/'government-xl-ets-basic-ground-capture-v1-20261015';ATTR=BASE/'government-xl-ets-actual-render-attributes-v2-20261015'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for folder in [CAP,ATTR]:
  r=read(folder/'result.json');refs.append(folder/'result.json')
  for q in r['evidenceRefs']:
   assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 a=read(ATTR/'attributes.json.gz')['rows'];assert len(a)==1;a=a[0];source=next(s for s in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if s['modelId']=='B360171738601063C0');asset=ROOT/source['asset']['path'];refs.append(asset);assert digest(asset.read_bytes())==a['sourceSHA256']==source['sourceSHA256'];worlds={'original':decode_original_world_triangles(asset.read_bytes())};ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
 for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[key]).reshape(-1,3)[ix]
 ground=np.asarray(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;g=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys);f=module('stanford_four_foundation',HERE/'xl-final-script-pass.py');binding=read(BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json')['rows'];b=next(r for r in binding if r['modelId']==source['modelId']);target=shapely.union_all([shapely.Polygon(x['viewerForm']['rings'][0],x['viewerForm']['rings'][1:])for x in b['bindings']]);claim=reservations.claim('stanford-four-world-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];cache={};summaries=[]
 try:
  DOC.mkdir()
  for mode,t in worlds.items():
   assert len(t)==10610;sha=digest(t.astype('<f8').tobytes())
   if sha in cache:summaries.append({**cache[sha],'mode':mode,'reusedExactWholeTriangleEquality':True});continue
   norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(norm,axis=1);rows=[];uncovered=[];warnings=[]
   for i,face in enumerate(t):
    c=face_ground_context(face,g,polys,tree)if length[i]>0 else degenerate_ground_context(face,g,polys,tree)
    if not c['groundProjectionCovered']:
     exact=diagnose(face,ground);c['exactCoverage']=exact;warnings.append(i)
     if not exact['exactProjectionCovered']:uncovered.append(i)
    rows.append(c)
    if i%1000==0:assert reservations.heartbeat(lease)['ok'];print(mode,i,len(t),flush=True)
   foundation=f.foundation_context(t,ground,target);failed=[i for i,c in enumerate(rows)if c.get('minimum')and c['minimum']['minimumGapM']<-.5];out={'mode':mode,'worldSHA256':sha,'completeFaces':len(t),'continuousBelowHalfMetreFaces':failed,'exactUncoveredFaces':uncovered,'floatingWarningsExactlyReplayed':warnings,'foundation':foundation,'fullAcceptance':False};cache[sha]=out;summaries.append(out);save(DOC/(mode+'-faces.json.gz'),{'rows':rows});print(mode,'buried',len(failed),'uncovered',len(uncovered),'foundation',foundation['completeTerrainTriangles'],flush=True)
  save(DOC/'summary.json',{'rows':summaries,'uniqueWorlds':len(cache),'allFourModesCovered':all(not r['exactUncoveredFaces']for r in summaries),'allFourModesUnburied':all(not r['continuousBelowHalfMetreFaces']for r in summaries),'fullAcceptance':False})
  refs.extend(HERE/n for n in ['xl-final-script-pass.py','exact_packed_world_geometry_20261009.py','original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','exact_original_projected_uncovered_regions_20261010.py'])
  module('freeze_stanford_four_ground',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-station-four-world-source-foundation-and-coverage-v1',refs,{'uids':['landsd/323703:0'],'rows':summaries,'fullAcceptance':False})
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
