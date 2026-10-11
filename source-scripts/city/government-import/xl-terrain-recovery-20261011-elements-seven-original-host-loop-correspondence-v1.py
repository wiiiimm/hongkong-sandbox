"""Complete original qualified-host loop correspondence for seven held parts.

This is a SOURCE-ONLY changed-evidence investigation. Genuine incidence-one
host loops are enumerated independently in every arithmetic stream and source
body, including all open/branched negatives. Reciprocal world-space band uses
the existing exact .1m kernel. XZ roof-plan association is explicitly a separate
projection-only lead: it never supplies a world mount, aperture, visual role,
ground root, bridge, source correction or current acceptance.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements-seven-original-host-loop-correspondence-v1';DOC=BASE/BATCH
INPUTS=(
 'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1',
 'xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1',
 'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1',
 'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1',
 'xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1',
 'xl-terrain-recovery-20261011-elements132-remaining-original-bodies-context-v1',
 'xl-terrain-recovery-20261011-elements24-named-original-visual-proposals-v1')
HELPERS=(
 'exact_original_body_boundary_group_census_v1_20261011.py',
 'test_exact_original_body_boundary_group_census_v1_20261011.py',
 'exact_original_shared_edge_component_census_v2_20261011.py',
 'exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',
 'test_exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',
 'test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'exact_packed_world_geometry_20261009.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py')
MODES=('providerOriginal','actualLiteral','explicitLeftFloat32','explicitBalancedFloat32')
OPENING_PARTS=(70,890,904,918);ROOF_PARTS=(839,893,902);PARTS=OPENING_PARTS+ROOF_PARTS
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def exact_upward(triangle):
 a,b,c=[tuple(F(float(x))for x in v)for v in triangle];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)]
 return u[2]*v[0]-u[0]*v[2]>0
def nearby_bounds(a,b):
 # Necessary only: exact reciprocal .1 certificates are evaluated afterward.
 return bool((np.abs(a.min((0,1))-b.min((0,1)))<=np.nextafter(.1,np.inf)).all()and(np.abs(a.max((0,1))-b.max((0,1)))<=np.nextafter(.1,np.inf)).all())
def plan(edges):
 raw=np.asarray(edges,float).copy();raw[:,:,1]=0.;return raw
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]+[ref(HERE/n)for n in HELPERS]
 for batch in INPUTS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
  for binding in r['evidenceRefs']:
   p=ROOT/binding['path'];assert p.is_file()and ref(p)==binding;refs.append(binding)
 refs=list({(r['path'],r['sha256']):r for r in refs}.values())
 # Pin all producing and source files before importing any new method/fixture.
 assert all(ref(ROOT/r['path'])==r for r in refs)
 boundary=load('elements_complete_host_loop_census',HERE/HELPERS[0]);loops=load('elements_exact_reciprocal_host_loop',HERE/HELPERS[3]);fixture=load('elements_seven_complete_source_fixture',HERE/HELPERS[5]);docs,packages=fixture.actual_fixture();worlds=next(iter(packages.values()))['worlds'];graph=docs['graph']
 paths=read(BASE/INPUTS[4]/'diagnostic.json.gz');qualified={}
 for mode in MODES:
  row=next(r for r in paths['rows']if r['mode']==mode);qualified[mode]=set(row['qualifiedDiagnosticOwnedBodies']);assert len(qualified[mode])==866 and row['noWholeNativeBodySeed']is True and all(i<998 for i in qualified[mode]);assert not qualified[mode].intersection(PARTS)
  bandrow=next(r for r in docs['bands']['rows']if r['mode']==mode);assert set(bandrow['qualifiedHostOriginalBodies'])==qualified[mode]and bandrow['boundedHostPathReceipt']==ref(BASE/INPUTS[4]/'result.json')
  for uid,offset,count in [('landsd/204145:0',0,12129),('landsd/204143:0',12129,11680)]:
   finite=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid);assert digest(worlds[mode][offset:offset+count].tobytes())==finite['completeWorldSHA256']and len(finite['allFaces'])==count
   assert all(f['strictlyExposedWholeFacet']is True and f['existingOrdinaryClearanceBoundProved']is True and f['closedProjectionCovered']is True for f in finite['allFaces'])
 claim=reservations.claim('elements-seven-original-loop-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  hostinventories={};sourceinventories={};results=[]
  for mode in MODES:
   w=worlds[mode];hostinventories[mode]=[];sourceinventories[mode]={}
   for body in sorted(qualified[mode]):
    item=graph['components'][body];ids=sorted(item['globalOriginalFaces']);inventory=boundary.census(w,ids)
    hostinventories[mode].append(dict(originalBody=body,actorUID=item['actorUID'],completeBodyBoundaryInventory=inventory));pulse()
   for body in PARTS:
    item=graph['components'][body];sourceinventories[mode][str(body)]=boundary.census(w,sorted(item['globalOriginalFaces']))
   for body in PARTS:
    item=graph['components'][body];source=sourceinventories[mode][str(body)];worldcandidates=[];plancandidates=[]
    for sourcegroup,sg in enumerate(source['completeIncidenceOneBoundaryGroups']):
     if not sg['closedConnectedDegreeTwoLoop']:continue
     sourceedges=np.asarray(sg['completeActualEdges'],float)
     for host in hostinventories[mode]:
      if host['actorUID']!=item['actorUID']:continue
      for hostgroup,hg in enumerate(host['completeBodyBoundaryInventory']['completeIncidenceOneBoundaryGroups']):
       if not hg['closedConnectedDegreeTwoLoop']:continue
       hostedges=np.asarray(hg['completeActualEdges'],float);record=dict(originalSourceBoundaryGroup=sourcegroup,qualifiedOriginalHostBody=host['originalBody'],originalHostBoundaryGroup=hostgroup,completeOriginalHostIncidences=hg['completeActualEdgeIncidences'])
       if nearby_bounds(sourceedges,hostedges):
        try:
         proof=loops.verify(sourceedges,hostedges);worldcandidates.append(dict(**record,worldClosedLoopValid=True,completeReciprocalWorldBoundaryProof=proof))
        except AssertionError as failure:
         worldcandidates.append(dict(**record,worldClosedLoopValid=False,invalidLoopDiagnostic=str(failure),completeReciprocalWorldBoundaryBandProved=False))
       if body in ROOF_PARTS:
        sourceplan,hostplan=plan(sourceedges),plan(hostedges)
        if not nearby_bounds(sourceplan,hostplan):continue
        try:loops.loop(sourceplan);loops.loop(hostplan)
        except AssertionError:
         plancandidates.append(dict(**record,projectedClosedLoopValid=False,projectionCollapseOrBranchRetained=True));continue
        proof=loops.verify(sourceplan,hostplan)
        incident=sorted({e['globalOriginalFace']for rows in hg['completeActualEdgeIncidences']for e in rows})
        plancandidates.append(dict(**record,projectedClosedLoopValid=True,completeReciprocalXZProjectionProof=proof,allHostBoundaryIncidentFacetsExactUpward=all(exact_upward(w[f])for f in incident),sourceWorldYRange=[float(w[sorted(item['globalOriginalFaces'])][:,:,1].min()),float(w[sorted(item['globalOriginalFaces'])][:,:,1].max())],hostBoundaryWorldYRange=[float(hostedges[:,:,1].min()),float(hostedges[:,:,1].max())],projectionOnlyNotWorldMount=True,genuineRoofApertureOrWholeSkinProjectionCertified=False))
       pulse()
    prior=next(r for r in next(r for r in docs['bands']['rows']if r['mode']==mode)['all132OriginalBodyAssociations']if r['originalBody']==body)
    results.append(dict(mode=mode,originalBody=body,actorUID=item['actorUID'],completeOriginalFaces=sorted(item['globalOriginalFaces']),completeSourceBoundaryInventory=source,allReciprocalWorldCandidates=worldcandidates,allXZProjectionOnlyCandidates=plancandidates,completeReciprocalWorldMatches=[r for r in worldcandidates if r.get('worldClosedLoopValid')and r['completeReciprocalWorldBoundaryProof']['completeReciprocalBoundaryBandProved']],completeReciprocalXZProjectionOnlyMatches=[r for r in plancandidates if r.get('projectedClosedLoopValid')and r['completeReciprocalXZProjectionProof']['completeReciprocalBoundaryBandProved']],priorWholeFacetAndBoundaryFailuresVerbatim=prior,visualRoleAccepted=False,structuralRootOrBridgeCredit=False));pulse();print(dict(mode=mode,body=body,worldCandidates=len(worldcandidates),worldMatches=len(results[-1]['completeReciprocalWorldMatches']),projectionCandidates=len(plancandidates),projectionMatches=len(results[-1]['completeReciprocalXZProjectionOnlyMatches'])),flush=True)
  pulse(True);assert len(results)==28 and all(ref(ROOT/r['path'])==r for r in refs)
  output=dict(uids=['landsd/204145:0','landsd/204143:0'],fourStreamCompleteOwnedWorldSHA256={m:digest(w.tobytes())for m,w in worlds.items()},allQualifiedHostBoundaryInventories=hostinventories,allSevenFourStreamCorrespondences=results,completeQualifiedNonvisualHostBodies=866,allHostOpenBranchNonmanifoldAndZeroFindingsRetained=True,sourceOnly=True,noFreshCurrentCapture=True,noNativeAvailabilityAsHostSeed=True,originalSimpleHoleOrCavityCertified=False,projectionOnlyRoofLeadsProvideNoWorldMount=True,visualRoleAccepted=False,currentAcceptance=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs)
  DOC.mkdir(parents=True);save(DOC/'diagnostic.json.gz',output);freezer=load('elements_seven_loop_freeze',HERE/HELPERS[-1]);freezer.freeze(BATCH,'elements-seven-complete-qualified-original-host-loops-four-stream-fixed-band-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=output['uids'],completeHeldParts=7,completeFourStreamRows=28,qualifiedNonvisualHosts=866,sourceOnly=True,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
