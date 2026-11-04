"""Bounded intrinsic original-sheet/backing correspondence for 15 held parts.

This is not another whole-body loop test. Every nonvisual qualified host body
is partitioned into source-defined exact coplanar full-edge surface patches.
Complete original patch boundaries can exist inside a closed body. Candidate
visual parts retain their complete topology, whole current finite clearance,
raw world-band negatives and actual pose. The three curved skins additionally
test their source-defined minimum-Y incident backing fan and whole reciprocal
XZ footprint/finite height correspondence to a genuine complete original roof
patch. Projection-only height ordering is not a .1m world mount or a root.

No role, hole, architectural function, source correction, new current capture,
structural propagation or native acceptance is supplied by this diagnostic.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements15-intrinsic-sheet-backing-and-roof-correspondence-v1';DOC=BASE/BATCH
PARTS=(69,70,75,76,78,705,744,839,890,893,897,902,904,918,921);ROOFS=(839,893,902)
INPUTS=(
 'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1',
 'xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1',
 'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1',
 'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1',
 'xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1',
 'xl-terrain-recovery-20261011-elements-seven-original-host-loop-correspondence-v1',
 'xl-terrain-recovery-20261011-elements-eight-remaining-original-role-context-v1')
HELPERS=(
 'exact_original_full_edge_coplanar_patch_census_v1_20261011.py',
 'test_exact_original_full_edge_coplanar_patch_census_v1_20261011.py',
 'exact_original_body_boundary_group_census_v1_20261011.py',
 'test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'original_coplanar_exterior_continuation_20261009.py',
 'exact_original_shell_intersections_20261009.py',
 'exact_original_shared_edge_component_census_v2_20261011.py',
 'exact_packed_world_geometry_20261009.py',
 'exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',
 'exact_original_projection_coverage_v2_20261010.py',
 'exact_original_paired_finite_clearance_v3_20261011.py',
 'exact_original_paired_finite_clearance_v2_20261010.py',
 'exact_original_closed_projection_intersection_20261010.py',
 'exact_original_facet_backing_footprint_diagnostic_v1_20261011.py',
 'test_exact_original_facet_backing_footprint_diagnostic_v1_20261011.py',
 'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',
 'exact_original_surface_coordinate_band_20261010.py',
 'exact_original_projection_coverage_20261009.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py')
MODES=('providerOriginal','actualLiteral','explicitLeftFloat32','explicitBalancedFloat32')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def nearby_bounds(a,b):return bool((np.abs(a.min((0,1))-b.min((0,1)))<=np.nextafter(.1,np.inf)).all()and(np.abs(a.max((0,1))-b.max((0,1)))<=np.nextafter(.1,np.inf)).all())
def fixed_plane_band(source,host_plane):
 p=tuple(map(F,host_plane));n=p[:3];den=sum(x*x for x in n);assert den>0
 values=[sum(n[i]*F(float(v[i]))for i in range(3))+p[3]for v in source.reshape(-1,3)]
 return dict(allActualSourceVerticesWithinExistingHostPlaneBand=all(v*v<=F(.1)**2*den for v in values),exactSignedUnnormalizedPlaneValues=list(map(str,values)),exactNormalSquaredLength=str(den),fixedBandM=.1,finiteHostInteriorCredit=False)
def projected_bounds_touch(source,hosts,host_plane):
 p=tuple(map(F,host_plane));n=p[:3];den=sum(x*x for x in n);projected=[]
 for raw in source.reshape(-1,3):
  v=tuple(F(float(x))for x in raw);distance=(sum(n[i]*v[i]for i in range(3))+p[3])/den;projected.append(tuple(v[i]-n[i]*distance for i in range(3)))
 return not any(max(v[k]for v in projected)<F(float(hosts[:,:,k].min()))or min(v[k]for v in projected)>F(float(hosts[:,:,k].max()))for k in range(3))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]+[ref(HERE/n)for n in HELPERS]
 for batch in INPUTS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
  for binding in r['evidenceRefs']:
   p=ROOT/binding['path'];assert p.is_file()and ref(p)==binding;refs.append(binding)
 refs=list({(r['path'],r['sha256']):r for r in refs}.values());assert all(ref(ROOT/r['path'])==r for r in refs)
 patches=load('elements_intrinsic_exact_coplanar_patch',HERE/HELPERS[0]);boundary=load('elements_intrinsic_backing_boundary',HERE/HELPERS[2]);fixture=load('elements15_original_complete_fixture',HERE/HELPERS[3]);loops=load('elements_intrinsic_patch_loop',HERE/HELPERS[9]);coverage=load('elements_intrinsic_projection_coverage',HERE/HELPERS[10]);paired=load('elements_intrinsic_plane_height',HERE/HELPERS[11]);footprint=load('elements_intrinsic_finite_backing_footprint',HERE/HELPERS[14]);docs,packages=fixture.actual_fixture();worlds=next(iter(packages.values()))['worlds'];graph=docs['graph'];paths=read(BASE/INPUTS[4]/'diagnostic.json.gz');original=worlds['providerOriginal']
 intrinsic_backing={}
 for body in ROOFS:
  ids=sorted(graph['components'][body]['globalOriginalFaces']);part=original[ids];low=float(part[:,:,1].min());corners=[dict(globalOriginalFace=f,originalCorner=c,completeOriginalVertex=part[k,c].tolist())for k,f in enumerate(ids)for c in range(3)if float(part[k,c,1])==low];fan=sorted({f for f in ids if any(float(v[1])==low for v in original[f])});assert fan
  intrinsic_backing[body]=dict(originalMinimumY=low,allExactSourceMinimumYCorners=corners,completeOriginalIncidentBackingFanFaces=fan,fanChosenFromProviderOriginalBeforeHostAssociation=True,completeBackingFanSourceBoundaryInventory=boundary.census(original,fan))
 claim=reservations.claim('elements15-intrinsic-sheets-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  outputs=[];inventories={}
  for mode in MODES:
   w=worlds[mode];pathrow=next(r for r in paths['rows']if r['mode']==mode);qualified=set(pathrow['qualifiedDiagnosticOwnedBodies']);assert len(qualified)==866 and pathrow['noWholeNativeBodySeed']is True and not qualified.intersection(PARTS);bandrow=next(r for r in docs['bands']['rows']if r['mode']==mode);assert set(bandrow['qualifiedHostOriginalBodies'])==qualified and bandrow['boundedHostPathReceipt']==ref(BASE/INPUTS[4]/'result.json');assert digest(w.tobytes())==bandrow['completeWorldSHA256']
   for uid,offset,count in [('landsd/204145:0',0,12129),('landsd/204143:0',12129,11680)]:
    finite=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid);assert digest(w[offset:offset+count].tobytes())==finite['completeWorldSHA256'];assert len(finite['allFaces'])==count and all(f['strictlyExposedWholeFacet']is True and f['existingOrdinaryClearanceBoundProved']is True and f['closedProjectionCovered']is True for f in finite['allFaces'])
   inventories[mode]=[]
   for body in sorted(qualified):
    item=graph['components'][body];inv=patches.verify(w,sorted(item['globalOriginalFaces']));inventories[mode].append(dict(originalBody=body,actorUID=item['actorUID'],completeSourceDefinedHostPatchInventory=inv));pulse()
   for body in PARTS:
    item=graph['components'][body];ids=sorted(item['globalOriginalFaces']);part=w[ids];sourcepatches=patches.verify(w,ids);a=next(r for r in bandrow['all132OriginalBodyAssociations']if r['originalBody']==body);sheetmatches=[];roofcandidates=[];backingplacements=[]
    for host in inventories[mode]:
     if host['actorUID']!=item['actorUID']:continue
     for hi,hp in enumerate(host['completeSourceDefinedHostPatchInventory']['allSourceDefinedFullEdgeCoplanarPatches']):
      hostids=hp['completeOriginalPatchFaces'];hostfaces=w[hostids]
      # Patch identity candidates require both complete surface-loop extrema,
      # not a clipped virtual host patch made to fit the visual component.
      for si,sp in enumerate(sourcepatches['allSourceDefinedFullEdgeCoplanarPatches']):
       sourcefaces=w[sp['completeOriginalPatchFaces']]
       if body not in ROOFS and sp['exactOriginalPlane'][:3]==hp['exactOriginalPlane'][:3]and projected_bounds_touch(sourcefaces,hostfaces,hp['exactOriginalPlane']):
        footproofs=[dict(globalOriginalSourceFace=f,completeFiniteBackingFootprintProof=footprint.verify(w[f],hostfaces))for f in sp['completeOriginalPatchFaces']];band=fixed_plane_band(sourcefaces,hp['exactOriginalPlane']);normal2=F(band['exactNormalSquaredLength']);values=list(map(F,band['exactSignedUnnormalizedPlaneValues']));squared=max(v*v/normal2 for v in values)
        backingplacements.append(dict(originalSourceSurfacePatch=si,completeOriginalSourcePatchFaces=sp['completeOriginalPatchFaces'],qualifiedOriginalHostBody=host['originalBody'],originalHostSurfacePatch=hi,completeOriginalHostPatchFaces=hostids,completeSourcePlane=sp['exactOriginalPlane'],completeOriginalHostPlane=hp['exactOriginalPlane'],originalPlanesExactlyParallel=True,allSourceFacetsCompleteFiniteFootprintProofs=footproofs,completeWholeSourcePatchFootprintCovered=all(r['completeFiniteBackingFootprintProof']['wholeFiniteBackingFootprintCovered']for r in footproofs),existingPointOnePlaneBandProofVerbatim=band,exactSourceToHostPlaneDistanceSquaredM2=str(squared),projectionOnlyNotWorldMount=True,sourceVisualAssociationAccepted=False));pulse()
       if not nearby_bounds(sourcefaces,hostfaces):continue
       planeproof=fixed_plane_band(sourcefaces,hp['exactOriginalPlane'])
       for sg,sourcegroup in enumerate(sp['completePatchBoundaryInventory']['completeIncidenceOneBoundaryGroups']):
        if not sourcegroup['closedConnectedDegreeTwoLoop']:continue
        for hg,hostgroup in enumerate(hp['completePatchBoundaryInventory']['completeIncidenceOneBoundaryGroups']):
         if not hostgroup['closedConnectedDegreeTwoLoop']:continue
         se=np.asarray(sourcegroup['completeActualEdges'],float);he=np.asarray(hostgroup['completeActualEdges'],float)
         if not nearby_bounds(se,he):continue
         row=dict(originalSourceSurfacePatch=si,completeOriginalSourcePatchFaces=sp['completeOriginalPatchFaces'],originalSourcePatchBoundaryGroup=sg,qualifiedOriginalHostBody=host['originalBody'],originalHostSurfacePatch=hi,completeOriginalHostPatchFaces=hostids,originalHostPatchBoundaryGroup=hg,completeOriginalHostPatchPlane=hp['exactOriginalPlane'],allSourceVerticesFixedPlaneBandProof=planeproof,completeOriginalHostBodyIncidences=hp['completePatchBoundaryOriginalBodyIncidences'])
         try:row.update(validCompleteWorldLoops=True,completeReciprocalWorldPatchBoundaryProof=loops.verify(se,he))
         except AssertionError as failure:row.update(validCompleteWorldLoops=False,invalidLoopDiagnostic=str(failure),completeReciprocalWorldBand=False)
         sheetmatches.append(row)
      if body not in ROOFS or not hp['allPatchFacesExactUpward']:continue
      # Whole roof-footprint coverage by ONE genuine complete original roof
      # sheet needs this inclusive bounds condition. Multi-sheet interpretations
      # are not disproved or credited by failure of this distinct certificate.
      plo=part[:,:,[0,2]].min((0,1));phi=part[:,:,[0,2]].max((0,1));hlo=hostfaces[:,:,[0,2]].min((0,1));hhi=hostfaces[:,:,[0,2]].max((0,1))
      if not(np.all(hlo<=plo)and np.all(hhi>=phi)):continue
      forward=[dict(globalOriginalSourceFace=f,completeProjectionProof=coverage.exact_coverage(w[f],hostfaces))for f in ids];reverse=[dict(globalOriginalHostFace=f,completeProjectionProof=coverage.exact_coverage(w[f],part))for f in hostids];height=[]
      for f in ids:
       xz=w[f][:,[0,2]];hxz=hostfaces[:,:,[0,2]];selected=np.flatnonzero(np.all(hxz.max(1)>=xz.min(0),axis=1)&np.all(hxz.min(1)<=xz.max(0),axis=1))
       if not len(selected):height.append(dict(globalOriginalSourceFace=f,noIntersectingHostPlane=True));continue
       proof=paired.optimized_ordinary_prism(w[f],hostfaces[selected]);gaps=[F(p['exactGapM'])for r in proof['allExactFiniteSourceGroundPieces']for p in r.get('allExactSourcePrismIntersectionVertices',[])];height.append(dict(globalOriginalSourceFace=f,completeOriginalHostFaces=[hostids[int(i)]for i in selected],finiteOriginalHostPlaneHeightProofVerbatim=proof,allExactIntersectionVertexGapsAtOrAboveHostPlane=bool(gaps)and min(gaps)>=0,exactMinimumPairedHeightGapM=str(min(gaps))if gaps else None,exactMaximumPairedHeightGapM=str(max(gaps))if gaps else None,hostIsSourceSurfaceNotActualGround=True))
      roofcandidates.append(dict(qualifiedOriginalHostBody=host['originalBody'],originalHostRoofSurfacePatch=hi,completeOriginalHostPatchFaces=hostids,allWholeSourceToHostProjectionProofs=forward,allWholeHostToSourceProjectionProofs=reverse,completeReciprocalExactFootprintCovered=all(r['completeProjectionProof']['exactProjectionCovered']for r in forward+reverse),allFiniteSourceToHostHeightProofs=height,projectionOnlyNotWorldMount=True,originalRoofSkinRoleAccepted=False));pulse()
    fanrecord=None
    if body in ROOFS:
     fan=intrinsic_backing[body]['completeOriginalIncidentBackingFanFaces'];proofs=[r for r in a['allActualFacetProofs']if r['globalOriginalFace']in fan];assert sorted(r['globalOriginalFace']for r in proofs)==fan
     fanrecord=dict(sourceIntrinsicBackingFan=intrinsic_backing[body],completeActualBackingFanBoundaryInventory=boundary.census(w,fan),allExistingWholeFacetHostBandProofsVerbatim=proofs,completeBackingFanWithinExistingFiniteHostBand=all(r['wholeFacetWithinExistingFiniteHostBand']is True for r in proofs),freeOuterRimNegativesRetained=a['allActualIncidenceOneBoundaryEdgeProofs'])
    nearest=[]
    for si,sp in enumerate(sourcepatches['allSourceDefinedFullEdgeCoplanarPatches']):
     eligible=[r for r in backingplacements if r['originalSourceSurfacePatch']==si and r['completeWholeSourcePatchFootprintCovered']]
     if eligible:
      low=min(F(r['exactSourceToHostPlaneDistanceSquaredM2'])for r in eligible);nearest.append(dict(originalSourceSurfacePatch=si,exactNearestCompleteBackingDistanceSquaredM2=str(low),allEquallyNearestCompleteOriginalBackingPatches=[r for r in eligible if F(r['exactSourceToHostPlaneDistanceSquaredM2'])==low],nearestPlacementNotAnAcceptedMount=True))
    outputs.append(dict(mode=mode,originalBody=body,actorUID=item['actorUID'],completeOriginalFaces=ids,completeSourceDefinedPartPatchInventory=sourcepatches,allCompleteOriginalSheetIdentityCandidates=sheetmatches,allExactParallelFiniteBackingPlacementCandidates=backingplacements,nearestCompleteOriginalBackingFootprintPlacements=nearest,allCompleteOriginalRoofFootprintCandidates=roofcandidates,sourceDefinedMinimumYBackingFan=fanrecord,priorWholeFacetAndBoundaryNegativesVerbatim=a,sourceVisualRoleAccepted=False,structuralRootOrBridgeCredit=False));pulse();print(dict(mode=mode,body=body,sheetCandidates=len(sheetmatches),backingPlacementCandidates=len(backingplacements),completeBackingPatchPlacements=len(nearest),roofCandidates=len(roofcandidates),backingFanPositive=None if fanrecord is None else fanrecord['completeBackingFanWithinExistingFiniteHostBand']),flush=True)
  pulse(True);assert len(outputs)==60 and all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=['landsd/204145:0','landsd/204143:0'],allSourceDefinedQualifiedHostPatchInventories=inventories,all15FourStreamIntrinsicCorrespondences=outputs,completeParts=15,completeFourStreamRows=60,completeQualifiedNonvisualHostBodies=866,sourceOnly=True,noFreshCurrentCapture=True,sourceGeometryChanges=0,originalHoleOrRoofFunctionCertified=False,projectionOnlyProvidesNoWorldMount=True,visualRoleAccepted=False,currentAcceptance=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,newlyInstalled=0,evidenceRefs=refs);DOC.mkdir(parents=True);save(DOC/'diagnostic.json.gz',output);freezer=load('elements15_intrinsic_sheet_freeze',HERE/HELPERS[-1]);freezer.freeze(BATCH,'elements15-source-defined-original-sheet-backing-roof-footprint-height-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=output['uids'],completeHeldParts=15,completeFourStreamRows=60,sourceOnly=True,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
