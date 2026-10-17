"""Source-only ordinary rims on explicitly altered authentic TIN.

Complete original indexed source correspondence and exact finite upper-ground
sampling; existing -.5/1/strict ±.1 limits. Contacts and nonzero EDGE body census
are independently replayed. This is NOT current drawn-ground/root acceptance:
the derived TIN is not deployed, and all current/foreign/full-facet gates remain.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,deque
import importlib.util,json,time,uuid
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from original_wall_rim_accounting_20261009 import original_samples
from original_ordinary_rim_accounting_20261009 import verify as ordinary
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1';DERIVED=BASE/'xl-terrain-recovery-20261011-hoi-shing-whole-authentic-tin-derived-step-candidate-v1';TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1';PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];results={}
 for folder in [GRAPH,DERIVED,PROBE]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  results[folder.name]=receipt;refs.append(ref(folder/'result.json'))
 graph=read(GRAPH/'diagnostic.json.gz');assert ref(GRAPH/'diagnostic.json.gz')in results[GRAPH.name]['evidenceRefs'];refs.append(ref(GRAPH/'diagnostic.json.gz'))
 derived=read(DERIVED/'diagnostic.json.gz');assert ref(DERIVED/'diagnostic.json.gz')in results[DERIVED.name]['evidenceRefs'];refs.append(ref(DERIVED/'diagnostic.json.gz'));assert derived['derivedTerrainGeometryChanged']and not derived['currentAcceptance']
 gpath=ROOT/derived['explicitDerivedTerrainArtifact']['path'];assert ref(gpath)==derived['explicitDerivedTerrainArtifact'];g=read(gpath);whole=np.asarray(g['triangles'],float);assert whole.shape==(177048,3,3)and digest(whole.tobytes())==g['derivedGroundSHA256'];refs.append(ref(gpath))
 subsetpath=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';assert ref(subsetpath)in read(TIN/'result.json')['evidenceRefs'];refs.extend([ref(subsetpath),ref(TIN/'result.json')]);subset=np.asarray(read(subsetpath)['sourceCoveringWholeFacetIds'],int);assert len(subset)==len(set(subset.tolist()))and np.all((subset>=0)&(subset<len(whole)));ground=whole[subset]
 geompath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';assert ref(geompath)in results[PROBE.name]['evidenceRefs'];refs.extend([ref(geompath),ref(PROBE/'selection.json.gz')]);runtime={r['uid']:r for r in read(geompath)['rows']};selection=read(PROBE/'selection.json.gz');worlds=[];indexed={};cursor=0;actors=[];maximum_roundoff=0
 for row in selection['rows']:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==runtime[uid]['sourceSHA256'];refs.append(ref(asset));world=decode_original_world_triangles(asset.read_bytes());rawpos=np.asarray(runtime[uid]['position'],float).reshape(-1,3);indices=np.asarray(runtime[uid]['index'],np.uint32).reshape(-1,3);assert len(world)==row['candidate']['entry']['triangles'];assert world.shape==rawpos[indices].shape;roundoff=float(np.max(np.abs(world-rawpos[indices])));assert roundoff<=1e-9;maximum_roundoff=max(maximum_roundoff,roundoff)
  positions=np.empty_like(rawpos);assigned={}
  for ids,face in zip(indices,world):
   for vertex,point in zip(ids,face):
    vertex=int(vertex)
    if vertex in assigned:assert np.array_equal(assigned[vertex],point)
    else:assigned[vertex]=point;positions[vertex]=point
  assert set(assigned)==set(range(len(positions)))and np.array_equal(positions[indices],world),'Incomplete original index correspondence';indexed[uid]=(positions,indices,cursor);actors.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],globalFaceRange=[cursor,cursor+len(world)],completeSourceFaces=len(world)));worlds.append(world);cursor+=len(world)
 tri=np.concatenate(worlds);assert len(tri)==19374 and digest(tri.tobytes())==graph['binding']['completeOriginalWorldSHA256'];components=graph['components'];members={fi:i for i,c in enumerate(components)for fi in c['globalOriginalFaces']};zero=graph['exactNonrenderingGlobalFacesRetained'];assert len(components)==145 and len(members)+len(zero)==len(tri)
 # Independently reproduce true nonzero EDGE bodies; exact zero faces stay
 # present but never gain an interface, ordinary root or bridge.
 expected=[];offset=0
 for actor,world in zip(actors,worlds):
  inv=census(world,list(range(len(world))))
  expected.extend(dict(actorUID=actor['uid'],globalOriginalFaces=[offset+i for i in ids])for ids in inv['sharedEdgeConnectedComponents']);offset+=len(world)
 assert expected==[{k:c[k]for k in ['actorUID','globalOriginalFaces']}for c in components]
 assert all(not np.any(np.cross(tri[fi,1]-tri[fi,0],tri[fi,2]-tri[fi,0]))for fi in zero)
 paths=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','original_wall_rim_accounting_20261009.py','original_ordinary_rim_accounting_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in paths)
 claim=reservations.claim('hoi-derived-original-rims-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>0;facets=ground[valid];wholeids=subset[valid];tree=shapely.STRtree(polys[valid]);rational={}
  def height(x,z):
   qx,qz=F(float(x)),F(float(z));values=[]
   for k in tree.query(shapely.Point(x,z)):
    k=int(k)
    if k not in rational:rational[k]=[[F(float(v))for v in p]for p in facets[k]]
    a,b,c=rational[k];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if not den:continue
    u=((b[2]-c[2])*(qx-c[0])+(c[0]-b[0])*(qz-c[2]))/den;v=((c[2]-a[2])*(qx-c[0])+(a[0]-c[0])*(qz-c[2]))/den;w=1-u-v
    if min(u,v,w)>=0:values.append((u*a[1]+v*b[1]+w*c[1],int(wholeids[k])))
   assert values,'Missing finite derived ground at original sample';y=max(p[0]for p in values);return float(y),str(y),[fi for h,fi in values if h==y]
  rows=[];roots=[]
  for i,c in enumerate(components):
   p,idx,start=indexed[c['actorUID']];local=np.asarray(c['globalOriginalFaces'])-start;vertexids=sorted(set(idx[local].reshape(-1).tolist()));mapping={v:j for j,v in enumerate(vertexids)};cp=p[vertexids];ci=np.asarray([[mapping[int(v)]for v in face]for face in idx[local]],np.uint32);bottom=float(cp[:,1].min());samples=original_samples(cp,ci,bottom);metric=None;proof=None;missing=[]
   for j,s in enumerate(samples):
    try:y,exact,faces=height(s['point'][0],s['point'][2]);s.update(ground=y,gap=s['point'][1]-y,exactFiniteDerivedGroundY=exact,completeUpperEnvelopeCoveringWholeSheetFaces=faces)
    except AssertionError as error:missing.append(dict(sample=j,reason=str(error)))
    pulse()
   if not missing:
    low=[s for s in samples if s['point'][1]<=bottom+.35];metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(s['gap']for s in samples),minLowGap=min(s['gap']for s in low),maxLowGap=max(s['gap']for s in low))
    try:proof=ordinary(cp,ci,bottom,samples,expected_metric=metric);roots.append(i)
    except AssertionError as error:proof=dict(verified=False,reason=str(error))
   rows.append(dict(component=i,actorUID=c['actorUID'],completeOriginalFaces=c['globalOriginalFaces'],completeOriginalIndexedVertexIds=vertexids,completeSampleInventory=samples,missingFiniteDerivedGroundSamples=missing,metric=metric,sourceOnlyOrdinaryRim=proof));pulse()
   if (i+1)%8==0:save(LOCAL/'ordinary-rim-progress.json.gz',dict(rows=rows,complete=False,sourceOnly=True,currentAcceptance=False));print(json.dumps(dict(component=i+1,total=len(components),sourceOnlyOrdinaryRoots=len(roots))),flush=True)
  adj=defaultdict(set);contacts=[]
  for r in graph['oneExactPositiveWitnessPerContactingBodyPair']:
   a,b=r['globalOriginalFaces'];ca,cb=r['components'];assert members[a]==ca and members[b]==cb;points=intersection_points(rational_face(tri[a]),rational_face(tri[b]));assert len(points)>=2;measure=contact_measure(points);assert measure==r['exactContact']and measure['dimension']>0;contacts.append(r);adj[ca].add(cb);adj[cb].add(ca);pulse()
  reached=set(roots);queue=deque(roots);parents={i:None for i in roots}
  while queue:
   a=queue.popleft()
   for b in sorted(adj[a]-reached):reached.add(b);parents[b]=a;queue.append(b)
  unresolved=sorted(set(range(len(components)))-reached);pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[a['uid']for a in actors],complete19374OriginalFaces=True,complete145NonzeroEdgeBodies=True,exactNonrenderingFacesAccountedWithNoRootBridgeCredit=zero,completeOriginalWorldSHA256=digest(tri.tobytes()),completeSelectedDerivedGroundSHA256=digest(ground.tobytes()),explicitAlteredTerrain=True,originalSourceRuntimeIndexMaximumRoundoffM=maximum_roundoff,allOriginalOrdinaryRimSamples=rows,sourceOnlyOrdinaryRimPositiveBodies=roots,all149ExactPositiveContactWitnessesRecomputed=contacts,sourceOnlyDerivedGroundReachedBodies=sorted(reached),sourceOnlyDerivedGroundParents=parents,unresolvedSourceBodies=unresolved,unresolvedSourceBodyFaces=sum(len(components[i]['globalOriginalFaces'])for i in unresolved),allOriginalTINAndCurrentNegativesPreserved=True,sourceOnly=True,groundScope='undeployed-explicitly-altered-authentic-TIN',currentDrawnGroundCredit=False,rootOrBridgeCreditForCurrentViewer=False,currentAcceptance=False,fullFacetFoundationForeignIdentityRuntimeStillMandatory=True,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/paths[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'hoi-shing-undeployed-derived-authentic-ground-complete-original-rim-graph-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,derivedTerrainGeometryChanged=True,ordinaryRimPositiveBodies=roots,unresolvedBodies=unresolved,newlyInstalled=0));print(json.dumps(dict(sourceOnlyOrdinaryRoots=roots,unresolved=unresolved)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
