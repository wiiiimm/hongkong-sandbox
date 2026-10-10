"""Complete unchanged source interfaces for nine estate originals; no support credit."""
from pathlib import Path
import importlib.util
import numpy as np
from run import ROOT, HERE, read, save, digest, connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components

BATCH = 'government-xl-man-fuk-nine-original-platform-interfaces-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
RECOVERY = DOC.parent / 'government-xl-man-fuk-nine-overlapping-originals-recovery-20261010'
PLATFORM = DOC.parent / 'government-xl-man-fuk-complete-retained-original-physical-v2-20261010'


def main():
    assert not DOC.exists(), 'Fresh immutable interface diagnosis required'
    receipt = read(RECOVERY / 'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    selected = read(RECOVERY / 'selection.json.gz'); assert not selected['missing'] and len(selected['rows']) == 9
    row = read(PLATFORM / 'selection.json.gz')['rows'][0]
    path = ROOT / row['candidate']['path']; raw = path.read_bytes(); assert digest(raw) == row['sourceSHA256']
    platform = decode_original_world_triangles(raw); assert len(platform) == 10661
    topology = components(platform)
    mapping = {face: ci for ci, c in enumerate(topology['components']) for face in c['faceIndices']}
    assert len(topology['components']) == 93 and len(mapping) == len(platform)
    rows = []
    paths = [Path(__file__), path, RECOVERY / 'result.json', RECOVERY / 'selection.json.gz',
        PLATFORM / 'selection.json.gz', PLATFORM / 'result.json',
        HERE / 'exact_original_component_contacts_20261009.py', HERE / 'source_closed_components.py',
        HERE / 'exact_packed_world_geometry_20261009.py']
    for row in selected['rows']:
        asset = ROOT / row['candidate']['path']; raw = asset.read_bytes(); assert digest(raw) == row['sourceSHA256']
        tri = decode_original_world_triangles(raw); assert len(tri) == row['native']['model']['triangles']
        top = components(tri)
        tower_mapping = {face: ci for ci, c in enumerate(top['components']) for face in c['faceIndices']}
        contacts = exact_component_contacts(platform, range(len(platform)), tri, range(len(tri)))
        assert contacts['allPairsExamined']
        for record in contacts['contacts']:
            record.update(originalPlatformComponent=mapping[record['sourceFaceA']],
                originalRelatedComponent=tower_mapping[record['sourceFaceB']])
        out = dict(uid=row['uid'], name=row['source']['building'].get('name'),
            sourceSHA256=row['sourceSHA256'], completeOriginalWorldSHA256=digest(tri.tobytes()),
            completeOriginalFaces=len(tri), completeOriginalTopology=top,
            completeOriginalPlatformContacts=contacts,
            positiveDimensionalContacts=sum(r['dimension'] > 0 for r in contacts['contacts']),
            zeroDimensionalContacts=sum(r['dimension'] == 0 for r in contacts['contacts']),
            contactOriginalComponentPairs=sorted({(r['originalPlatformComponent'], r['originalRelatedComponent']) for r in contacts['contacts'] if r['dimension'] > 0}),
            geometricInterfaceOnly=True, structuralSupportAccepted=False,
            identityAccepted=False, fullAcceptance=False, installationApproved=False)
        rows.append(out); paths.append(asset)
        save(DOC / 'partial-diagnostic.json.gz', dict(rows=rows, sourceGeometryChanges=0, fullAcceptance=False))
        print({k: out[k] for k in ['uid', 'name', 'completeOriginalFaces', 'positiveDimensionalContacts', 'zeroDimensionalContacts', 'contactOriginalComponentPairs']}, flush=True)
    save(DOC / 'diagnostic.json.gz', dict(rows=rows, completeOriginalPlatformFaces=len(platform),
        completeOriginalPlatformWorldSHA256=digest(platform.tobytes()),
        completeOriginalPlatformTopology=topology,
        sourceGeometryChanges=0, fullAcceptance=False, installationApproved=False,
        qualification='Every original indexed source component and all exact rational point/line/area contacts remain separate. Geometric contact alone supplies no ownership or structural-root credit; original source roles and complete terrain/native/basic/runtime/browser gates remain mandatory.'))
    spec = importlib.util.spec_from_file_location('man_fuk_nine_interfaces_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freeze = importlib.util.module_from_spec(spec); spec.loader.exec_module(freeze)
    freeze.freeze(BATCH, 'nine-complete-original-platform-interface-diagnoses-v1', paths,
        dict(uids=['landsd/266062:0'] + [r['uid'] for r in rows],
            positiveInterfaceUids=[r['uid'] for r in rows if r['positiveDimensionalContacts']],
            sourceGeometryChanges=0, structuralSupportAccepted=False,
            nextStep='Prove exact original body/platform support paths and independent source identities; then full current assembly physics and publication gates.'))


if __name__ == '__main__': main()
