"""Exact finite source-only comparison; no terrain edits or support acceptance."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as Q
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='xl-terrain-recovery-20261010-beverly-garden-nine-authentic-ground-comparison-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-beverly-garden-nine-retained-current-physical-v3-20261010'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,HERE/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not (DOC/'result.json').exists()
 row=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='19a98fa6709619ab7ec32664025d15c084f458b4890f4b5db85d1fd36035b587'
 tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==10434
 runtimepath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtimepath)['rows'][0];positions=np.asarray(runtime['position']).reshape(-1,3);indices=np.asarray(runtime['index']).reshape(-1,3);literal=positions[indices];assert np.max(abs(literal-tri))<=1e-9
 sheet=PHYSICAL/'source-recovery.json';r=read(sheet)['sheets'][0];assert r['sheet']=='12-NW-21A';cache=ROOT/r['cache'];files=[cache/'terrain'/f['name'] for f in r['terrainFiles']]
 for f,p in zip(r['terrainFiles'],files):assert digest(p.read_bytes())==f['sha256']
 second=mod('bev_auth_ground_second','xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
 original=np.concatenate([second.terrain_triangles(p) for p in files if p.suffix=='.gltf'])
 proposalpath=ROOT/read(PHYSICAL/'terrain-candidates.json')[0]['path'];parentpath=ROOT/'3d-viewer/city/data/government-native-32066-0.json'
 def patch(p):
  d=read(p)['nativeMesh'];pp=np.asarray(d['position'],np.float32).reshape(-1,3).astype(float);ii=np.asarray(d['index']).reshape(-1,3);return pp[ii]
 groundsets={'authenticatedWholeOriginalTIN':original,'literalCurrentProposalGround':np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3),'packedProposedNativeOnly':patch(proposalpath),'packedExistingParentNativeOnly':patch(parentpath)}
 vertices=np.unique(tri.reshape(-1,3),axis=0);bottom=float(vertices[:,1].min());points=vertices[vertices[:,1]<=bottom+.35];assert len(points)>0
 rows=[];summaries={}
 for label,g in groundsets.items():
  lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));mask=(g[:,:,0].max(axis=1)>=lo[0])&(g[:,:,0].min(axis=1)<=hi[0])&(g[:,:,2].max(axis=1)>=lo[2])&(g[:,:,2].min(axis=1)<=hi[2]);ids=np.where(mask)[0];gf=g[ids];tree=shapely.STRtree(shapely.box(gf[:,:,0].min(axis=1),gf[:,:,2].min(axis=1),gf[:,:,0].max(axis=1),gf[:,:,2].max(axis=1)));rational={};actual=[]
  for pi,point in enumerate(points):
   x,z=Q(float(point[0])),Q(float(point[2]));hits=[]
   for j in tree.query(shapely.Point(float(x),float(z))):
    j=int(j)
    if j not in rational:rational[j]=[[Q(float(v)) for v in p] for p in gf[j]]
    a,b,c=rational[j];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if not den:continue
    u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den;v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;w=1-u-v
    if min(u,v,w)>=0:hits.append((u*a[1]+v*b[1]+w*c[1],int(ids[j])))
   hits.sort(reverse=True);q=dict(pointIndex=pi,point=point.tolist(),completeFiniteCoverFacetIndices=[i for y,i in hits],ground=float(hits[0][0]) if hits else None,gap=float(Q(float(point[1]))-hits[0][0]) if hits else None);actual.append(q)
  covered=[p['gap'] for p in actual if p['gap'] is not None];summaries[label]=dict(completeFacetCount=len(g),sourceBoundsIntersectingOriginalFacetCount=len(gf),facetSHA256=digest(g.tobytes()),points=len(actual),missing=sum(p['gap'] is None for p in actual),minimumGapM=min(covered) if covered else None,maximumGapM=max(covered) if covered else None,genuineExistingPointBandWitnesses=sum(abs(v)<=.1 for v in covered));rows.append(dict(surface=label,samples=actual))
 refs=[Path(__file__),PHYSICAL/'selection.json.gz',PHYSICAL/'terrain-candidates.json',PHYSICAL/'result.json',sheet,runtimepath,asset,proposalpath,parentpath,*files,HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py']+list((HERE/'local'/BATCH).rglob('*'))
 refs=[p for p in refs if p.is_file()]
 result=dict(uids=['landsd/30031:0'],completeOriginalFaces=len(tri),sourceSHA256=row['sourceSHA256'],sourceWorldSHA256=digest(tri.tobytes()),literalWorldSHA256=digest(literal.tobytes()),sheet=r['sheet'],sourceBottomM=bottom,uniqueWholeSourceLowVertices=len(points),summaries=summaries,rows=rows,interpretation='Diagnostic finite low original vertex comparison, not a complete source support proof. Original full sheet is not current rendered ground. No terrain or source changes, root or installation acceptance.',supportAccepted=False,fullAcceptance=False)
 result=json.loads(json.dumps(result,allow_nan=False));save(DOC/'diagnostic.json.gz',result);final=mod('bev_ground_checkpoint','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-low-vertices-authentic-tin-vs-proposal-v1',refs,result)
 print(json.dumps(dict(jobId=final['jobId'],summaries=summaries)),flush=True)
if __name__=='__main__':main()
