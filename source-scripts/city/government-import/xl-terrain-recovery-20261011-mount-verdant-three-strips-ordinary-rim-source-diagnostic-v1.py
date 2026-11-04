"""Source-only ordinary rims of three original long strips against TIN/P roof.

Every original component sample and complete finite upper surface accounted.
Uninstalled original P top is a separate geometric diagnostic, never current
support availability. No visual detail may become a structural root or bridge.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples
from original_ordinary_rim_accounting_20261009 import verify as ordinary
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-three-strips-ordinary-rim-source-diagnostic-v1';DOC=BASE/BATCH
CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1';LONG=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-long-original-backing-facets-v1';TIN=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-finite-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [CAPTURE,LONG,TIN]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  receipts[folder.name]=receipt;refs.append(ref(folder/'result.json'))
 srcpath=CAPTURE/'literal-source-inputs.json.gz';actualpath=CAPTURE/'actual-render-attributes.json.gz';assert ref(srcpath)in receipts[CAPTURE.name]['evidenceRefs']and ref(actualpath)in receipts[CAPTURE.name]['evidenceRefs'];src=read(srcpath);actual=read(actualpath);worlds=[];index=None
 for row,record in zip(src['rows'],actual['rows']):
  assert row['uid']==record['uid'];asset=ROOT/row['path'];assert digest(asset.read_bytes())==row['entry']['sha256']==record['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());worlds.append(world);refs.append(ref(asset))
  if row['uid']=='landsd/261717:0':index=np.asarray(record['completeOriginalIndex'],np.uint32).reshape(-1,3);assert len(index)==len(world)==14938
 assert index is not None and len(worlds)==2 and len(worlds[1])==641;world=worlds[0];assigned={}
 for ids,face in zip(index,world):
  for vertex,point in zip(ids,face):
   if int(vertex)in assigned:assert np.array_equal(assigned[int(vertex)],point)
   else:assigned[int(vertex)]=point
 gpath=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';assert ref(gpath)in receipts[TIN.name]['evidenceRefs'];g=read(gpath);ground=np.asarray(g['completeSelectedFacets'],float);assert digest(ground.tobytes())==g['completeSelectedFacetSHA256'];lpath=LONG/'diagnostic.json.gz';assert ref(lpath)in receipts[LONG.name]['evidenceRefs'];long=read(lpath);refs.extend(ref(p)for p in [srcpath,actualpath,gpath,lpath]);rows=[]
 for mode,surface in [('authentic-original-TIN-only',ground),('authentic-TIN-plus-complete-uninstalled-original-podium',np.concatenate([ground,worlds[1]]))]:
  polygons=shapely.polygons(surface[:,:,[0,2]]);valid=shapely.area(polygons)>0;facets=surface[valid];tree=shapely.STRtree(polygons[valid]);rational={}
  def height(x,z):
   qx,qz=F(float(x)),F(float(z));values=[]
   for k in tree.query(shapely.Point(x,z)):
    k=int(k)
    if k not in rational:rational[k]=[[F(float(v))for v in p]for p in facets[k]]
    a,b,c=rational[k];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if not den:continue
    u=((b[2]-c[2])*(qx-c[0])+(c[0]-b[0])*(qz-c[2]))/den;v=((c[2]-a[2])*(qx-c[0])+(a[0]-c[0])*(qz-c[2]))/den;w=1-u-v
    if min(u,v,w)>=0:values.append(u*a[1]+v*b[1]+w*c[1])
   assert values,'Missing complete finite source surface';return float(max(values))
  for body in long['all30OriginalLongStripFaces']:
   fi=body['all10CompleteOriginalFaces'];vertexids=sorted(set(index[fi].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(vertexids)};cp=np.asarray([assigned[v]for v in vertexids]);ci=np.asarray([[mapping[int(v)]for v in face]for face in index[fi]],np.uint32);assert np.array_equal(cp[ci],world[fi]);bottom=float(cp[:,1].min());samples=original_samples(cp,ci,bottom);missing=[]
   for i,sample in enumerate(samples):
    try:y=height(sample['point'][0],sample['point'][2]);sample.update(ground=y,gap=sample['point'][1]-y)
    except AssertionError as e:missing.append(dict(sample=i,reason=str(e)))
   metric=None;proof=None
   if not missing:
    low=[s for s in samples if s['point'][1]<=bottom+.35];metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(s['gap']for s in samples),minLowGap=min(s['gap']for s in low),maxLowGap=max(s['gap']for s in low))
    try:proof=ordinary(cp,ci,bottom,samples,expected_metric=metric)
    except AssertionError as error:proof=dict(verified=False,reason=str(error))
   rows.append(dict(mode=mode,originalBody=body['originalBody'],all10OriginalFaces=fi,completeOriginalIndexedVertexIds=vertexids,completeSourceSurfaceSHA256=digest(surface.tobytes()),allOriginalSamples=samples,missingSourceSurface=missing,metric=metric,sourceOnlyOrdinaryRim=proof,currentRootCredit=False));print(dict(mode=mode,body=body['originalBody'],metric=metric,ordinary=proof),flush=True)
 refs.extend(ref(HERE/n)for n in ['exact_packed_world_geometry_20261009.py','original_wall_rim_accounting_20261009.py','original_ordinary_rim_accounting_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']);assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uid='landsd/261717:0',complete14938OriginalWorldSHA256=digest(world.tobytes()),rows=rows,allOriginalOpenLoopAndOrdinaryFailuresPreserved=True,uninstalledPodiumNeverDeclaredAvailableSupport=True,sourceOnly=True,visualRoleAccepted=False,rootOrBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount-three-long-source-strips-ordinary-rim-original-TIN-uninstalled-P-surface-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[out['uid']],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
