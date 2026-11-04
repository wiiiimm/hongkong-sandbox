"""New complete original-face context for Murray's retained one-contact failure."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-murray-original-support-20261006';BATCH='government-xl-murray-original-boundary-face-v1-20261017';DOC=BASE/BATCH;U='landsd/265825:0';P='landsd/248655:0'
def main():
 assert not DOC.exists();prior=read(OLD/'result.json');pins={e['path']:e['sha256']for e in prior['evidenceRefs']};refs=[Path(__file__),OLD/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for p in [OLD/'support-inputs.json',OLD/'support-checks.json.gz']:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 sources=read(OLD/'support-inputs.json')['sources'];geo={}
 for r in sources:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];geo[r['uid']]=decode_original_world_triangles(p.read_bytes());assert len(geo[r['uid']])==r['triangles'];refs.append(p)
 sha=next(r['sourceSHA256']for r in sources if r['uid']==U);count=BASE/'government-xl-oi-sin-original-installed-v1-20261017/full-xl-current-count.json';require_remaining(count,U,sha);refs.append(count)
 raw=read(OLD/'support-checks.json.gz')['rows'][0];assert len(raw['unresolved'])==1;failure=raw['unresolved'][0];assert len(failure['originalSourceFaces'])==1;fi=failure['originalSourceFaces'][0]['faceIndex'];assert fi==2074
 t=geo[U];host=geo[P];face=t[fi];oldface=np.asarray(failure['originalSourceFaces'][0]['vertices']);assert np.max(np.abs(face-oldface))<1e-9
 edges=[]
 for a,b in zip(face,np.roll(face,-1,axis=0)):
  if a[1]!=face[:,1].min()or b[1]!=face[:,1].min():continue
  proof=verify(np.asarray([a,b]),host);adj=[i for i,tri in enumerate(t)if any(np.array_equal(a,x)for x in tri)and any(np.array_equal(b,x)for x in tri)];edges.append(dict(segment=[a.tolist(),b.tolist()],allIncidentSourceFaces=adj,proof=proof))
 assert len(edges)==1;positions=[np.asarray(failure['position']),*face,face.mean(axis=0)];dist=[]
 for p in positions:
  i,q,d=nearest(p,host);n=np.cross(host[i,1]-host[i,0],host[i,2]-host[i,0]);dist.append(dict(point=p.tolist(),nearestHostFace=i,nearestHostPoint=q.tolist(),distanceM=d,hostNormal=(n/np.linalg.norm(n)).tolist()))
 save(DOC/'boundary.json.gz',dict(uid=U,sourceSHA256=sha,sourceFace=fi,originalVertices=face.tolist(),oldLiteralVertices=oldface.tolist(),maximumOriginalLiteralDifferenceM=float(np.max(np.abs(face-oldface))),rawInterface=raw['interface'],edges=edges,nearestDiagnostics=dist,fullAcceptance=False,geometryChanges=0))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,6),dpi=160);origin=face.mean(axis=0);lo=face.min(axis=0)-3;hi=face.max(axis=0)+3
 for j,az in enumerate([-45,135],1):
  ax=fig.add_subplot(1,2,j,projection='3d')
  for tri,color,alpha in [(host,'#777777',.25),(t,'#1786ae',.22),(face[None,:,:],'#d72b36',1)]:
   mask=np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1);local=(tri[mask]-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(local,facecolors=color,edgecolors=color,linewidths=.3,alpha=alpha))
  low=(lo-origin)[[0,2,1]];high=(hi-origin)[[0,2,1]];ax.set(xlim=(low[0],high[0]),ylim=(low[1],high[1]),zlim=(low[2],high[2]),xlabel='East(m)',ylabel='South(m)',zlabel='Height(m)',title='Original face2074 red; tower blue; podium grey');ax.view_init(elev=25,azim=az);ax.set_box_aspect(high-low)
 fig.tight_layout();fig.savefig(DOC/'original-junction.png');plt.close(fig)
 summary=dict(uid=U,failedContactNearestM=dist[0]['distanceM'],completeLowEdgePass=edges[0]['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'],sourceFacesAtLowEdge=edges[0]['allIncidentSourceFaces'],rawStrictInterfacePassed=False,fullAcceptance=False)
 save(DOC/'summary.json',summary);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','fu_tor_loy_nearest_interfaces_v1_20261017.py','require_remaining_xl.py'])
 r=module('murray_boundary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-complete-original-failed-boundary-context-v1',refs,dict(uids=[U,P],summary=summary,nextStep='Inspect complete original junction and distinguish authored boundary from missing support; preserve raw failure and require fresh current identity/foundation/neighbours/renderer/browser before publication.'));print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
