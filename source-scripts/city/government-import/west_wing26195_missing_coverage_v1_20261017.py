"""Attribute the entire missing West Wing footprint to unchanged paired sources.
Diagnostic only: no identity waiver, source edit or publication.
"""
from pathlib import Path
import uuid
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-missing-coverage-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015';UID='landsd/26195:0'
def main():
 assert not DOC.exists();old=read(PRIOR/'projection.json');source=next(r for r in old['rows']if r['uid']==UID)
 require_remaining(BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json',UID,source['sourceSHA256'])
 receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={r['path']:r['sha256']for r in receipt['evidenceRefs']};assert pins[str((PRIOR/'projection.json').relative_to(ROOT))]==digest((PRIOR/'projection.json').read_bytes())
 tile=ROOT/'3d-viewer/city/data/tiles/0_0.json';forms={r['uid']:r for r in read(tile)['buildings']};target=Polygon(forms[UID]['rings'][0],forms[UID]['rings'][1:]);refs=[Path(__file__),tile,PRIOR/'projection.json',PRIOR/'result.json'];projections={};counts={}
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  for row in old['rows']:
   candidates=[q for q in old['inputRefs']if q['sha256']==row['sourceSHA256']];assert len(candidates)==1
   q=candidates[0];p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());assert len(tri)==row['completeFaces'];ps=shapely.polygons(tri[:,:,[0,2]]);projections[row['uid']]=shapely.union_all(ps[shapely.area(ps)>0]);counts[row['uid']]=len(tri)
  own=projections[UID];missing=target.difference(own);remaining=missing;components=[];features=[];credits=[]
  for u,p in projections.items():
   if u==UID:continue
   overlap=remaining.intersection(p);credits.append(dict(uid=u,newlyCoveredAreaM2=overlap.area,completeSourceFaces=counts[u]));remaining=remaining.difference(p)
  def parts(g):
   if g.geom_type=='Polygon':return [g]
   if hasattr(g,'geoms'):return [p for z in g.geoms for p in parts(z)]
   return []
  for i,p in enumerate(sorted(parts(remaining),key=lambda p:-p.area)):
   boundary_contact=p.boundary.intersection(target.boundary).length
   item=dict(component=i,areaM2=p.area,bounds=list(p.bounds),touchesTargetBoundaryLengthM=boundary_contact,interiorToTarget=boundary_contact==0,otherCurrentFootprints=[dict(uid=u,name=f.get('name'),areaM2=p.intersection(Polygon(f['rings'][0],f['rings'][1:])).area)for u,f in forms.items()if u!=UID and p.intersection(Polygon(f['rings'][0],f['rings'][1:])).area>1e-6])
   components.append(item);features.append(dict(type='Feature',properties=item,geometry=mapping(p)))
  assert abs(missing.area-sum(r['newlyCoveredAreaM2']for r in credits)-remaining.area)<1e-6
  save(DOC/'missing-components.geojson',dict(type='FeatureCollection',features=features))
  summary=dict(uid=UID,sourceSHA256=source['sourceSHA256'],originalMissingM2=missing.area,sourceAttribution=credits,remainingM2=remaining.area,components=components,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False)
  save(DOC/'coverage.json',summary)
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from matplotlib.patches import Polygon as Patch
  fig,ax=plt.subplots(figsize=(10,11),dpi=180)
  def draw(g,color,alpha):
   for p in parts(g):ax.add_patch(Patch(np.asarray(p.exterior.coords),facecolor=color,edgecolor=color,alpha=alpha))
  draw(target,'#a5b0bc',.25);draw(own,'#2c8a9b',.4)
  for u,p in projections.items():
   if u!=UID:draw(p.intersection(target),'#d8a239',.45)
  draw(remaining,'#d04458',.8)
  for r in components:
   if r['areaM2']<1:continue
   p=parts(remaining);v=next(x for x in p if abs(x.area-r['areaM2'])<1e-8).representative_point();ax.text(v.x,v.y,str(r['component']),fontsize=7)
  ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('West Wing: full original footprint coverage\nBlue: original source; gold: paired originals; red: unresolved area');ax.set_xlabel('Local east (m)');ax.set_ylabel('Local south (m)');fig.tight_layout();fig.savefig(DOC/'coverage.png');plt.close(fig)
  refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'require_remaining_xl.py',BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json'])
  out=module('west_missing_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-original-missing-footprint-source-attribution-v1',refs,dict(uids=[UID],originalMissingM2=missing.area,remainingM2=remaining.area,sourceAttribution=credits,remainingComponents=len(components),identityAccepted=False,nextStep='Review every remaining missing area against source-authored open spaces and retained architect plan; no blanket coverage exemption.'))
  print(dict(jobId=out['jobId'],originalMissingM2=missing.area,remainingM2=remaining.area,components=len(components)),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
