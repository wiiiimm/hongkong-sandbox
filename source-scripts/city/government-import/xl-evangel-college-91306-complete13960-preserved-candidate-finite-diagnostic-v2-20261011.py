"""Check all13960 unchanged source facets against actual drawn candidate ground.

All13960/four streams and finite projection remain complete.
Captured source worlds are reused only under exact entry/source/module bindings
and literal runtime parity. All raw negatives remain; no typed acceptance.
"""
import importlib.util, json, sys, uuid, subprocess
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from evangel_college_original_wing_extension_identity_20261011 import UID, SOURCE_SHA
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import source_proposal_pin_path
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE = ROOT / 'docs/astra-city/government-import'
INPUT = BASE / 'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011'
PHYSICAL = BASE / 'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'
CURRENT_INPUT = BASE / 'government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011'
BATCH = 'government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011'
DOC = BASE / BATCH; LOCAL = HERE / 'local' / BATCH; LEASE = LOCAL / 'reservation.json'
def owned():
    lease = read(LEASE); assert reservations.owns(lease) and not DOC.exists()
    refs = [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [INPUT, PHYSICAL]:
            r = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (r['jobId'],)).fetchone() == ('complete', r)
            refs.append(folder / 'result.json')
            for pin in r['evidenceRefs']:
                p = source_proposal_pin_path(pin) if folder == INPUT else ROOT / pin['path']; assert digest(p.read_bytes()) == pin['sha256']; refs.append(p)
    capture = read(INPUT / 'complete-current-actual-source-and-ground.json.gz')
    data = read(INPUT / 'complete-four-stream-ground-inputs.json.gz')
    assert data['uid'] == UID and data['sourceSHA256'] == SOURCE_SHA
    physical=read(PHYSICAL/'diagnostic.json.gz');assert physical['all17CurrentActorGuardsRetained']and physical['changedTerrainProposal']and not physical['currentAcceptance']
    runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path);assert len(runtime['rows'])==1
    actual=runtime['rows'][0];assert actual['uid']==UID and actual['sourceSHA256']==SOURCE_SHA
    literal=np.asarray(actual['position'],dtype='<f8').reshape(-1,3)[np.asarray(actual['index']).reshape(-1,3)]
    saved_literal=np.asarray(data['completeWorldStreams']['actualLiteral']['completeWorldTriangles'],dtype='<f8')
    assert np.array_equal(literal,saved_literal) and digest(literal.tobytes())==data['completeWorldStreams']['actualLiteral']['completeWorldTriangleSHA256']
    candidate_row=read(PHYSICAL/'selection.json.gz')['rows'][0];assert candidate_row['candidate']['entry']==capture['entry']
    captured_own_forms=[f for f in capture['completeCurrentForms']if f['uid']==UID];assert len(captured_own_forms)==1 and candidate_row['source']['building']==captured_own_forms[0]
    source_tile_path='3d-viewer/'+candidate_row['source']['tile'];assert capture['inputHashes'][source_tile_path]==runtime['inputHashes'][source_tile_path]==digest((ROOT/source_tile_path).read_bytes())
    current_own_forms=[f for f in read(ROOT/source_tile_path)['buildings']if f['uid']==UID];assert current_own_forms==captured_own_forms
    assert digest((ROOT/candidate_row['candidate']['path']).read_bytes())==SOURCE_SHA
    assert capture['completeRecursiveLoaderModuleClosure']['completeAuditedLiteralImportClosure'] and not capture['completeRecursiveLoaderModuleClosure']['unsupportedDynamicImports']
    for path,sha in capture['completeRecursiveLoaderModuleClosure']['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    # Production acceptance-metrics nominates EVERY actual terrain facet whose
    # closed XZ AABB intersects entry bounds padded by1m, with no slope filter.
    # All four WHOLE unused-position bounds fit strictly inside that universe.
    nomination_bounds=np.asarray(candidate_row['candidate']['entry']['worldBounds'],dtype='<f8');full_bounds=read(CURRENT_INPUT/'proposal-input.json')['completeFourWorldUnusedPOSITIONBounds'];assert len(full_bounds)==4
    for bounds in full_bounds:
        b=np.asarray(bounds,dtype='<f8');assert np.isfinite(b).all()and np.all(b[0,[0,2]]>=nomination_bounds[0,[0,2]]-1)and np.all(b[1,[0,2]]<=nomination_bounds[1,[0,2]]+1)
    grounds=dict(currentDrawn=np.asarray(actual['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3));assert len(grounds['currentDrawn'])>0 and np.isfinite(grounds['currentDrawn']).all()
    ground_hashes={kind:digest(ground.tobytes())for kind,ground in grounds.items()}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==physical['currentManifest']['sha256']==runtime['inputHashes']['3d-viewer/city/data/manifest.json']
    for path,sha in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    save(DOC/'exact-current-source-and-ground-binding.json',dict(uid=UID,sourceSHA256=SOURCE_SHA,currentManifest=physical['currentManifest'],completeCurrentRuntimeLiteralSHA256=digest(literal.tobytes()),originalCapturedSourceEntryExactlyEqualsCurrentCandidateEntry=True,completeCurrentSourceFormExactlyEqualsCapturedForm=True,currentSourceTileSHA256=runtime['inputHashes'][source_tile_path],completeUnchangedProductionLoaderModuleHashes=capture['completeRecursiveLoaderModuleClosure']['inputHashes'],completeFourWorldUnusedPOSITIONBounds=full_bounds,productionClosedAABBNominationMarginM=1,completeActualCandidateGroundSHA256=ground_hashes['currentDrawn'],completeActualCandidateGroundFacets=len(grounds['currentDrawn']),noSlopeOrHeightFilter=True,changedTerrainProposalIsNotInstalled=True,currentAcceptance=False))
    refs.extend([runtime_path,CURRENT_INPUT/'proposal-input.json',PHYSICAL/'selection.json.gz',HERE/'acceptance-metrics.mjs'])
    rows = []; cache = {}
    for mode, stream in data['completeWorldStreams'].items():
        world = np.asarray(stream['completeWorldTriangles'], dtype='<f8')
        assert world.shape == (13960, 3, 3) and digest(world.tobytes()) == stream['completeWorldTriangleSHA256']
        faces = []
        for face_id in range(13960):
            comparisons = {}
            for kind, ground in grounds.items():
                key = (digest(world[face_id].tobytes()), ground_hashes[kind])
                if key not in cache:
                    a = coarse(world[face_id], ground)
                    b = None if a['existingOrdinaryClearanceBoundProved'] else paired(world[face_id], ground)
                    cache[key] = dict(coarse=a, paired=b, completeFiniteOrdinaryBoundProved=a['existingOrdinaryClearanceBoundProved'] or bool(b and b['existingOrdinaryClearanceBoundProved']))
                comparisons[kind] = cache[key]
            face=world[face_id];normal=np.cross(face[1]-face[0],face[2]-face[0]);length=np.linalg.norm(normal)
            ratio=float(normal[1]/length)if length else None
            orientation='collapsed'if ratio is None else 'steep-wall'if abs(ratio)<=.25 else 'upward'if ratio>0 else 'downward'
            faces.append(dict(sourceFace=face_id,orientationDiagnostic=orientation,wholeOriginalYRangeHKPD=[float(face[:,1].min()),float(face[:,1].max())],groundComparisons=comparisons))
            if face_id%1000==0:print(json.dumps(dict(arithmetic=mode,completedSourceFaces=face_id)),flush=True)
        rows.append(dict(arithmetic=mode, completeWholeWorldSHA256=stream['completeWorldTriangleSHA256'], complete13960FaceComparisons=faces,
                         failedFacesByGround={kind: [f['sourceFace'] for f in faces if not f['groundComparisons'][kind]['completeFiniteOrdinaryBoundProved']] for kind in grounds},
                         currentRawFailuresRetained=True, currentGroundRootAccepted=False))
        print(json.dumps(dict(arithmetic=mode, failures=rows[-1]['failedFacesByGround'])), flush=True)
    save(DOC / 'diagnostic.json.gz', dict(uids=[UID], sourceSHA256=SOURCE_SHA, rows=rows,
         completeGrounds={kind: dict(completeFaces=len(g), completeWorldSHA256=digest(g.tobytes()), wholeGroundYRangeHKPD=[float(g[:,:,1].min()),float(g[:,:,1].max())]) for kind,g in grounds.items()},
         terrainReplacementProposed=True,terrainProposalIsNotInstalled=True,
         noBelowGradeFoundationExposureAssumption=True, geometryChanges=0, currentAcceptance=False, physicalAccepted=False, installationApproved=False))
    assert reservations.owns(lease) and manifest.read_bytes() == before
    for path,sha in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    for path,sha in capture['inputHashes'].items():assert digest(source_proposal_pin_path(dict(path=path,sha256=sha)).read_bytes())==sha
    refs += [HERE / n for n in ['evangel_college_original_wing_extension_identity_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_projection_coverage_v2_20261010.py']]
    s=importlib.util.spec_from_file_location('evangel_whole_finite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    r=m.freeze(BATCH,'complete13960-four-stream-actual-preserved-candidate-finite-diagnostic-no-role-or-installation-credit',refs+[DOC/'diagnostic.json.gz',DOC/'exact-current-source-and-ground-binding.json'],dict(uids=[UID],completeWholeSourceFaces=13960,currentAcceptance=False,newlyInstalled=0))
    print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
    if '--owned' in sys.argv: return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim=reservations.claim('evangel-whole-source-current-finite-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok']
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
