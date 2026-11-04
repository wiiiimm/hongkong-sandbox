"""Source-only views of exact unresolved Oi Sin interfaces; no acceptance edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-oi-sin-interface-role-views-v1-20261017'; DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-oi-sin-four-originals-physical-v1-20261017'
EDGES=BASE/'government-xl-oi-sin-original-edges-v1-20261017'
COVERAGE=BASE/'government-xl-oi-sin-assembly-coverage-v1-20261017'
RT=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
T='landsd/256280:0'; P='landsd/91128:0'
def main():
 assert not DOC.exists()
 required=[RT,PHYSICAL/'selection.json.gz',EDGES/'edges.json.gz',COVERAGE/'coverage.json']
 receipts=[read(x/'result.json') for x in [PHYSICAL,EDGES,COVERAGE]]
 pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for e in r['evidenceRefs']:
    if ROOT/e['path'] in required:
     assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p in required:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 rows=read(PHYSICAL/'selection.json.gz')['rows'];tri={}
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 refs=[Path(__file__),*required,*[x/'result.json' for x in [PHYSICAL,EDGES,COVERAGE]],HERE/'exact_packed_world_geometry_20261009.py']
 for r in rows:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];tri[r['uid']]=decode_original_world_triangles(p.read_bytes());assert len(tri[r['uid']])==r['triangles'];refs.append(p)
 edges=read(EDGES/'edges.json.gz')['rows'];ids=sorted({i for e in edges for i in e['sourceFaces']}); source=tri[T];host=tri[P]
 facets=[]
 for i in ids:
  f=source[i];n=np.cross(f[1]-f[0],f[2]-f[0]);length=float(np.linalg.norm(n));facets.append(dict(face=i,vertices=f.tolist(),areaM2=length/2,normal=(n/length).tolist() if length else [0,0,0]))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection,LineCollection
 fig,axes=plt.subplots(2,2,figsize=(16,12))
 configs=[((0,2),'East','South'),((0,1),'East','Height'),((2,1),'South','Height'),((0,2),'East','South')]
 origin=np.array([6870.,34.382,710.]); seg=np.asarray([e['segment']for e in edges])
 for index,(ax,(dims,xlab,ylab)) in enumerate(zip(axes.ravel(),configs)):
  hs=host if index!=3 else host[(host.min(1)[:,1]<=34.5)&(host.max(1)[:,1]>=34.2)]
  st=source if index==0 else source[ids]
  ax.add_collection(PolyCollection((hs-origin)[:,:,dims],facecolors='#299bb0',edgecolors='#267b8b',alpha=.18,linewidths=.25))
  ax.add_collection(PolyCollection((st-origin)[:,:,dims],facecolors='#e5b542',edgecolors='#987000',alpha=.25,linewidths=.3))
  ax.add_collection(LineCollection((seg-origin)[:,:,dims],colors='#d7191c',linewidths=1.5))
  ax.autoscale_view();ax.set_aspect('equal');ax.set_xlabel(xlab+' offset m');ax.set_ylabel(ylab+' offset m');ax.grid(alpha=.2)
  if dims[1]==1:ax.set_ylim(-5,12)
  ax.set_title('Complete projection' if index==0 else 'Contact-height podium slice' if index==3 else 'Exact failed-edge adjacent source facets')
 fig.suptitle('Oi Sin unchanged sources: podium blue, tower/source facets gold, 92 affected edges red\nSource evidence only: no support or identity approval');fig.tight_layout();DOC.mkdir();fig.savefig(DOC/'interface-context.png',dpi=140);plt.close(fig)
 save(DOC/'interface-context.json.gz',dict(sourceFaces=len(source),hostFaces=len(host),affectedEdges=len(edges),adjacentFacets=facets,sourceGeometryChanges=0,acceptance=False,qualification='All original facets adjacent to affected low edges accounted. Source-only visual evidence; historical physical input, not fresh current-world acceptance.'))
 out=module('oi_sin_role_views_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-original-interface-role-views-v1',refs,dict(uids=[T,P],affectedEdges=len(edges),adjacentFaceCount=len(ids),fullAcceptance=False,nextStep='Interpret original contact-height interface and qualify compound identity; preserve all raw physical failures and require current complete acceptance.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
