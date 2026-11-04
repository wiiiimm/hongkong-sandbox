"""Whole original projection/extension accounting, diagnostic only."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-park-avenue-restored-v1-20261018'
IDENTITY=BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018'
BATCH='government-xl-olympian-two-park-projection-context-v1-20261018';DOC=BASE/BATCH

def draw(ax,g,color,alpha=1,fill=False):
 if g.is_empty:return
 if g.geom_type=='Polygon':
  x,y=g.exterior.xy
  if fill:ax.fill(x,y,color=color,alpha=alpha)
  else:ax.plot(x,y,color=color,alpha=alpha,linewidth=.7)
  for ring in g.interiors:ax.plot(*ring.xy,color=color,alpha=alpha,linewidth=.5)
 elif hasattr(g,'geoms'):
  for part in g.geoms:draw(ax,part,color,alpha,fill)

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018/selection.json.gz';rows=read(selection)['rows'];projections={};meshes={};polys={}
 for row in rows:
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];uid=row['uid'];meshes[uid]=tri;polys[uid]=shapely.polygons(tri[:,:,[0,2]]);projections[uid]=shapely.union_all(polys[uid])
 for extra in read(PRIOR/'restored.json')['rows']:
  raw=(ROOT/extra['assetPath']).read_bytes();assert digest(raw)==extra['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==extra['triangles'];uid=extra['uid'];assert uid not in meshes;meshes[uid]=tri;polys[uid]=shapely.polygons(tri[:,:,[0,2]]);projections[uid]=shapely.union_all(polys[uid])
 refs.extend([IDENTITY/'result.json',selection]);identity_receipt=read(IDENTITY/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(identity_receipt['jobId'],)).fetchone()==('complete',identity_receipt)
 for e in identity_receipt['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];assert digest((ROOT/e['path']).read_bytes())==e['sha256'];pins[e['path']]=e['sha256']
 assert len(meshes)==14
 rows+=read(IDENTITY/'selection.json.gz')['rows']
 results=[];fig,axes=plt.subplots(2,4,figsize=(24,16),constrained_layout=True);axes=axes.ravel();axes[-1].axis('off')
 for ax,uid in zip(axes,['landsd/82096:0','landsd/79627:0','landsd/83600:0','landsd/79657:0','landsd/80122:0','landsd/83837:0','landsd/72277:0']):
  row=next(x for x in rows if x['uid']==uid);proof=read(IDENTITY/(uid.split('/')[1]+'-identity.json'))['proof'];form=row['source']['building'];target=Polygon(form['rings'][0],form['rings'][1:]);projection=projections[uid];excess=projection.difference(target);other=shapely.union_all([p for k,p in projections.items() if k!=uid]);uncovered=excess.difference(other)
  face_ids=np.flatnonzero(shapely.area(shapely.intersection(polys[uid],excess))>0).tolist();faces=[]
  for i in face_ids:
   outside=polys[uid][i].difference(target)
   faces.append(dict(face=i,outsideAreaM2=outside.area,minY=float(meshes[uid][i,:,1].min()),maxY=float(meshes[uid][i,:,1].max()),outsideProjection=mapping(outside)))
  overlaps=[]
  for item in proof['freshCurrentIdentity']['intersectingForms']:
   tile=ROOT/'3d-viewer'/item['tile'];forms=read(tile)['buildings'];foreign=next(b for b in forms if b['uid']==item['uid']);fp=Polygon(foreign['rings'][0],foreign['rings'][1:]);inter=excess.intersection(fp)
   overlaps.append(dict(**item,excessIntersectionAreaM2=inter.area,excessIntersection=mapping(inter)))
   draw(ax,fp,'#888888',.65);pt=fp.representative_point();ax.text(pt.x,pt.y,item['uid'].split('/')[1],fontsize=6,clip_on=True)
  save(DOC/(uid.split('/')[1]+'-geometry.json.gz'),dict(uid=uid,sourceSHA256=row['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],sourceFaces=len(meshes[uid]),projection=mapping(projection),target=mapping(target),excess=mapping(excess),excessNotCoveredByOtherThirteenOriginals=mapping(uncovered),extensionFaces=faces,overlaps=overlaps))
  summary=dict(uid=uid,sourceFaces=len(meshes[uid]),extensionFaces=len(faces),sourceAreaM2=projection.area,excessAreaM2=excess.area,excessCoveredByOtherOriginalsM2=excess.intersection(other).area,excessUncoveredByOtherOriginalsM2=uncovered.area,rawIdentityReasons=proof['reasons']);results.append(summary);print(summary,flush=True)
  draw(ax,projection,'#1e70aa',.25,True);draw(ax,target,'#111111');draw(ax,excess,'#e07428',.65,True);draw(ax,uncovered,'#d32626',.85,True)
  x0,y0,x1,y1=projection.bounds;ax.set_xlim(x0-10,x1+10);ax.set_ylim(y0-10,y1+10);ax.set_aspect('equal');ax.set_title(uid+'\nblue original / black form\norange extension / red outside other thirteen originals');ax.set_xlabel('World X (m)');ax.set_ylabel('World Z (m)')
 DOC.mkdir(parents=True,exist_ok=True);fig.savefig(DOC/'complete-projections.png',dpi=160);plt.close(fig)
 save(DOC/'summary.json',dict(rows=results,identityApproved=False,fullAcceptance=False,newlyInstalled=0,qualification='Complete original projected geometry, not sampled vertices. Other-source projection coverage is context only, not identity, vertical clearance or physical approval. All extension polygons and original face indices retained; no source changes.'))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([selection,HERE/'exact_packed_world_geometry_20261009.py'])
 out=module('olympian_projection_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-fourteen-original-extension-projection-context-v1',list(set(refs)),dict(uids=[x['uid']for x in rows],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
