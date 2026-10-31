"""Complete original podium footprint differences and adjoining source attribution."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-assembly-projection-v2-20261018';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-park-avenue239350-current-identity-runtime-v3-20261018';UID='landsd/239350:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
 row=read(PRIOR/'selection.json.gz')['rows'][0];tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert len(tri)==row['triangles'];forms={f['uid']:f for f in read(ROOT/'3d-viewer'/row['source']['tile'])['buildings']}
 def proj(t):
  ps=shapely.polygons(t[:,:,[0,2]]);return shapely.union_all(ps[shapely.area(ps)>0])
 own=proj(tri);f=forms[UID];target=Polygon(f['rings'][0],f['rings'][1:]);missing=target.difference(own);excess=own.difference(target)
 context=read(PRIOR/'239350:0-identity.json')['context']['identity'];uids=[x['uid'] for x in context['intersectingForms'] if x['uid']!=UID]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs=[Path(__file__),PRIOR/'result.json',manifest,*[ROOT/p for p in pins]];models={}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid'] in uids:
    assert e['uid'] not in models;models[e['uid']]=(p,e);refs.append(p)
 restored=BASE/'government-xl-park-avenue239350-companion-restored-v1-20261018';receipt=read(restored/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs.append(restored/'result.json')
 for e in receipt['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256'];assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
 for companion in read(restored/'restored.json')['rows']:
  uid=companion['uid'];assert uid not in models and uid in uids
  entry=dict(companion['candidate']);asset=ROOT/companion['assetPath'];assert asset.parent.parent/entry['asset']==asset
  models[uid]=(asset.parent.parent/'catalogue.json',entry)
 remaining=missing;credits=[];overlays=[]
 for uid in uids:
  ff=forms[uid];fp=Polygon(ff['rings'][0],ff['rings'][1:]);entry=dict(uid=uid,name=ff.get('name'),structureType=ff.get('structureType'),formAreaM2=fp.area,excessInFormM2=excess.intersection(fp).area,sourceAvailable=uid in models)
  if uid in models:
   cat,e=models[uid];p=cat.parent/e['asset'];assert digest(p.read_bytes())==e['sha256'];t=decode_original_world_triangles(p.read_bytes());projection=proj(t);refs.append(p);overlays.append((uid,projection))
   contribution=remaining.intersection(projection);remaining=remaining.difference(projection)
   entry.update(sourceSHA256=e['sha256'],sourceFaces=len(t),sourceProjectionOverlapM2=own.intersection(projection).area,newlyCoveredMissingM2=contribution.area)
  credits.append(entry)
 features=[]
 def parts(g):
  if g.geom_type=='Polygon':return [g]
  return [p for c in getattr(g,'geoms',[]) for p in parts(c)]
 for kind,geom in [('missing',missing),('excess',excess),('remainingAfterInstalledSources',remaining)]:
  for i,p in enumerate(sorted(parts(geom),key=lambda p:-p.area)):
   features.append(dict(type='Feature',properties=dict(kind=kind,index=i,areaM2=p.area,bounds=list(p.bounds)),geometry=mapping(p)))
 assert abs(missing.area-remaining.area-sum(x.get('newlyCoveredMissingM2',0) for x in credits))<1e-6
 save(DOC/'differences.geojson',dict(type='FeatureCollection',features=features));save(DOC/'summary.json',dict(uid=UID,sourceSHA256=row['sourceSHA256'],sourceFaces=len(tri),targetAreaM2=target.area,sourceAreaM2=own.area,missingM2=missing.area,excessM2=excess.area,remainingMissingM2=remaining.area,adjoiningSources=credits,identityAccepted=False,sourceGeometryChanges=0))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Polygon as Patch
 fig,axes=plt.subplots(1,2,figsize=(14,8),dpi=170)
 def draw(ax,g,color,alpha):
  for p in parts(g):
   ax.add_patch(Patch(np.asarray(p.exterior.coords),facecolor=color,edgecolor=color,alpha=alpha))
   for ring in p.interiors:ax.add_patch(Patch(np.asarray(ring.coords),facecolor='white',edgecolor=color,alpha=1))
 for ax in axes:
  draw(ax,own,'#4396a8',.35);draw(ax,target,'#888888',.15)
  ax.set_xlim(min(own.bounds[0],target.bounds[0])-8,max(own.bounds[2],target.bounds[2])+8);ax.set_ylim(max(own.bounds[3],target.bounds[3])+8,min(own.bounds[1],target.bounds[1])-8);ax.set_aspect('equal');ax.set_xlabel('East (m)');ax.set_ylabel('South (m)')
 draw(axes[0],missing,'#d32f3f',.8);draw(axes[0],excess,'#efaa25',.8);axes[0].set_title('Red: target missing from source; gold: source extension')
 for uid,p in overlays:
  clip=p.intersection(target.buffer(5));draw(axes[1],clip,'#5d9a49',.3)
 draw(axes[1],remaining,'#d32f3f',.8);axes[1].set_title('Remaining red after installed and recovered originals')
 fig.tight_layout();fig.savefig(DOC/'whole-source-differences.png');plt.close(fig)
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
 refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 out=module('park_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue239350-complete-source-assembly-projection-v1',list(set(refs)),dict(uids=[UID],missingM2=missing.area,remainingMissingM2=remaining.area,identityAccepted=False,publication=False))
 print(dict(jobId=out['jobId'],missingM2=missing.area,remainingMissingM2=remaining.area,adjoiningSources=credits),flush=True)
if __name__=='__main__':main()
