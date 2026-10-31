"""Distinct complete lateral-patch hypothesis, never failed-backloop credit.

Patch membership is independently derived from all original frame topology,
before consulting any host proof. Every whole patch and boundary must stay in
the existing .1m band across each arithmetic mode. All39 other bodies receive
an explicit conditional evidence/held disposition, not an architectural role.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_four_side_frame_patch_census_diagnostic_v1_20261011 import verify as patch_census
from exact_original_facet_residual_finite_host_edge_band_diagnostic_v2_20261011 import verify as residual_verify
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify as edge_verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements31-complete-lateral-patches-and39-disposition-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1'
ASSOC=BASE/'xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1'
MOUNTS=BASE/'xl-terrain-recovery-20261011-elements132-complete-unit-mount-patches-v1'
FINITE=BASE/'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1'
ATTR=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
UIDS=['landsd/204145:0','landsd/204143:0'];COUNTS=[12129,11680]
MODES=[('providerOriginal',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [GRAPH,ASSOC,MOUNTS,FINITE,ATTR]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,name):
  p=folder/name;assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 graph=bound(GRAPH,'diagnostic.json.gz');assoc=bound(ASSOC,'diagnostic.json.gz');mounts=bound(MOUNTS,'diagnostic.json.gz');finite=bound(FINITE,'diagnostic.json.gz');attrs=bound(ATTR,'actual-render-attributes.json.gz')['rows']
 assert [a['uid']for a in attrs]==UIDS and len(finite['rows'])==8 and all(not r['unprovedStrictExposureFaces']for r in finite['rows'])
 originals=[]
 for s,a,n in zip(graph['binding']['completeSourceInputs'][:2],attrs,COUNTS):
  p=ROOT/s['asset']['path'];assert ref(p)==s['asset']and digest(p.read_bytes())==s['sourceSHA256']==a['sourceSHA256'];refs.append(ref(p));t=decode_original_world_triangles(p.read_bytes());assert len(t)==n;originals.append(t)
 original=np.concatenate(originals)
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_four_side_frame_patch_census_diagnostic_v1_20261011.py','test_exact_original_four_side_frame_patch_census_diagnostic_v1_20261011.py','test_exact_original_four_side_frame_patch_census_diagnostic_v2_20261011.py','exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py','exact_original_facet_residual_finite_host_edge_band_diagnostic_v1_20261011.py','test_exact_original_facet_residual_finite_host_edge_band_diagnostic_v1_20261011.py','exact_original_facet_residual_finite_host_edge_band_diagnostic_v2_20261011.py','test_exact_original_facet_residual_finite_host_edge_band_diagnostic_v2_20261011.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('elements31-lateral-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[];source_partition={}
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for mode,field in MODES:
   parts=originals if field is None else [np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)]for a in attrs]
   world=np.concatenate(parts);ar=next(r for r in assoc['rows']if r['mode']==mode);mr=next(r for r in mounts['rows']if r['mode']==mode);assert digest(world.tobytes())==ar['completeWorldSHA256']==mr['completeWorldSHA256'];bybody={r['originalBody']:r for r in ar['all132OriginalBodyAssociations']}
   for uid,t in zip(UIDS,parts):assert digest(t.tobytes())==next(r for r in finite['rows']if r['uid']==uid and r['mode']==mode)['completeWorldSHA256']
   units=[]
   for unit in mr['all31OriginalThreeBodyUnits']:
    body=unit['completeOriginalBodies'][1];ids=graph['components'][body]['globalOriginalFaces'];partition=patch_census(world,ids);patch_records=[]
    if partition['verifiedCompleteFourSidePatchPartition']:
     current_partition=[p['completeOriginalPatchFacetIds']for p in partition['allFourCompleteOriginalSidePatches']]
     if mode=='providerOriginal':source_partition[body]=current_partition
     same=current_partition==source_partition.get(body)
     host_ids=bybody[body]['completeHostSelection']['selectedGlobalHostFaces'];hosts=world[host_ids];facet_prior={f['globalOriginalFace']:f for f in bybody[body]['allActualFacetProofs']}
     for patch in partition['allFourCompleteOriginalSidePatches']:
      fs=[];es=[]
      for f in patch['completeOriginalPatchFacetIds']:
       prior=facet_prior[f];extra=None
       if not prior['wholeFacetWithinExistingFiniteHostBand']:extra=residual_verify(world[f],hosts)
       passed=prior['wholeFacetWithinExistingFiniteHostBand']or(extra is not None and extra['wholeFacetWithinExistingFiniteHostBand'])
       fs.append(dict(globalOriginalFace=f,priorPartialFacetProofVerbatim=prior,distinctResidualFiniteProofVerbatim=extra,wholeFacetWithinExistingFiniteHostBand=passed));pulse()
      for e in patch['completePatchBoundaryEdges']:
       if len(hosts):p=edge_verify(e,hosts);passed=p['verifiedCompleteOriginalEdgeFiniteFacadeBand']
       else:p=dict(noSelectedFiniteHost=True,verifiedCompleteOriginalEdgeFiniteFacadeBand=False);passed=False
       es.append(dict(completeActualSourceEdge=e,actualSubsetWholeEdgeHostProofVerbatim=p,completeEdgeWithinExistingFiniteHostBand=passed));pulse()
      patch_records.append(dict(completeSourcePatchVerbatim=patch,completeSameActorQualifiedHostSelection=bybody[body]['completeHostSelection'],allFourActualFacetProofs=fs,allActualPatchBoundaryProofs=es,completePatchWithinExistingFiniteBand=all(f['wholeFacetWithinExistingFiniteHostBand']for f in fs)and all(e['completeEdgeWithinExistingFiniteHostBand']for e in es)))
     pairs=[pair for pair in partition['completeOppositePatchPairs']if all(patch_records[i]['completePatchWithinExistingFiniteBand']for i in pair)]
    else:same=False;pairs=[]
    contacts=all(c['actualPositiveDimensionalContact']and c['allChosenEndpointFacetsStrictlyExposedByCompleteFiniteProof']for c in unit['bothBodyInterfaceProofs'])
    units.append(dict(completeOriginalBodies=unit['completeOriginalBodies'],complete22OriginalUnitFaceIds=unit['completeOriginalFaceIds'],completeIndependentActualPatchPartition=partition,actualPatchMembershipMatchesCompleteSource=same,allCompleteLateralPatchProofs=patch_records,completeOppositePatchBandCandidates=pairs,allInternalActualInterfacesStrictPositive=contacts,conditionalLateralMountCandidate=same and contacts and bool(pairs),failedBackloopAndFreeInteriorFindingsVerbatim=unit,authoredVisualRoleAccepted=False,structuralRootOrBridgeCredit=False));pulse()
   rows.append(dict(mode=mode,completeWorldSHA256=digest(world.tobytes()),all31CompleteUnitLateralDiagnoses=units,all39IndependentMountFindingsVerbatim=mr['all39IndependentOriginalBodies']));pulse(True)
   print(dict(mode=mode,completeLateralCandidates=sum(u['conditionalLateralMountCandidate']for u in units),units=31),flush=True)
  # No conditional geometry evidence is converted into an authored role here.
  dispositions=[]
  independent={r['originalBody']:r for r in mounts['rows'][0]['all39IndependentOriginalBodies']}
  for body in sorted(independent):
   allm=[next(b for b in r['all39IndependentOriginalBodies']if b['originalBody']==body)for r in mounts['rows']]
   whole=all(b['priorFullFacetAndBoundaryFailuresVerbatim']['allFacetsWithinFixedBand']for b in allm);boundary=all(b['priorFullFacetAndBoundaryFailuresVerbatim']['allBoundaryEdgesWithinFixedBand']for b in allm)
   patches=set.intersection(*[{tuple(p['completeOriginalPatchFacetIds'])for p in b['allAssociatedOriginalFacetPatches']if p['completePatchBoundaryWithinBand']}for b in allm])
   category='conditional-complete-source-backed-surface-association'if whole else 'complete-perimeter-interior-and-authentic-host-opening-unresolved'if boundary else 'partial-original-patches-whole-authored-mount-unresolved'if patches else 'no-complete-current-four-stream-original-mount-certificate'
   dispositions.append(dict(originalBody=body,completeOriginalFaceIds=independent[body]['completeOriginalFaceIds'],boundedSourceOnlyDisposition=category,allFourStreamWholeFacetBandPositive=whole,allFourStreamWholeBoundaryBandPositive=boundary,identicalCompleteOriginalAssociatedPatchesAcrossAllFourModes=[list(p)for p in sorted(patches)],originalSourceRoleInterpretationStillRequired=True,qualifiedStructuralHostPathRequired=True,allActualFreeEdgesAndInteriorNegativesRetained=True,notSourceCorruptionOrPermanentImpossibility=True,authoredVisualRoleAccepted=False,structuralRootOrBridgeCredit=False))
  # Source-only exports retain the full22-face unit and show literal original
  # candidate host facets. Hosts are cropped visual context, not a new proof.
  source=rows[0];fig=plt.figure(figsize=(18,10),dpi=100);exports=[]
  for k,body in enumerate([393,444,483]):
   u=next(r for r in source['all31CompleteUnitLateralDiagnoses']if r['completeOriginalBodies'][1]==body);ids=u['complete22OriginalUnitFaceIds'];t=original[ids];lo=t.min((0,1));hi=t.max((0,1));margin=np.maximum((hi-lo)*.2,.15);a=next(r for r in assoc['rows']if r['mode']=='providerOriginal');b=next(r for r in a['all132OriginalBodyAssociations']if r['originalBody']==body);hostids=b['completeHostSelection']['selectedGlobalHostFaces'];ax=fig.add_subplot(1,3,k+1,projection='3d')
   if hostids:ax.add_collection3d(Poly3DCollection(original[hostids][:,:,[0,2,1]],facecolors='#b6c2ce',edgecolors='#6f7c89',linewidths=.2,alpha=.25))
   ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors='#e8a77e',edgecolors='#9b4d30',linewidths=.3,alpha=.35))
   pids=[f for p in u['allCompleteLateralPatchProofs']if p['completePatchWithinExistingFiniteBand']for f in p['completeSourcePatchVerbatim']['completeOriginalPatchFacetIds']]
   if pids:ax.add_collection3d(Poly3DCollection(original[pids][:,:,[0,2,1]],facecolors='#286aa6',edgecolors='#143857',linewidths=.5,alpha=.9))
   ax.set_xlim(lo[0]-margin[0],hi[0]+margin[0]);ax.set_ylim(lo[2]-margin[2],hi[2]+margin[2]);ax.set_zlim(lo[1]-margin[1],hi[1]+margin[1]);ax.set_box_aspect(np.maximum(hi-lo+2*margin,.01)[[0,2,1]]);ax.view_init(elev=20,azim=-45);ax.set_axis_off();ax.set_title(str(u['completeOriginalBodies'])+' / full original22 faces',fontsize=10);exports.append(dict(originalBodies=u['completeOriginalBodies'],complete22HighlightedSourceFaces=ids,blueSourcePatchFaces=pids,croppedQualifiedSourceHostFaces=hostids,visualContextNotNewPhysicalProof=True))
  fig.suptitle('Original complete units: blue full-band side patches / amber free geometry / grey cropped host / no role or support credit',fontsize=11);fig.tight_layout();DOC.mkdir(parents=True);fig.savefig(DOC/'original-frame-lateral-patches-and-jamb-context-1800x1000.png');plt.close(fig)
  assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=UIDS,rows=rows,complete39SourceOnlyDispositions=dispositions,sourceOriginalExports=exports,all132OriginalBodiesAnd3172FacesPreserved=True,failedCompleteBackloopHypothesisNotReinterpreted=True,strictBandM=.1,sourceOnly=True,noFreshCurrentReacceptance=True,authoredVisualRoleAccepted=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);pulse(True)
  spec=importlib.util.spec_from_file_location('elements_lateral_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'elements31-complete-lateral-source-patches-and39-explicit-four-stream-disposition-diagnostic-v1',[ROOT/r['path']for r in refs]+list(DOC.iterdir()),dict(uids=UIDS,sourceOnly=True,completeRemainingBodies=132,all39DispositionsPreserved=True,lateralCandidates={r['mode']:[u['completeOriginalBodies']for u in r['all31CompleteUnitLateralDiagnoses']if u['conditionalLateralMountCandidate']]for r in rows},currentAcceptance=False,authoredVisualRoleAccepted=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
