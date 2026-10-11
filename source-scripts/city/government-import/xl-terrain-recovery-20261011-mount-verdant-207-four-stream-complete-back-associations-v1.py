"""Complete207 source-only mount association diagnoses in four arithmetic streams.

170 entire authored openings, 34 six-face back patches, three two-face backs.
Every body retained; no function/visual/root/bridge/current host qualification.
Same fixed finite .1m kernels; exact original failures remain immutable.
"""
from pathlib import Path
import importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_band
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-207-four-stream-complete-back-associations-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1';CLOSED=BASE/'xl-terrain-recovery-20261011-mount-verdant-34-complete-backing-patches-context-v1';LONG=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-long-original-backing-facets-v1';CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder,name in [(PRIOR,'diagnostic.json.gz'),(CLOSED,'diagnostic.json.gz'),(LONG,'diagnostic.json.gz'),(CAPTURE,'actual-render-attributes.json.gz')]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert ref(folder/name)in receipt['evidenceRefs'];receipts[folder.name]=receipt;refs.extend([ref(folder/'result.json'),ref(folder/name)])
 source=read(CAPTURE/'literal-source-inputs.json.gz');actual=read(CAPTURE/'actual-render-attributes.json.gz');assert ref(CAPTURE/'literal-source-inputs.json.gz')in receipts[CAPTURE.name]['evidenceRefs'];refs.append(ref(CAPTURE/'literal-source-inputs.json.gz'));uids=['landsd/261717:0','landsd/75782:0'];assert [r['uid']for r in source['rows']]==[r['uid']for r in actual['rows']]==uids;worlds=[[],[],[],[]];counts=[14938,641]
 fields=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
 for row,captured,count in zip(source['rows'],actual['rows'],counts):
  asset=ROOT/row['path'];assert digest(asset.read_bytes())==row['entry']['sha256']==captured['sourceSHA256'];refs.append(ref(asset));original=decode_original_world_triangles(asset.read_bytes());index=np.asarray(captured['completeOriginalIndex'],np.uint32).reshape(-1,3);assert original.shape==(count,3,3)and len(index)==count;worlds[0].append(original)
  for mode,field in enumerate(fields,1):
   position=np.asarray(captured[field],float).reshape(-1,3);assert np.isfinite(position).all()and np.all(index<len(position));worlds[mode].append(position[index])
 worlds=[np.concatenate(parts)for parts in worlds];assert all(w.shape==(15579,3,3)for w in worlds);original=read(PRIOR/'diagnostic.json.gz');assert digest(worlds[0].tobytes())==original['complete15579PairWorldSHA256'];hostids=original['completeHostGlobalFaceIDs'];closed=read(CLOSED/'diagnostic.json.gz');long=read(LONG/'diagnostic.json.gz');mapping={}
 for r in original['all207Bodies2682Faces']:
  if r.get('completeBoundaryWithinFixedBand'):mapping[r['originalBody']]=dict(kind='complete-original-incidence-one-opening',allBodyFaces=r['completeOriginalGlobalFaceIDs'],backPatchFaces=None)
 for r in closed['completeAll34OriginalClosed28FaceBodies']:
  assert r['wholeBackingPatchAndPerimeterWithinExistingBand'];mapping[r['originalBody']]=dict(kind='complete-six-facet-authored-backing-patch',allBodyFaces=r['all28OriginalBodyFaces'],backPatchFaces=r['completeBackingPatch']['completeBackingOriginalFaceIDs'])
 for r in long['all30OriginalLongStripFaces']:
  assert r['conditionalCompleteBackingPatchPositive'];mapping[r['originalBody']]=dict(kind='complete-two-facet-authored-backing-patch',allBodyFaces=r['all10CompleteOriginalFaces'],backPatchFaces=r['completePositiveFacetPatch']['completeBackingOriginalFaceIDs'])
 assert set(mapping)=={r['originalBody']for r in original['all207Bodies2682Faces']}and len(mapping)==207 and sum(len(r['allBodyFaces'])for r in mapping.values())==2682;assert not set(fi for r in mapping.values()for fi in r['allBodyFaces'])&set(hostids)
 context=HERE/'xl-terrain-recovery-20261011-mount-verdant-34-complete-backing-patches-context-v1.py';spec=importlib.util.spec_from_file_location('patch',context);patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)
 names=['exact_packed_world_geometry_20261009.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend([ref(context),*[ref(HERE/n)for n in names]]);modes=['untouched-provider-original','captured-literal','explicit-left-associated-Float32','explicit-balanced-Float32'];binding=dict(worldSHA256=[digest(w.tobytes())for w in worlds],completeHostGlobalFaces=hostids,completeBodyAndBackingMappings=mapping,refs=refs);binding=json.loads(json.dumps(binding));progress=LOCAL/'compute-progress.json.gz';saved=read(progress)if progress.exists()else None;assert saved is None or saved['binding']==binding;rows=[]if saved is None else saved['rows'];order=[(mode,body)for mode in range(4)for body in sorted(mapping)];assert [(r['modeIndex'],r['originalBody'])for r in rows]==order[:len(rows)]
 claim=reservations.claim('mount207-fourstreams-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();save(progress,dict(binding=binding,rows=rows,complete=False));print(json.dumps(dict(completeStreamBodies=len(rows),total=828)),flush=True)
 try:
  for mode,body in order[len(rows):]:
   world=worlds[mode];entry=mapping[body];ids=entry['allBodyFaces'];patchfaces=ids if entry['backPatchFaces']is None else entry['backPatchFaces'];inventory=patch.patch_inventory(world,patchfaces);facets=[]
   if entry['backPatchFaces']is not None:
    for fi in patchfaces:facets.append(dict(originalGlobalBackingFace=fi,proof=facet_band(world[fi],world[hostids])));pulse()
   edges=[]
   for edge in inventory['completeBackingBoundaryEdges']:edges.append(dict(completeArithmeticBackingBoundaryEdge=edge,proof=edge_band(np.asarray(edge),world[hostids])));pulse()
   positive=inventory['everyBackingFaceSharedEdgeConnected']and inventory['completeBoundaryDegreeTwo']and not inventory['backingWindingConflicts']and not inventory['backingNonmanifoldEdges']and len(edges)==(4 if entry['backPatchFaces']is None or len(patchfaces)==2 else len(inventory['completeBackingBoundaryEdges']))and all(r['proof']['wholeFacetAssociated']for r in facets)and all(r['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in edges)
   rows.append(dict(modeIndex=mode,mode=modes[mode],originalBody=body,kind=entry['kind'],completeAllOriginalBodyFaces=ids,completeBodyArithmeticTrianglesSHA256=digest(world[ids].tobytes()),completeBackingPatchOrOpeningInventory=inventory,completeAllBackingFacetProofs=facets,completeWholeBoundaryProofs=edges,conditionalWholeBackingAssociationPositive=positive,rawOriginalBodyAndOpenLoopFailuresPreserved=True,hostPhysicalQualificationStillRequired=True,visualRoleAccepted=False,rootOrBridgeCredit=False));pulse()
  assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/r['path'])==r for r in refs);save(progress,dict(binding=binding,rows=rows,complete=True));out=dict(uid=uids[0],complete15579Worlds=[dict(mode=mode,completeWorldSHA256=digest(world.tobytes()))for mode,world in zip(modes,worlds)],all207Bodies2682FacesEveryArithmeticStream=rows,summary=[dict(mode=mode,positive=sum(r['conditionalWholeBackingAssociationPositive']for r in rows if r['mode']==mode),negativeBodies=[r['originalBody']for r in rows if r['mode']==mode and not r['conditionalWholeBackingAssociationPositive']])for mode in modes],frozenCapturedManifestSHA256=source['currentManifest']['sha256'],sourceOnly=True,freshCurrentAcceptance=False,explicitF32ArithmeticNotUniversalGPUCameraClaim=True,conditionalHostGroundingStillUnqualified=True,visualRoleAccepted=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/names[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount207-complete-original-literal-two-F32-backing-associations-diagnostic-v1',[ROOT/r['path']for r in refs]+[progress,DOC/'diagnostic.json.gz'],dict(uids=[uids[0]],sourceOnly=True,currentAcceptance=False,completeFourStream207BodySummary=out['summary'],newlyInstalled=0));print(json.dumps(out['summary']),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
