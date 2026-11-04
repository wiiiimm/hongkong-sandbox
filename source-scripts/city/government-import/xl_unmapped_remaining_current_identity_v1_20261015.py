"""Complete original projection/current-form comparison for remaining unmapped XL sources."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unmapped-remaining-current-identity-v1-20261015';DOC=BASE/BATCH
IDS={'B349971856402063C0','B352981210001063C0'}
def main():
 assert not DOC.exists();recovery=BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json';sources=[r for r in read(recovery)['rows']if r['modelId']in IDS];assert len(sources)==2
 final=module('unmapped_current_projection',HERE/'xl-final-script-pass.py');manifest=ROOT/'3d-viewer/city/data/manifest.json';pins={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())};rows=[];refs=[Path(__file__),recovery,HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'];native={e['uid']:e for u in read(manifest)['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/u)['models']}
 for source in sources:
  asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));projection=final.projection(tri);forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);matches=[]
  for b,poly,tile in forms:
   path='3d-viewer/'+tile;pins[path]=digest((ROOT/path).read_bytes());area=projection.intersection(poly).area
   if area<=0:continue
   matches.append({'uid':b['uid'],'name':b.get('name'),'buildingCSUID':b.get('buildingCSUID'),'structureType':b.get('structureType'),'base':b['base'],'height':b['height'],'intersectionM2':area,'targetCoverage':area/poly.area,'sourceCoverage':area/projection.area,'centroidDistanceM':projection.centroid.distance(poly.centroid),'verticalOverlapContext':final.vertical_overlap(tri,poly),'strictIdentityFit':area/poly.area>=.98 and projection.centroid.distance(poly.centroid)<=1,'installedNative':b['uid']in native,'viewerForm':b,'tile':tile})
  rows.append({'sourceKey':source['sourceKey'],'sourceSHA256':source['sourceSHA256'],'modelId':source['modelId'],'completeFaces':len(tri),'worldBounds':[lo.tolist(),hi.tolist()],'completeProjectionAreaM2':projection.area,'matches':matches,'identityAccepted':False,'physicalAcceptance':False})
 DOC.mkdir();save(DOC/'context.json',{'rows':rows,'currentPins':pins,'newlyInstalled':0,'sourceGeometryChanges':0})
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 module('unmapped_current_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-remaining-unmapped-complete-current-projection',refs,{'uids':sorted({m['uid']for r in rows for m in r['matches']}),'sources':[{'modelId':r['modelId'],'sourceKey':r['sourceKey'],'strictIdentityMatches':[m['uid']for m in r['matches']if m['strictIdentityFit']]}for r in rows],'fullAcceptance':False,'newlyInstalled':0})
 for r in rows:print(r['modelId'],[{k:v for k,v in m.items()if k not in ['viewerForm','verticalOverlapContext']}for m in r['matches']],flush=True)
if __name__=='__main__':main()
