"""UNEXECUTED readonly saved-facet cause diagnostic; no source decode/DB/leases."""
import argparse, collections, gzip, hashlib, json
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
import southside_saved_surface_overlap_provenance_v1_20261012 as exact
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012'
DOC=BASE/BATCH
DRAFT=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
MODES={'actualLiteral':'completeLiteralWorldPosition','explicitLeftAssociatedF32ModelMatrix':'completeExplicitLeftAssociatedFloat32WorldPosition','explicitBalancedF32ModelMatrix':'completeExplicitBalancedFloat32WorldPosition'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.load(gzip.open(p,'rt')if p.suffix=='.gz'else p.open())
def pin(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p))
def preflight():
 resultpath=DOC/'result.json';assert digest(resultpath)=='7931ea4e62ccc0cc317db1fbbf37c2707a837913548e66ebec879063ba7591e5'
 result=read(resultpath);assert result['jobId']=='1be4acb6a5e52787ecc57dd7806df25dc4d5281fa6e94b6858a5ea2c14b2cfae'
 refs=result['evidenceRefs']
 for ref in refs:assert digest(ROOT/ref['path'])==ref['sha256'],ref['path']
 assert digest(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 accountpath=DOC/'source-terrain-inventory-and-proposal-account.json.gz';assert digest(accountpath)=='d16e0ea485b093b2b053db0fa17f86f99b59eead1b822bbe03d07cc742e5cf4c'
 whole=read(accountpath);account=whole['account'];candidate=ROOT/account['privateCandidatePath'];assert digest(candidate)=='55f7e1f9a90bf7e9be759d2934cc8b0aa59f886a1dd96a8d8fa59a0905b7fea8'
 patch=read(candidate);pos=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);idx=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3)
 assert np.isfinite(pos).all()and np.array_equal(idx.reshape(-1),np.arange(len(pos)))
 faces=pos[idx];lineage=account['completeOutputFacetLineage'];assert len(faces)==len(lineage)==78016
 assert [q['outputFacet']for q in lineage]==list(range(len(faces)))
 for f,q in zip(faces,lineage):
  expected=np.asarray([[float(exact.F(v))for v in p]for p in q['exactProposedFragment']],dtype=np.float32).astype(np.float64)
  assert np.array_equal(f,expected)
 captures=[]
 for uid,sha,count in [('315025','85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c',11699),('300867','2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1',1191)]:
  p=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'/f'complete-current-actual-source-and-ground-{uid}-0.json.gz';q=read(p)
  assert q['sourceSHA256']==sha and q['completeFaces']==count and q['startAndEndInputsVerified']is True
  assert len(q['completeOriginalIndex'])==3*count
  assert any(ref['path']==str(p.relative_to(ROOT))and ref['sha256']==digest(p)for ref in refs)
  captures.append(q)
 return result,whole,faces,lineage,captures,[*refs,pin(resultpath),pin(Path(__file__)),pin(Path(exact.__file__)),pin(DRAFT/'NEXT-SAVED-LAYER-LOCALITY-METHOD.md')]
def run(state,validation):
 result,whole,faces,lineage,captures,refs=state
 v=read(validation);test=Path(__file__).parent/'test_southside_saved_surface_overlap_provenance_v1_20261012.py'
 required=[Path(__file__),Path(exact.__file__),test,DRAFT/'NEXT-SAVED-LAYER-LOCALITY-METHOD.md']
 assert v['tests']==8 and v['passed']is True and v['exitCode']==0
 assert v['codePins']==[pin(p)for p in required]
 log=ROOT/v['testLogPath'];assert digest(log)==v['testLogSHA256'];refs.extend([pin(validation),pin(log),pin(test)])
 polygons=[Polygon(f[:,[0,2]])for f in faces];areas=np.asarray([p.area for p in polygons]);tree=shapely.STRtree(polygons)
 zero=[int(i)for i in np.flatnonzero(areas==0)];records=[];kindcounts=collections.Counter();sourcekindcounts=collections.Counter();sheetcounts=collections.Counter();inventory=whole['fullOriginalInventoryVerbatim']
 def sheet(global_id):
  return next(s['sheet']for s in inventory if s['globalOriginalFacetStart']<=global_id<s['globalOriginalFacetEndExclusive'])
 for i,polygon in enumerate(polygons):
  if areas[i]==0:continue
  for j in sorted(int(x)for x in tree.query(polygon)if int(x)>i):
   if areas[j]==0:continue
   packed=exact.classify(faces[i].tolist(),faces[j].tolist())
   if not packed['positiveProjectedArea']:continue
   source=exact.classify(lineage[i]['exactOriginalSourceFragment'],lineage[j]['exactOriginalSourceFragment'])
   pair=[dict(outputFacet=k,globalOriginalFacetId=lineage[k]['globalOriginalFacetId'],sheet=sheet(lineage[k]['globalOriginalFacetId']),classification=lineage[k]['classification'],parentFacet=lineage[k]['parentFacet'],alphaBranch=lineage[k]['alphaBranch'])for k in [i,j]]
   records.append(dict(pair=pair,packedFiniteOverlap=packed,originalFiniteFragmentOverlap=source,packingOnlyPositiveProjection=not source['positiveProjectedArea']))
   kindcounts[packed['classification']]+=1;sourcekindcounts[source['classification']]+=1;sheetcounts['same-sheet'if pair[0]['sheet']==pair[1]['sheet']else'different-sheets']+=1
 locality={}
 for mode,key in MODES.items():
  building=[]
  for q in captures:
   vertices=np.asarray(q[key],dtype=np.float64).reshape(-1,3);index=np.asarray(q['completeOriginalIndex']).reshape(-1,3);assert np.isfinite(vertices).all()
   for f in vertices[index]:
    p=Polygon(f[:,[0,2]])
    # Degenerate source projections remain closed contact obligations.
    building.append(p if p.area else shapely.MultiPoint(f[:,[0,2]]).convex_hull)
  union=unary_union(building);nominated=[]
  for i,p in enumerate(polygons):
   closed=p if p.area else shapely.MultiPoint(faces[i][:,[0,2]]).convex_hull
   if closed.intersects(union):nominated.append(i)
  nominated_set=set(nominated)
  locality[mode]=dict(inclusiveIndexedProjectionNominatedOutputIds=nominated,strictlyDisjointOutputIds=[i for i in range(len(faces))if i not in nominated_set],scope='Floating GEOS projection measurement only; no omission/clearance credit, providerOriginal projection not computed')
 union=unary_union([p for p in polygons if p.area>1e-10]);extentArea=(1022.5-602.5)*(4722.5-4232.5)
 measured=sum(p.area for p in polygons if p.area>1e-10)-union.area
 for ref in refs:assert digest(ROOT/ref['path'])==ref['sha256'],ref['path']
 assert digest(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 out=dict(schema='southside-saved-layer-locality-cause-diagnostic-v1',evidenceRefs=refs,completeOutputFacets=78016,allZeroProjectedOutputIds=zero,positiveProjectedPairRecords=records,packedPairClassificationCounts=dict(kindcounts),originalPairClassificationCounts=dict(sourcekindcounts),pairSheetCounts=dict(sheetcounts),floatingValidatorProjectedExcessM2=measured,floatingValidatorThresholdM2=max(.001,extentArea*1e-7),pairAreaSumsAreNotUnionExcess=True,productionProjectionLocality=locality,providerOriginalAndUnusedBoundsProtection=[q['completeOriginalPOSITIONProof']['originalWholeSourceBounds']for q in captures],all774477OriginalInventoryVerbatim=whole['fullOriginalInventoryVerbatim'],all46FormsVerbatim=whole['all46FormsVerbatim'],stationForeignObligationVerbatim=whole['stationForeignOverlapAnd34FacetsVerbatim'],noNewSourceDecode=True,noDB=True,noLease=True,noNewTerrain=True,physicalAccepted=False,currentAcceptance=False)
 target=DRAFT/'saved-layer-locality-cause-diagnostic-v1.json.gz'
 with target.open('xb')as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0)as gz:gz.write((json.dumps(out,sort_keys=True,separators=(',',':'))+'\n').encode())
 print(json.dumps(dict(artifact=pin(target),positiveOverlapPairs=len(records),packedClassificationCounts=dict(kindcounts),originalClassificationCounts=dict(sourcekindcounts),floatingProjectedExcessM2=measured,localityCounts={k:len(v['inclusiveIndexedProjectionNominatedOutputIds'])for k,v in locality.items()},noApproval=True)),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--preflight-only',action='store_true');p.add_argument('--test-validation');a=p.parse_args();state=preflight()
 if a.preflight_only:print(json.dumps(dict(savedFacets=78016,allInputsVerified=True,noSourceDecode=True,noDB=True,noLease=True)));return
 assert a.test_validation;run(state,Path(a.test_validation).resolve())
if __name__=='__main__':main()
