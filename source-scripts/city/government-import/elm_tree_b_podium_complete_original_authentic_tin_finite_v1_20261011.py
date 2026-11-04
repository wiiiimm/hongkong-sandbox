"""DRAFT all12928 unchanged original Elm B/P facets vs exact cached original11-SE-11C TIN.
Diagnostic only: original TIN differs from actual ground; no proposal, root/bridge,
current acceptance, source edits, broad body role or foreign-regression discharge.
Root full-read required before execution; preserves every prior current negative.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,time,uuid,numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elm-tree-b-podium-complete-original-authentic-tin-finite-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
IDENT=B/'government-xl-elm-tree-b-podium-frozen-source-identity-context-v1-20261011';NOM=B/'government-xl-fixed295-simple-source-support-nomination-census-v1-20261011';CAP=B/'government-xl-beverly-elm-complete-current-support-ground-capture-v2-20261011';CONTACT=B/'government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011';CURRENT=B/'government-xl-elm-tree-original-podium-complete-current-finite-ground-diagnostic-v1-20261011';OLD=B/'government-xl-elm-tree-podium-physical-20261007'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for doc in [IDENT,NOM,CAP,CONTACT,CURRENT]:
  receipt=read(doc/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(doc/n)for n in ['result.json','diagnostic.json.gz']if(doc/n).exists())
 identity=read(IDENT/'diagnostic.json.gz');assert all(not r['fixedSpatialBoundsOnlyFailedFields']for r in identity['rows']);tower=next(r for r in read(NOM/'diagnostic.json.gz')['rows']if r['uid']=='landsd/253874:0');p=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']=='landsd/258892:0');old=next(r for r in read(OLD/'selection.json.gz')['rows']if r['uid']=='landsd/258892:0');assert old['native']['sheet']=='11-SE-11C'and old['sourceSHA256']==p['candidate']['entry']['sha256'];contact=read(CONTACT/'diagnostic.json.gz');sources=[]
 for uid,assetref,n,worldsha in [('landsd/253874:0',tower['sourceAsset'],12164,contact['completeTowerWorldSHA256']),('landsd/258892:0',ref(ROOT/p['candidate']['path']),764,contact['completePodiumWorldSHA256'])]:
  asset=ROOT/assetref['path'];assert ref(asset)==assetref;world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(n,3,3)and digest(world.tobytes())==worldsha and np.isfinite(world).all();sources.append((uid,assetref,world));refs.append(assetref)
 terrain_record=read(OLD/'terrain.json');sourcefiles=terrain_record['sourceFiles'];assert len(sourcefiles)==2;gltf=next(ROOT/r['path']for r in sourcefiles if r['path'].endswith('.gltf'));assert 'sheets/11-SE-11C/terrain/'in str(gltf)
 for r in sourcefiles:assert ref(ROOT/r['path'])==r;refs.append(r)
 folder=HERE/'local/government-xl-owned-57-sequence-20261006-253874-0/sheets/11-SE-11C';decoder=module('elm_original_terrain_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL;whole=decoder.terrain_triangles(gltf);assert whole.ndim==3 and whole.shape[1:]==(3,3)and np.isfinite(whole).all();allworld=np.concatenate([w for _,_,w in sources]);lo=allworld.min((0,1));hi=allworld.max((0,1));keep=(whole[:,:,0].max(1)>=lo[0])&(whole[:,:,0].min(1)<=hi[0])&(whole[:,:,2].max(1)>=lo[2])&(whole[:,:,2].min(1)<=hi[2]);ground=whole[keep];assert len(ground)
 groundfile=LOCAL/'complete-original-tin-covering-whole-facets.json.gz';save(groundfile,dict(sourceSheet='11-SE-11C',completeOriginalSheetFacets=len(whole),completeOriginalSheetSHA256=digest(whole.tobytes()),completeSelectedFacets=ground.tolist(),completeSelectedFacetIds=np.flatnonzero(keep).tolist(),completeSelectedFacetSHA256=digest(ground.tobytes()),sourceBounds=[lo.tolist(),hi.tolist()],selection='Every unchanged whole original facet whose closedXZ AABB intersects complete two-source bounds; no clipping, slope filter, resampling, artificial heights or retained-parent proposal.',currentDrawnGround=False));refs.append(ref(groundfile))
 refs.extend(ref(x)for x in [OLD/'selection.json.gz',OLD/'terrain.json',folder/'original/download.json',folder/'directory/result.json',CAP/'selection.json.gz',CAP/'support-source-preflight.json'])
 for repair in sorted((LOCAL/'terrain-repairs').rglob('*'))if(LOCAL/'terrain-repairs').exists()else []:
  if repair.is_file():refs.append(ref(repair))
 refs.extend(ref(HERE/(x+'.py'))for x in ['xl-second-pass','exact_packed_world_geometry_20261009','exact_original_face_conservative_clearance_v5_20261010','exact_original_projection_coverage_v2_20261010','exact_original_triangle_pair_column_gap_20261010']);claim=reservations.claim('elm-original-tin-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 try:
  for uid,assetref,world in sources:
   binding=dict(producer=ref(Path(__file__)),source=assetref,completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),ground=ref(groundfile));checkpoint=LOCAL/(uid.replace('/','-').replace(':','-')+'-partial.json.gz');partial=read(checkpoint)if checkpoint.exists()else None;assert partial is None or partial['binding']==binding;faces=[]if partial is None else partial['allFaces'];assert [r['sourceFace']for r in faces]==list(range(len(faces)))
   for i in range(len(faces),len(world)):
    proof=finite(world[i],ground);lower=F(proof['exactCertifiedLowerClearanceM']);pieces=[]
    if proof['groundProjectionCovered']and lower< -F(1,2):
     pieces=[dict(originalGroundFace=j,proof=column(world[i],ground[j]))for j in proof['allProjectedBoundingCandidateOriginalGroundFacets']];gaps=[F(x['proof']['exactMinimumFiniteColumnGapM'])for x in pieces if x['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps;lower=min(gaps)
    faces.append(dict(sourceFace=i,completeFiniteProof=proof,allRefinedFiniteColumnPairs=pieces,exactLowerM=str(lower),ordinaryFiniteProved=bool(proof['groundProjectionCovered']and lower>=-F(1,2)),strictPositiveFiniteProved=bool(proof['groundProjectionCovered']and lower>0)))
    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];save(checkpoint,dict(binding=binding,allFaces=faces));print(json.dumps(dict(uid=uid,faces=len(faces),total=len(world))),flush=True);last=time.monotonic()
   save(checkpoint,dict(binding=binding,allFaces=faces,complete=True));rows.append(dict(uid=uid,source=assetref,completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=len(world),allFaces=faces,ordinaryFailingFaces=[r['sourceFace']for r in faces if not r['ordinaryFiniteProved']],coverageFailingFaces=[r['sourceFace']for r in faces if not r['completeFiniteProof']['groundProjectionCovered']],minimumCertifiedOrRefinedLowerM=str(min(F(r['exactLowerM'])for r in faces))))
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs);save(DOC/'diagnostic.json.gz',dict(uids=[u for u,_,w in sources],rows=rows,completeOriginalSourceFaces=12928,completeRelevantOriginalTINFacets=len(ground),sourceOnly=True,currentAcceptance=False,installationApproved=False,terrainProposalCreated=False,sourceGeometryChanges=0,terrainGeometryChanges=0,currentDrawnGround=False,actualF32TowerBNotCaptured=True,originalOnlyNotFourStreamProof=True,ordinaryThresholdM='-1/2',strictPositiveSeparate=True,rawCurrentBurial223FacetsPreserved=True,full306TowerBodyObligationsRemain=True,gradeRootProved=False,foreignNativeRegressionsDischarged=False,evidenceRefs=refs,qualification='Whole unchanged original12928 facets versus authentic cached source11-SE-11C TIN only. No current drawn-ground/F32 clearance, genuine grade/root, foreign/native protection, terrain seam feasibility, or source-supported detail roles inferred. Existing223 current buried podiumfacets and BASIC233656/253871 historical regressions remain. Exact authenticTIN changes would require a distinct bounded source-derived proposal and full current protected-actor proof.'));print(json.dumps(dict(rows=[{k:v for k,v in r.items()if k!='allFaces'}for r in rows],currentAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
