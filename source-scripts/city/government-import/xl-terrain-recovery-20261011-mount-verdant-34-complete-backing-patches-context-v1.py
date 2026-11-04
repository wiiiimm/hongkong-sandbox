"""Source-only complete backing patches of all34 original shallow details.

All28 body faces retained, every previously positive backing facet and its whole
incidence-one boundary verified. No role/function/closed-solid/root credit.
Original three tall-loop negatives and representative full source are rendered.
Hosts retain only unqualified source geometric paths, not current ground credit.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,json,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-34-complete-backing-patches-context-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1';SOURCE=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def patch_inventory(tri,ids):
 edges=defaultdict(list)
 for fi in ids:
  points=[tuple(float(v)for v in p)for p in tri[fi]]
  for a,b in zip(points,points[1:]+points[:1]):edges[tuple(sorted((a,b)))].append(dict(face=fi,direction=[a,b]))
 boundary=[edge for edge,rows in edges.items()if len(rows)==1];adj=defaultdict(set)
 for rows in edges.values():
  for a in rows:
   for b in rows:
    if a['face']!=b['face']:adj[a['face']].add(b['face'])
 reached={ids[0]};queue=[ids[0]]
 while queue:
  for b in adj[queue.pop()]-reached:reached.add(b);queue.append(b)
 degrees=defaultdict(int)
 for edge in boundary:
  for point in edge:degrees[point]+=1
 return dict(completeBackingOriginalFaceIDs=ids,completeBackingFaceSHA256=digest(tri[ids].tobytes()),everyBackingFaceSharedEdgeConnected=len(reached)==len(ids),completeBackingAllEdgeIncidences=[dict(edge=[list(p)for p in edge],records=rows)for edge,rows in edges.items()],completeBackingBoundaryEdges=[[list(p)for p in edge]for edge in boundary],completeBoundaryDegreeTwo=bool(boundary)and set(degrees.values())=={2},backingWindingConflicts=[[[float(v)for v in p]for p in edge]for edge,rows in edges.items()if len(rows)==2 and rows[0]['direction']==rows[1]['direction']],backingNonmanifoldEdges=[[[float(v)for v in p]for p in edge]for edge,rows in edges.items()if len(rows)>2])
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(PRIOR/'diagnostic.json.gz')in receipt['evidenceRefs'];d=read(PRIOR/'diagnostic.json.gz');selected=read(SOURCE/'selection.json.gz');worlds=[];assets=[]
 for uid,count in [('landsd/261717:0',14938),('landsd/75782:0',641)]:
  row=next(r for r in selected['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());assert t.shape==(count,3,3);worlds.append(t);assets.append(asset)
 tri=np.concatenate(worlds);assert digest(tri.tobytes())==d['complete15579PairWorldSHA256'];hosts=d['completeHostGlobalFaceIDs'];host=tri[hosts];closed=[r for r in d['all207Bodies2682Faces']if r.get('closed28FaceCompleteFacetCensus')];assert len(closed)==34 and all(len(r['wholeFacetBandPositiveFaceIDs'])==6 for r in closed)
 names=['exact_packed_world_geometry_20261009.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs=[ref(p)for p in [Path(__file__),PRIOR/'result.json',PRIOR/'diagnostic.json.gz',SOURCE/'selection.json.gz',*assets,*[HERE/n for n in names]]];claim=reservations.claim('mount34-backing-context-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 try:
  for original in closed:
   ids=original['completeOriginalGlobalFaceIDs'];patch=patch_inventory(tri,original['wholeFacetBandPositiveFaceIDs']);assert patch['everyBackingFaceSharedEdgeConnected']and not patch['backingWindingConflicts']and not patch['backingNonmanifoldEdges'];proofs=[dict(completeOriginalBackingBoundaryEdge=edge,proof=edge_band(np.asarray(edge),host))for edge in patch['completeBackingBoundaryEdges']];body=tri[ids]
   rows.append(dict(originalBody=original['originalBody'],all28OriginalBodyFaces=ids,completeBodyTrianglesSHA256=digest(body.tobytes()),completeOriginalBounds=[body.min((0,1)).tolist(),body.max((0,1)).tolist()],completeYSpanM=float(np.ptp(body[:,:,1])),completeBackingPatch=patch,allSixWholeFacetPositiveProofsRetained=[r for r in original['all28WholeFacetHostBandProofs']if r['originalGlobalSourceFace']in patch['completeBackingOriginalFaceIDs']],completeBackingPerimeterProofs=proofs,wholeBackingPatchAndPerimeterWithinExistingBand=patch['completeBoundaryDegreeTwo']and all(r['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in proofs),remaining22BodyFacetNegativesPreserved=True,closedSourceEdgeTopologyIsNotSolidOrFunctionCertification=True))
   if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(closedBody=len(rows),total=34)),flush=True)
  failed=[r for r in d['all207Bodies2682Faces']if r.get('openBack10FaceFourEdgeLoop')and not r['completeBoundaryWithinFixedBand']];assert [r['originalBody']for r in failed]==[311,312,313]
  representatives=[next(r for r in d['all207Bodies2682Faces']if r.get('completeBoundaryWithinFixedBand')),failed[0],closed[0]];fig=plt.figure(figsize=(18,10),dpi=100)
  for panel,r in enumerate(representatives):
   ids=r['completeOriginalGlobalFaceIDs'];part=tri[ids];low=part.min((0,1));high=part.max((0,1));bounds=np.asarray([low-.8,high+.8]);near=[i for i in hosts if np.all(tri[i].max(0)>=bounds[0])and np.all(tri[i].min(0)<=bounds[1])];center=(low+high)/2
   for view in range(2):
    ax=fig.add_subplot(2,3,view*3+panel+1,projection='3d');ax.add_collection3d(Poly3DCollection((tri[near]-center)[:,:,[0,2,1]],facecolors='#9baeb8',edgecolors='#526773',alpha=.3,linewidths=.2));ax.add_collection3d(Poly3DCollection((part-center)[:,:,[0,2,1]],facecolors='#e39039',edgecolors='#733e14',alpha=.98,linewidths=.55));s=(bounds-center)[:,[0,2,1]];ax.set_xlim(s[:,0]);ax.set_ylim(s[:,1]);ax.set_zlim(s[:,2]);ax.set_box_aspect(s[1]-s[0]);ax.view_init(22,-62 if view==0 else 118);ax.set_title('Original body '+str(r['originalBody'])+' / '+str(len(ids))+' faces');ax.set_xlabel('X(m)');ax.set_ylabel('Z(m)');ax.set_zlabel('Y(m)')
  DOC.mkdir(parents=True);png=DOC/'original-three-representative-tower-details-1800x1000.png';fig.tight_layout();fig.savefig(png);plt.close(fig);refs.append(ref(png));assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uid='landsd/261717:0',complete15579PairWorldSHA256=digest(tri.tobytes()),completeAll34OriginalClosed28FaceBodies=rows,completeThreeOpenBackFailuresPreserved=failed,conditionalSourceOnlyHostBodyIDsAndFaces=hosts,unqualifiedHostGroundingStillRequired=True,sourceOnly=True,authoredVisualRoleAccepted=False,closedSolidCertification=False,functionInferred=False,structuralRootOrBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/names[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount34-complete-original-backing-facets-perimeter-source-context-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[out['uid']],sourceOnly=True,currentAcceptance=False,all34CompleteBackingAndPerimeterPositive=sum(r['wholeBackingPatchAndPerimeterWithinExistingBand']for r in rows),newlyInstalled=0));print(json.dumps(dict(all34BackingPositive=sum(r['wholeBackingPatchAndPerimeterWithinExistingBand']for r in rows))),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
