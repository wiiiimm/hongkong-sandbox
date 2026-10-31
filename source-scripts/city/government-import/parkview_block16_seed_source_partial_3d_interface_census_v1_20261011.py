"""DRAFT exact partial3D seed-frontier/current-edge source context census.
Reuses immutable full source census; no global frontier rerun/new terrain.
Zero3D tolerance; positive intervals required. Opposing local-face side is not
proof of an outside whole selected region or a qualified terrain interface.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_shared_3d_segment_intervals_v1_20261011 import overlap,covered,point
B=ROOT/'docs/astra-city/government-import';AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';FRONTIER=B/'government-xl-parkview-block16-canonical-original-TIN-frontier-inventory-v1-20261011';DOC=B/'government-xl-parkview-block16-seed-source-partial3D-interface-census-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def side(a,b,c):return (b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])
def main():
 assert not DOC.exists();refs=[ref(p)for p in [Path(__file__),INSTALLED,FRONTIER/'diagnostic.json.gz',FRONTIER/'complete-original-TIN-nonzero-edge-inventory.json.gz',FRONTIER/'result.json',AUTH/'diagnostic.json.gz',AUTH/'result.json',HERE/'pending-context.py',HERE/'native_patch_resolution.py',HERE/'exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'test_exact_shared_3d_segment_intervals_v1_20261011.py']];old=read(FRONTIER/'diagnostic.json.gz');seed=set(old['seedPositiveAreaOriginalTINFacetIDs']);assert len(seed)==145;ledger=read(FRONTIER/'complete-original-TIN-nonzero-edge-inventory.json.gz');assert len(ledger)==old['completeOriginalTINTopology']['completeNonzeroEdges']==592556
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256']==old['completeOriginalTINWorldSHA256'];packed=terrain.astype(np.float32).astype('<f8');assert digest(packed.tobytes())==old['completePackedOriginalTINWorldSHA256'];current=_faces(read(INSTALLED));assert len(current)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 ce=np.stack([current[:,[0,1]],current[:,[1,2]],current[:,[2,0]]],axis=1).reshape(-1,2,3);clo,chi=ce.min(1),ce.max(1);sourceByCurrent={}
 for r in old['exactWholeOriginalPackedCurrentFacetMatches']:
  for nid in r['exactWholePackedCurrentNativeFacetMatches']:sourceByCurrent.setdefault(nid,[]).append(r['originalTINFacet'])
 rows=[];candidateTotal=0
 for record in ledger:
  inc=record['originalFaceIncidences'];inside=sorted(i for i,_ in inc if i in seed);outside=sorted(i for i,_ in inc if i not in seed)
  if not inside or(not outside and len(inc)>1):continue
  originaledge=np.asarray(record['edge']);edge=originaledge.astype(np.float32).astype('<f8');a,b=map(point,edge);assert a!=b,'Collapsed packed boundary has no intervalcredit';ids=np.flatnonzero(np.all(chi>=edge.min(0),axis=1)&np.all(clo<=edge.max(0),axis=1)).tolist();candidateTotal+=len(ids);assert candidateTotal<=16384,'Bounded complete sourceedge/currentedge3DAABB census; no truncation';hits=[]
  for eid in ids:
   iv=overlap(edge[0],edge[1],ce[eid,0],ce[eid,1])
   if iv is None:continue
   nid,le=divmod(eid,3);third=point(current[nid,(le+2)%3]);insideSides=[]
   for fid in inside:
    vertices=[point(p)for p in packed[fid]];thirds=[p for p in vertices if p not in [a,b]];assert len(thirds)==1;insideSides.append(side(a,b,thirds[0]))
   opposite=all(s!=0 and s*side(a,b,third)<0 for s in insideSides)
   hits.append(dict(currentNativeFacet=nid,currentLocalEdge=le,exactSourceInterval=[str(v)for v in iv],opposingEveryLocalInsideFaceXZSide=opposite,wholePackedCurrentFacetSourceMatches=sourceByCurrent.get(nid,[]),wholeMatchedOriginalSourceOutsideSeed=[i for i in sourceByCurrent.get(nid,[])if i not in seed],currentDerivedPieceOriginalPlaneProvenanceSeparatelyRequired=True))
  allparts=[tuple(map(F,h['exactSourceInterval']))for h in hits];opp=[tuple(map(F,h['exactSourceInterval']))for h in hits if h['opposingEveryLocalInsideFaceXZSide']]
  rows.append(dict(exactOriginalSourceEdge=record['edge'],actualFloat32SourceEdge=edge.tolist(),insideOriginalTINFacets=inside,outsideOriginalTINFacets=outside,completeCurrentEdge3DAABBCandidateIDs=ids,positiveDimensionalExact3DCurrentEdgeHits=hits,completeCurrent3DEdgeIntervalUnion=covered(allparts),completeOpposingLocal3DEdgeIntervalUnion=covered(opp),sourceInterfaceContextOnly=True,qualifiedRetainedTerrainFrontier=False))
 assert len(rows)==old['deterministicFrontierHistory'][0]['boundaryEdges']==61
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,retentionRemovalApproved=False,nativeReacceptance=False,seedOriginalTINFacetIDs=sorted(seed),completeSeedSourceBoundaryEdges=61,completeCurrentNativeEdgeCount=len(ce),complete3DAABBCandidatePairCount=candidateTotal,rows=rows,evidenceRefs=refs,qualification='Exactpartial3Dsegment/source-current context only. Opposing localface side does not prove outside whole selecteddomain, authenticplane provenance, full internalmesh/overlap/F32compatibility or support. Actualcollinearity/fullintervalcoverage is zero-tolerance; no point-only/nearplane bridge. No terrainproposal, source root or affected17/allnative/foreign obligation discharge.'))
 print(json.dumps(dict(seedBoundaryEdges=61,completeCandidatePairs=candidateTotal,edgesWithAnyExact3DHits=sum(bool(r['positiveDimensionalExact3DCurrentEdgeHits'])for r in rows),full3DIntervalContextEdges=sum(r['completeCurrent3DEdgeIntervalUnion']for r in rows),opposingFull3DContextEdges=sum(r['completeOpposingLocal3DEdgeIntervalUnion']for r in rows),terrainProposalWritten=False,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
