"""UNEXECUTED source-only terrain/witness feasibility. No patch or acceptance."""
import importlib.util,json,sys,types
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
BASE=ROOT/'docs/astra-city/government-import';DRAFT=BASE/'government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v1-20261013';OUT=DRAFT/'calculation-v1'
CAPTURE=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013';CONTEXT=BASE/'government-xl-polyu-sports305582-saved-failure-source-context-v2-20261013';NAM=BASE/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
UID='landsd/305582:0';P='landsd/305793:0';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def scene_faces(g):
 seen=set();count=0
 def visit(i):
  nonlocal count
  assert i not in seen;seen.add(i);n=g['nodes'][i]
  if 'mesh'in n:
   for p in g['meshes'][n['mesh']]['primitives']:
    assert p.get('mode',4)==4;a=p['indices']if'indices'in p else p['attributes']['POSITION'];assert g['accessors'][a]['count']%3==0;count+=g['accessors'][a]['count']//3
  for j in n.get('children',[]):visit(j)
 for i in g['scenes'][g.get('scene',0)]['nodes']:visit(i)
 return count

def preflight():
 assert not OUT.exists();contract=read(DRAFT/'input-contract.json');pins={p['path']:p['sha256']for p in contract['filePins']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==CURRENT and before==(CAPTURE/'captured-manifest.json').read_bytes()
 data=read(CAPTURE/'complete-sports-four-stream-current-ground-inputs.json.gz');cap=read(CAPTURE/'complete-current-actual-source-and-ground-305582-0.json.gz');inputs=read(CAPTURE/'capture-inputs.json.gz');ctx=read(CONTEXT/'saved-failure-source-context.json.gz')
 assert data['uid']==UID and data['sourceSHA256']==contract['sourceSHA256']and ctx['captureJob']=='74fc230cb2ea65e352f2d47ec20440f455bc6ae428158ba68472ab528a37bf5e'and ctx['finiteGradeJob']=='1c3dd3740d3c812b90214de76073cdf51e9e178591a2401b3c3c46f60127b229'
 assert len(data['completeWorldStreams'])==4 and len(ctx['rows'])==4 and len(data['completeOriginalTopologyVerbatim']['sharedEdgeConnectedComponents'])==21 and len(data['completeOriginalTopologyVerbatim']['exactNonrenderingOriginalFaces'])==4
 assert inputs['installedPodiumDependency']['entry']['uid']==P and inputs['installedPodiumDependency']['entry']['publicationApproved']is False
 for row in ctx['rows']:
  w=np.asarray(data['completeWorldStreams'][row['arithmetic']]['completeWorldTriangles'],dtype='<f8');assert w.shape==(10536,3,3)and digest(w.tobytes())==row['completeWorldSHA256'];assert len(row['all752FullSavedFailures'])==752 and row['summary']=={'actualPairedWitnessFailures':752,'coverageFailures':0,'conservativeOnlyFailures':0}
 terrain=contract['terrain'];folder=ROOT/terrain['folder'];download=read(ROOT/terrain['originalReceipt']);directory=read(ROOT/terrain['directoryReceipt']);assert download['sheet']==directory['sheet']=='11-NW-25C'and download['terrainGeometryIncluded']and download['directorySHA256']==directory['directorySHA256']==terrain['directorySHA256']
 files=[e for e in download['entries']if e['name'].startswith('TERRAIN')and e['name'].endswith(('.gltf','.bin'))];assert files==terrain['allOriginalTerrainFiles'];declared=0
 for e in files:
  p=folder/'terrain'/e['name'];assert len(p.read_bytes())==e['bytes']and digest(p.read_bytes())==e['sha256']
  if p.suffix=='.gltf':declared+=scene_faces(read(p))
 assert declared==terrain['declaredOriginalFacets']==181089
 # Four COMPLETE unused-POSITION envelopes define a conservative closed core,
 # not a mask fit to the failing faces, roof interpretation or ownership claim.
 bounds=np.asarray([cap['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*cap['completeWholeUnusedVertexBounds']],dtype='<f8');assert bounds.shape==(4,2,3)and cap['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']and np.isfinite(bounds).all()
 core=[float(bounds[:,0,0].min()),float(bounds[:,0,2].min()),float(bounds[:,1,0].max()),float(bounds[:,1,2].max())]
 current=np.asarray(data['completeDrawnGround'],dtype='<f8');assert current.shape==(12,3,3)and digest(current.tobytes())==data['completeDrawnGroundSHA256'];parent=[float(current[:,:,0].min()),float(current[:,:,2].min()),float(current[:,:,0].max()),float(current[:,:,2].max())]
 assert parent[0]<=core[0]<=core[2]<=parent[2]and parent[1]<=core[1]<=core[3]<=parent[3]
 comp=read(NAM/'composition.json.gz');assert comp['completeCurrentNativeActors']==6650 and comp['currentManifest']['sha256']==CURRENT
 baseline=read(ROOT/comp['baselineInventory']['path']);delta=read(ROOT/comp['actualNewDelta']['path']);binding=read(ROOT/comp['exactBaselineCurrentBinding']['path']);nam_inputs=read(NAM/'input.json.gz');native=baseline['rows']+delta['rows'];assert len(native)==6650 and len({r['uid']for r in native})==6650
 assert len(binding['rows'])==6649 and binding['exactAllSourceFormEntryLoaderTuples']is True
 for p,h in nam_inputs['requiredUnchangedProductionClosure'].items():assert digest((ROOT/p).read_bytes())==h,p
 by={r['uid']:r for r in native}
 for z in binding['rows']:assert canonical(by[z['uid']])==z['unchangedActualBoundsSHA256']and canonical(nam_inputs['currentAllNativeSourceForms'][z['uid']])==z['currentViewerFormSHA256']and digest((ROOT/z['source']['path']).read_bytes())==z['source']['sha256']
 for r in native:assert r['wholeUnusedPositionVerticesIncluded']is True and r['sourceFacesOmitted']==0
 decoder=module('polyu_authentic_complete_decoder',HERE/'xl-second-pass.py');forms_module=module('polyu_feasibility_forms','xl-final-script-pass.py')
 code=[]
 for m in list(sys.modules.values())+[decoder,forms_module]:
  if isinstance(m,types.ModuleType)and getattr(m,'__file__',None):
   p=Path(m.__file__).resolve()
   if ROOT in p.parents and p.is_file():code.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 assert(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 return dict(contract=contract,pins=pins,before=before,data=data,cap=cap,inputs=inputs,context=ctx,folder=folder,files=files,declared=declared,core=core,parent=parent,native=native,decoder=decoder,forms_module=forms_module,importedCodePins=sorted({r['path']:r for r in code}.values(),key=lambda r:r['path']))
def calculate(s):
 OUT.mkdir();s['decoder'].LOCAL=OUT/'faithful-schema-only-descriptors';fragments=[];lineage=[]
 for e in s['files']:
  if not e['name'].endswith('.gltf'):continue
  p=s['folder']/'terrain'/e['name'];w=s['decoder'].terrain_triangles(p);assert len(w)==scene_faces(read(p))and np.isfinite(w).all();fragments.append(w);lineage.append(dict(sourcePath=str(p.relative_to(ROOT)),sourceSHA256=digest(p.read_bytes()),completeFacets=len(w),completeWorldSHA256=digest(np.asarray(w,dtype='<f8').tobytes())))
 full=np.concatenate(fragments).astype('<f8');assert full.shape==(181089,3,3);xz=full[:,:,[0,2]];d=s['parent'];ids=np.flatnonzero((xz.max(1)[:,0]>=d[0])&(xz.min(1)[:,0]<=d[2])&(xz.max(1)[:,1]>=d[1])&(xz.min(1)[:,1]<=d[3]));assert len(ids);ground=full[ids];gsha=digest(ground.tobytes());cache={};rows=[]
 # Existing exact point finite proof is a NEW authentic-source witness context,
 # never a full facet/core/support/sampler or physical acceptance certificate.
 for row in s['context']['rows']:
  witnesses=[]
  for failed in row['all752FullSavedFailures']:
   for v in failed['allSavedPairedGapViolationWitnesses']:
    old=v['savedExactWitnessVerbatim'];point=tuple(old['exactOriginalSourcePoint']);key=(point,gsha)
    if key not in cache:
     face=np.asarray([[float(F(a))for a in point]]*3,dtype='<f8')
     try:
      a=coarse(face,ground);b=None if a['existingOrdinaryClearanceBoundProved']else paired(face,ground);cache[key]=dict(pointDoubleQuerySHA256=digest(face.tobytes()),exactSavedPointRetained=point,queryUsesNearestFloat64NotRationalUniversalCertificate=True,coarse=a,paired=b,existingPointOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
     except AssertionError as err:cache[key]=dict(pointQueryContractFailure=str(err),pointQueryIsUnqualified=True)
    witnesses.append(dict(sourceFace=failed['sourceFace'],originalComponent=failed['originalComponent'],orientationDescriptiveOnly=failed['orientationLabelVerbatim'],actualCurrentViolationVerbatim=v,authenticSourcePointContext=cache[key],noWholeFacetOrPhysicalAcceptance=True))
  rows.append(dict(arithmetic=row['arithmetic'],all752FailureRecordsVerbatim=row['all752FullSavedFailures'],allSavedViolationWitnessAuthenticContexts=witnesses))
 forms=s['forms_module'].load_forms(s['parent']);formuids={f['uid']for f,_,_ in forms};protected=s['inputs']['completeCurrentForms'];forms_by={f['uid']:dict(form=f,tile=t)for f,_,t in forms}
 for f in protected:
  if f['uid']in forms_by:assert forms_by[f['uid']]['form']==f
  else:forms_by[f['uid']]=dict(form=f,tile=None,explicitCoupledOrIndependentProtectedActor=True)
 overlaps=[]
 for r in s['native']:
  bounds=[r['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],r['completeLiteralBounds'],r['completeLeftAssociatedF32Bounds'],r['completeBalancedF32Bounds']]
  touched=[i for i,(lo,hi)in enumerate(bounds)if hi[0]>=d[0]and lo[0]<=d[2]and hi[2]>=d[1]and lo[2]<=d[3]]
  if touched:overlaps.append(dict(uid=r['uid'],arithmeticViews=touched,completeActualBoundsRecordVerbatim=r,requiresWholeActualBeforeAfterTerrainProof=True))
 save(OUT/'feasibility.json.gz',dict(uid=UID,sourceCoreClosedAABBFromWholeUnusedFourViews=s['core'],provisionalParentRoutingEnvelope=s['parent'],collarWidthNotChosen=True,allCurrent12GroundFacetsVerbatim=s['data']['completeDrawnGround'],allGroundFacetOriginsVerbatim=s['cap']['currentDrawnGround']['completeRegionalFacetOrigins'],allSource181089FacetsSHA256=digest(full.tobytes()),completeTerrainSourceLineage=lineage,conservativeClosedNominationOriginalTerrainIds=ids.tolist(),allNominatedAuthenticTerrainFacets=ground.tolist(),allSourceSlopesVerticalsAndZerosRetainedWithoutHeightLayerDeletion=True,rows=rows,all21BodyAndOriginalZeroBindingsVerbatim=s['data']['completeOriginalTopologyVerbatim'],fullCurrentProtectedForms=list(forms_by.values()),sourceFormNominationIsConservativeNotActualMeshExclusion=True,complete6650NativeBoundsAccounted=True,nativeOverlaps=overlaps,nativeStrictlyDisjoint=len(s['native'])-len(overlaps),installedPodiumDependencyVerbatim=s['inputs']['installedPodiumDependency'],futureConstructionRequirements=['allOriginalCoreLayersRetained','completeClosedTransitionAndActualFloat32Packing','unchangedParentExterior','current12GroundParentCellRouting','fullActualAffectedBasicAndNativeBeforeAfter','realProductionMaxHeightAndSampler','existing.01mJoins','25000TerrainFacets','ordinaryMinus.5m','wholeSportsSourceRoleRootsAndTerminalParts','separateInnovationCommunalAndSuppressedLee','nativePodiumPublicationHoldRemainsFalse'],noPatchGenerated=True,noSourceGeometryChange=True,noDB=True,noLease=True,noCurrentFiniteContactCensusReplay=True,currentAcceptance=False,physicalAccepted=False,sourceRoleInterpretationAccepted=False))
 for p,h in s['pins'].items():assert digest((ROOT/p).read_bytes())==h,p
 for pin in s['importedCodePins']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256'],pin['path']
 assert(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==s['before'];print(json.dumps(dict(output=str((OUT/'feasibility.json.gz').relative_to(ROOT)),sha256=digest((OUT/'feasibility.json.gz').read_bytes()),declaredOriginalTerrainFacets=181089,selectedClosedTerrainFacets=len(ids),uniqueAuthenticPointQueries=len(cache),affectedForms=len(forms_by),nativeOverlaps=len(overlaps),noPatch=True,currentAcceptance=False)),flush=True)
def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noDB=True,noLease=True,noTerrainDecoded=True,noWitnessOrConstructionPredicatesRun=True,declaredOriginalTerrainFacets=181089,sourceSlots=42144,closedSourceCore=s['core'],provisionalParentEnvelope=s['parent'],completeNativeBounds=6650,importedCodePins=s['importedCodePins'])),flush=True);return
 assert '--calculate-authentic-source-feasibility-only'in sys.argv;calculate(s)
if __name__=='__main__':main()
