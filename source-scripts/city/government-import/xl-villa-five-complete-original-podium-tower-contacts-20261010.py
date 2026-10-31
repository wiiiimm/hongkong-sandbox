"""Complete exact original podium/tower contacts; no support or ownership credit."""
import importlib.util
import json
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_mesh_components import face_components
from xl_source_stream_binding_20261009 import source_stream_binding

BATCH = 'government-xl-villa-five-complete-original-podium-tower-contacts-20261010'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
PODIUM = BASE / 'government-xl-villa-current-bound-courtyard-edge-inputs-v1-20261010'
TOWERS = BASE / 'government-xl-villa-premiere-four-tower-original-recovery-20261010'
PRIMARY = BASE / 'government-xl-villa-premiere-five-original-primary-relationships-20261010'
UID = 'landsd/89917:0'

def main():
    assert not DOC.exists()
    own = read(PODIUM / 'selection.json.gz')['rows'][0]
    rows = [own] + read(TOWERS / 'selection.json.gz')['rows']
    assert len(rows) == 5 and len({r['uid'] for r in rows}) == 5 and own['uid'] == UID
    originals = {}; actors = []; assets = []
    for row in rows:
        path = ROOT / row['candidate']['path']; raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256']
        tri = decode_original_world_triangles(raw)
        assert len(tri) == row['triangles'] and np.isfinite(tri).all()
        originals[row['uid']] = tri; assets.append(path)
        actors.append(dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'],
            completeOriginalFaces=len(tri), completeOriginalWorldSHA256=digest(tri.tobytes()),
            completeOriginalProviderStreams=source_stream_binding(raw),
            completeOriginalParts=[list(map(int, p)) for p in face_components(tri)],
            bounds=[tri.min((0, 1)).tolist(), tri.max((0, 1)).tolist()]))
    contacts = []
    for row in rows[1:]:
        target = originals[row['uid']]
        proof = exact_component_contacts(originals[UID], range(len(originals[UID])), target, range(len(target)))
        assert proof['allPairsExamined']
        contacts.append(dict(podiumUID=UID, towerUID=row['uid'], completeFiniteContacts=proof))
        print(json.dumps(dict(uid=row['uid'], positiveInterfaces=sum(c['dimension'] > 0 for c in proof['contacts']),
            exactPairsTested=proof['trianglePairsTested'])), flush=True)
    out = dict(uids=[r['uid'] for r in rows], actors=actors, completePodiumTowerContacts=contacts,
        completeOriginalFaces=sum(len(t) for t in originals.values()), sourceGeometryChanges=0,
        identityAccepted=False, physicalSupportAccepted=False, installationApproved=False,
        qualification='Every original podium/tower face and exact finite interface retained. Direct provider OP records remain separate evidence. Contacts imply authored association only, never a rooted body, load bearing, common legal ownership, actor suppression or any foreign/terrain/collision exemption.')
    save(DOC / 'diagnostic.json.gz', out)
    spec = importlib.util.spec_from_file_location('villa_five_contact_fence', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    fence = importlib.util.module_from_spec(spec); spec.loader.exec_module(fence)
    refs = [Path(__file__), PODIUM / 'selection.json.gz', TOWERS / 'selection.json.gz', TOWERS / 'result.json',
        PRIMARY / 'diagnostic.json', PRIMARY / 'result.json', HERE / 'exact_original_component_contacts_20261009.py',
        HERE / 'exact_original_shell_intersections_20261009.py', HERE / 'exact_packed_world_geometry_20261009.py',
        HERE / 'exact_mesh_components.py', HERE / 'xl_source_stream_binding_20261009.py', *assets]
    result = fence.freeze(BATCH, 'complete-five-original-podium-tower-finite-contact-diagnostic-v1', refs, out)
    print(json.dumps(dict(jobId=result['jobId'], completeOriginalFaces=out['completeOriginalFaces'], physicalSupportAccepted=False)), flush=True)

if __name__ == '__main__': main()
