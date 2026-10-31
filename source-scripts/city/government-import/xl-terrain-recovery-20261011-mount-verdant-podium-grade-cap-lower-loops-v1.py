"""Source-only podium grade/cap paths and two complete original lower loops.

Every641 original facet retained, with all72 true wall failures preserved. Grade
and lower-loop association are diagnostics, not structural, role or current
acceptance. The uninstalled tower never supplies a host, root or bridge.
"""
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as F
import importlib.util,json,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_verify
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v1';DOC=BASE/BATCH
OLD=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006'
SRC=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-original-complete-interfaces-v1'
COARSE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-finite-v1'
PAIRED=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-paired-refinement-v1'
UID='landsd/75782:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in (SRC,COARSE,PAIRED):
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert next(r for r in receipt['evidenceRefs']if r['path']==str((folder/'diagnostic.json.gz').relative_to(ROOT)))==ref(folder/'diagnostic.json.gz');refs.extend((ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')))
 row=next(r for r in read(OLD/'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'
 tri=decode_original_world_triangles(asset.read_bytes());assert tri.shape==(641,3,3);source=next(r for r in read(SRC/'diagnostic.json.gz')['completeSources']if r['uid']==UID);assert digest(tri.tobytes())==source['completeOriginalWorldSHA256'];inv=census(tri,list(range(641)));assert inv==source['completeEdgeCensus'];parts=inv['sharedEdgeConnectedComponents'];assert [len(p)for p in parts]==[576,10,10,10,10,10,12]
 groundfile=HERE/'local'/COARSE.name/'complete-authentic-source-tin-ground.json.gz';g=read(groundfile);ground=np.asarray(g['completeSelectedFacets'],float);assert digest(ground.tobytes())==g['completeSelectedFacetSHA256']
 cr=read(COARSE/'diagnostic.json.gz')['rows'][0];pr=read(PAIRED/'diagnostic.json.gz');assert cr['uid']==UID and cr['completeOriginalWorldSHA256']==digest(tri.tobytes())==pr['completeOriginalWorldSHA256'] and pr['completeOriginalTINSelectedGroundSHA256']==digest(ground.tobytes());refined={r['sourceFace']:r['independentExactPairedFiniteProof']for r in pr['allSeventyFiveCompletePairedRefinements']};assert len(refined)==75
 proofrows=[]
 for i,r in enumerate(cr['allFaces']):
  assert r['sourceFace']==i;coarse=r['proof'];paired=refined.get(i);selected=coarse if coarse['existingOrdinaryClearanceBoundProved']else paired;assert selected is not None
  proofrows.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=dict(sourceFace=i,completeOriginal=coarse),pairedExactOriginalFiniteBound=paired,completeOriginalBoundProved=selected['existingOrdinaryClearanceBoundProved']))
 helper_names=('exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_upper_ground_interfaces_20261009.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','exact_original_segment_surface_contact_band_20261009.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(ref(HERE/n)for n in helper_names);refs.extend(ref(p)for p in (asset,groundfile,OLD/'selection.json.gz'))
 claim=reservations.claim('mount-podium-grade-caps-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  cb=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical(proofrows));ctx=contexts(tri,ground,proofrows,expected_binding=cb,current_binding=cb);assert reservations.heartbeat(lease)['ok']
  binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([]));caps=cap_verify(tri,ctx,[],expected_binding=binding,current_binding=binding);assert len(caps['affectedOriginalWallFaces'])==72;assert all(i in parts[0]for i in caps['affectedOriginalWallFaces']);print(dict(walls=72,allClearCapPaths=caps['allAffectedHavePaths'],unexposedWallFaces=caps['rawExposureFailures']),flush=True)
  grade=exact_upper_ground_interfaces(tri,parts[0],ground);assert reservations.heartbeat(lease)['ok'];print(dict(completeMainBodyGradeInterfaces=len(grade)),flush=True)
  normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],size,out=np.zeros(len(tri)),where=size!=0);roofs=[i for i in parts[0]if ratio[i]>.25 and ctx[i]['minimum']['minimumGapM']>=-.5];assert roofs
  detailrecords=[];fig=plt.figure(figsize=(18,9),dpi=100)
  for panel,k in enumerate((1,6)):
   ids=parts[k];part=tri[ids];low=part.min((0,1));high=part.max((0,1));bottom=float(low[1]);edges=defaultdict(list)
   for i in ids:
    for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
     if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
   bottomfaces=[i for i in ids if np.all(tri[i,:,1]==bottom) and ratio[i]<-.25]
   if bottomfaces:
    floor_edges=Counter(e for i in bottomfaces for e in [tuple(sorted((tuple(a),tuple(b))))for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0))]if e[0]!=e[1]);lower=sorted(e for e,n in floor_edges.items()if n==1);kind='complete-original-bottom-facet-union-perimeter'
   else:
    lower=sorted(e for e,m in edges.items()if len(m)==1 and e[0][1]==e[1][1]==bottom);kind='complete-original-open-bottom-boundary'
   incidence=Counter(v for e in lower for v in e);cycle=bool(lower)and all(n==2 for n in incidence.values());bands=[]
   for e in lower:
    proof=verify_contact_segment(np.asarray(e),tri[roofs]);proof['completeOriginalSurfacePieces']=[{**p,'originalPodiumMainBodyRoofFace':roofs[p['originalSurfaceFace']]}for p in proof['completeOriginalSurfacePieces']];bands.append(dict(completeOriginalLowerEdge=[list(v)for v in e],completeFiniteUpperRoofBand=proof));assert reservations.heartbeat(lease)['ok']
   bounds=np.array([low-1.5,high+1.5]);near=[int(i)for i in parts[0]if np.all(tri[i].max(0)>=bounds[0])and np.all(tri[i].min(0)<=bounds[1])];center=(low+high)/2;ax=fig.add_subplot(1,2,panel+1,projection='3d');ax.add_collection3d(Poly3DCollection((tri[near]-center)[:,:,[0,2,1]],facecolors='#849ba8',edgecolors='#455b67',alpha=.42,linewidths=.3));ax.add_collection3d(Poly3DCollection((part-center)[:,:,[0,2,1]],facecolors='#dd893b',edgecolors='#693813',alpha=.97,linewidths=.7));s=(bounds-center)[:,[0,2,1]];ax.set_xlim(s[0,0],s[1,0]);ax.set_ylim(s[0,1],s[1,1]);ax.set_zlim(s[0,2],s[1,2]);ax.set_box_aspect(s[1]-s[0]);ax.view_init(24,-64);ax.set_title('Complete original podium part '+str(k)+'; '+str(len(ids))+' faces');ax.set_xlabel('Original X(m)');ax.set_ylabel('Original Z(m)');ax.set_zlabel('Original Y(m)')
   detailrecords.append(dict(originalPodiumComponent=k,completeOriginalSourceFaces=ids,completeOriginalSourceTriangles=part.tolist(),completeOriginalBounds=[low.tolist(),high.tolist()],completeOriginalPartEdgeCensus=census(tri,ids),wholeOrdinaryFiniteClearanceProved=all(ctx[i]['minimum']['minimumGapM']>=-.5 for i in ids),lowerBoundaryKind=kind,completeOriginalBottomFaces=bottomfaces,completeOriginalLowerEdges=[[list(v)for v in e]for e in lower],wholeLowerPerimeterDegreeTwo=cycle,wholeLowerPerimeterBandProofs=bands,allCompleteLowerEdgesWithinExistingBand=cycle and all(p['completeFiniteUpperRoofBand']['verifiedCompleteOriginalEdgeContactBand']for p in bands),allOtherOriginalOpenBoundaryEdges=[[list(v)for v in e]for e,m in edges.items()if len(m)==1 and e not in lower],conditionalHostCompleteSourceFaces=parts[0],conditionalHostRootStillIndependent=True,exactNoContactPreserved=True,structuralRootOrBridgeCredit=False,authoredRoleAccepted=False,croppedVisualMainBodyContextFaces=near,croppedVisualContextNotFullPhysicalScope=True))
  DOC.mkdir(parents=True);png=DOC/'original-two-podium-details-1800x900.png';fig.tight_layout();fig.savefig(png);plt.close(fig);refs.append(ref(png));assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(tri.tobytes()),completeOriginalGroundSHA256=digest(ground.tobytes()),complete641FacetProofRows=proofrows,complete641OriginalFacetContexts=ctx,all72WallRawNegativesPreserved=True,completeMainBody576OriginalFaces=parts[0],completeMainBodyOriginalGradeInterfaces=grade,strictClearCapWallPaths=caps,completeTwoDetachedDetailLowerLoopDiagnoses=detailrecords,completeOriginalNonrenderingFacesRetained=inv['exactNonrenderingOriginalFaces'],uninstalledTowerNeverSuppliesHostRootOrBridge=True,sourceOnly=True,currentRendererGround=False,currentAcceptance=False,terrainProposalCreated=False,structuralRootCredit=False,nativeReacceptance=False,authoredRoleAccepted=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helper_names[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-mount-verdant-podium-original-authentic-grade-strict-cap-two-full-lower-loop-source-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],all72WallsHaveStrictCapPath=caps['allAffectedHavePaths'],unexposedWallFaces=caps['rawExposureFailures'],completeMainBodyGradeInterfaces=len(grade),allTwoCompleteLowerLoopsWithinExistingBand=all(p['allCompleteLowerEdgesWithinExistingBand']for p in detailrecords),sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
