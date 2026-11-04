"""Current-bound identity-only interpretation of one104-face original canopy.

Complete source projection/cell, remaining18638 ordinary extent, all foreign
forms and byte/root/native bindings remain. No precise image registration,
property boundary, contact, ground, structural or runtime exemption follows.
"""
from copy import deepcopy
import importlib.util
import json
import numpy as np
from run import ROOT, HERE, read, digest, connect, NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from king_cheung_complete_ancillary_proposal_20261011 import proposal, UID, CSUID, MODEL, SOURCE_SHA, RAW_REASONS
BASE = ROOT / 'docs/astra-city/government-import'
RAW = BASE / 'government-xl-king-cheung-95691-current-original-identity-v1-20261011'
PRIMARY = BASE / 'government-xl-king-cheung-95691-primary-relations-v1-20261011'
SOURCE = BASE / 'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011'
LOW = BASE / 'government-xl-king-cheung-95691-complete-low-parts-contacts-v1-20261011'
PROPOSAL = BASE / 'government-xl-king-cheung-95691-complete-ancillary-proposal-v1-20261011'
POLICY = 'king-cheung-exact104-original-ancillary-canopy-identity-only-v1'
PRIMARY_PARAMETERS = {'f': 'json', 'where': "BuildingCSUID IN ('3080039468T20140728')", 'outFields': '*',
                      'returnGeometry': 'true', 'outSR': '2326', 'orderByFields': 'OBJECTID', 'resultRecordCount': '1000'}

def current_binding(captured_row, captured_context, row, context, loaded_forms, captured_forms, manifest_bytes, captured_manifest_bytes, native_results, installed_uids):
    assert row == captured_row and context == captured_context
    assert row['uid'] == context['uid'] == UID and row['modelId'] == MODEL and row['sourceSHA256'] == SOURCE_SHA
    assert manifest_bytes == captured_manifest_bytes
    assert len({f['uid'] for f in loaded_forms}) == len(loaded_forms)
    assert {f['uid']: f for f in loaded_forms} == {f['uid']: f for f in captured_forms}
    assert len({f['uid'] for f in captured_forms}) == len(captured_forms)
    assert native_results == [(row['native']['resultSha'],)]
    assert UID not in installed_uids
    return True

def named_identity(previous, row, triangles, forms, provider, topology, low_contacts, frozen_proposal):
    recomputed = proposal(previous, row, triangles, forms, provider, topology, low_contacts)
    frozen = deepcopy(frozen_proposal)
    primary_refs = frozen.pop('architecturalInterpretationPrimaryRefs')
    assert len(primary_refs) == 4 and all(set(r) == {'path', 'sha256'} and len(r['sha256']) == 64 for r in primary_refs)
    assert frozen == recomputed
    assert recomputed['proposalSpatialGuardsSatisfied']
    assert previous['reasons'] == RAW_REASONS
    out = deepcopy(previous)
    out.update(policy=POLICY, passed=True, reasons=[], rawAncillaryExtentReasonsRetained=previous['reasons'],
               rawOriginalIdentityRetained=deepcopy(previous), completeAncillaryInterpretation=recomputed,
               architecturalPrimaryRefs=primary_refs, allOtherCurrentFormsRetained=forms,
               proof={k: True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']},
               sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
               physicalAccepted=False, structuralSupportAccepted=False, physicalSupportExemption=False,
               runtimeExemption=False, currentActorRemoval=False, installationApproved=False, modelGeometryChanges=0,
               qualification='Identity only for unchanged King Cheung source. The complete104 original faces are a freestanding estate entrance canopy/post role corroborated by the unique HA estate record/photo. No precise plan registration, property ownership or grounding claim. Full source coverage/cell/foreign checks and18638 ordinary-extent faces retained; isolated post43 and absence of canopy/main-body contact remain. All39/43/44 complete ground/support and full original runtime/foreign physical gates remain independent.')
    return out

def verify_files(row, context, local):
    receipt = read(PROPOSAL / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
        native = c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchall()
    for pin in receipt['evidenceRefs']: assert digest((ROOT / pin['path']).read_bytes()) == pin['sha256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes(); parsed = json.loads(before)
    catalogue_refs = [(ROOT / '3d-viewer' / path, digest((ROOT / '3d-viewer' / path).read_bytes())) for path in parsed['officialModelCatalogues']]
    installed = [entry['uid'] for path, _ in catalogue_refs for entry in read(path)['models']]
    raw = (ROOT / row['candidate']['path']).read_bytes(); assert digest(raw) == SOURCE_SHA
    triangles = decode_original_world_triangles(raw)
    s = importlib.util.spec_from_file_location('king_current_complete_forms', HERE / 'xl-final-script-pass.py')
    final = importlib.util.module_from_spec(s); s.loader.exec_module(final)
    low, high = triangles.min((0, 1)), triangles.max((0, 1))
    forms = final.load_forms([low[0]-2, low[2]-2, high[0]+2, high[2]+2])
    for _, _, tile in forms: assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == context['neighbourTileHashes'][tile]
    current_binding(read(RAW / 'selection.json.gz')['rows'][0], read(RAW / 'context.json.gz')['rows'][0], row, context,
                    [f for f, _, _ in forms], read(RAW / 'complete-current-forms.json.gz')['rows'],
                    before, (RAW / 'captured-manifest.json').read_bytes(), native, installed)
    request = read(PRIMARY / 'exact-current-one-primary.request.json')
    assert request['url'] == 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
    assert request['parameters'] == PRIMARY_PARAMETERS and request['sha256'] == digest((PRIMARY / 'exact-current-one-primary.json').read_bytes())
    previous = raw_verify(row, context, local / 'raw-whole-cell')
    assert previous == read(RAW / 'identity.json')
    result = named_identity(previous, row, triangles, [f for f, _, _ in forms], read(PRIMARY / 'exact-current-one-primary.json'),
                           read(SOURCE / 'diagnostic.json.gz')['completeTopology'], read(LOW / 'diagnostic.json.gz'), read(PROPOSAL / 'diagnostic.json.gz'))
    assert manifest.read_bytes() == before and digest((ROOT / row['candidate']['path']).read_bytes()) == SOURCE_SHA
    for path, sha in catalogue_refs: assert digest(path.read_bytes()) == sha
    for _, _, tile in forms: assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == context['neighbourTileHashes'][tile]
    return result
