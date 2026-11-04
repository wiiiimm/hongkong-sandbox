"""Full compound foundation replay and exact two-face association in four source/runtime worlds."""
from fractions import Fraction as F
from pathlib import Path
import time,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as orthogonal
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as edge
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-aqua272788-four-world-junction-v1-20261017';DOC=BASE/BATCH
CAP=BASE/'government-xl-aqua272788-four-world-capture-v1-20261017';PHYS=BASE/'government-xl-aqua272788-current-physical-v3-20261017';ROLE=BASE/'government-xl-aqua272788-original-junction-review-v1-20261017';T='landsd/272788:0';P='landsd/193086:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,PHYS,ROLE]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:pins.setdefault(e['path'],set()).add(e['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(CAP/'world-triangles.json.gz');role=consume(ROLE/'ROOT-SOURCE-REVIEW.json');assert role['sourceRoleInterpretationAccepted']
 source=consume(PHYS/'selection.json.gz')['rows'][0];rings=source['source']['building']['rings'];polygon=Polygon(rings[0],rings[1:]);rt=consume(HERE/'local'/PHYS.name/'runtime-geometry.json.gz');ground=np.asarray(rt['rows'][0]['drawnGroundGeometry'],float).reshape(-1,3,3)
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 helper=module('aqua_four_foundation',HERE/'xl-final-script-pass.py');claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];renewed=time.monotonic();cache={};rows=[]
 try:
  DOC.mkdir()
  for mode,w in worlds.items():
   tower=np.array(w[T]);host=np.array(w[P]);key=(digest(tower.tobytes()),digest(host.tobytes()));assert len(tower)==11045 and len(host)==22735
   if key in cache:rows.append(dict(mode=mode,reusedExactWorldMode=cache[key]['mode'],sourceWorldSHA256=key[0],hostWorldSHA256=key[1],verified=cache[key]['verified']));continue
   foundation=helper.foundation_context(tower,np.concatenate([ground,host]),polygon);proofs=[]
   for face in [32,1836]:
    nodes=[]
    def visit(t,depth):
     nonlocal renewed
     if time.monotonic()-renewed>20:assert reservations.heartbeat(lease,ttl=3600)['ok'];renewed=time.monotonic()
     i=len(nodes);n=dict(id=i,depth=depth,exactVertices=[[str(v)for v in p]for p in t]);nodes.append(n);a=np.array([[float(v)for v in p]for p in t]);exact=all(F(float(a[k,j]))==t[k][j]for k in range(3)for j in range(3));n['exactlyRepresentable']=exact
     if not exact:n['complete']=False;return i,False
     o=orthogonal(a,host);e=None if o['wholeFacetAssociated']else edge(a,host);passed=o['wholeFacetAssociated']or bool(e and e['wholeFacetFiniteEdgeUnionAssociated']);n.update(orthogonalProof=o,edgeProof=e,complete=passed)
     if passed or depth==8:return i,passed
     x,y,z=t;xy=[(x[j]+y[j])/2 for j in range(3)];yz=[(y[j]+z[j])/2 for j in range(3)];zx=[(z[j]+x[j])/2 for j in range(3)];children=[visit(c,depth+1)for c in [[x,xy,zx],[xy,y,yz],[zx,yz,z],[xy,yz,zx]]];n['children']=[j for j,_ in children];n['complete']=all(ok for _,ok in children);return i,n['complete']
    _,passed=visit([[F(float(v))for v in p]for p in tower[face]],0);path=DOC/(mode+'-face-'+str(face)+'.json.gz');save(path,dict(sourceFace=face,complete=passed,nodes=nodes,sourceWorldSHA256=key[0],hostWorldSHA256=key[1]));proofs.append(dict(face=face,complete=passed,nodes=len(nodes)));print(mode,face,passed,len(nodes),flush=True)
   verified=all(p['complete']for p in proofs)and foundation['completeTerrainTriangles']==11045 and foundation['fullyBuriedTriangles']==2 and foundation['fullyBuriedUpwardTriangles']==0
   row=dict(mode=mode,sourceWorldSHA256=key[0],hostWorldSHA256=key[1],foundation=foundation,faceProofs=proofs,verified=verified);rows.append(row);cache[key]=row
  save(DOC/'summary.json',dict(rows=rows,allFourModesVerified=len(rows)==4 and all(r['verified']for r in rows),groundSHA256=digest(ground.tobytes()),fullAcceptance=False,sourceGeometryChanges=0,qualification='Complete canonical compound foundation evaluated in each unique actual world. Exact complete two-facet 0.1m proximity separately proved in each source/host world. Raw foundation flags remain for scoped role resolution.'))
  refs += [HERE/'xl-final-script-pass.py',Path(helper.s.context.shared.__file__),HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py',HERE/'exact_original_surface_coordinate_band_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py']
  out=module('aqua_four_junction_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-complete-four-world-original-junction-v1',refs,dict(uids=[T],allFourModesVerified=len(rows)==4 and all(r['verified']for r in rows),fullAcceptance=False,nextStep='Resolve only the explicitly reviewed original two-side-skin warnings if all coordinate modes pass; retain all other current source/neighbour/browser gates.'));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
