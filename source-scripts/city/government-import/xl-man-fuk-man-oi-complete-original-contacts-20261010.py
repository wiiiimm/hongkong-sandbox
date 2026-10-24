"""Complete unchanged original Man Fuk/Man Oi surface contacts, research only."""
from pathlib import Path
import json, numpy as np
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components

BATCH = 'government-xl-man-fuk-man-oi-complete-original-contacts-20261010'
DOC = ROOT/'docs/astra-city/government-import'/BATCH
SOURCE = DOC.parent/'government-xl-man-fuk-man-oi-original-recovery-20261010'
CONTEXT = DOC.parent/'government-xl-man-fuk-complete-foreign-context-20261010'

def main():
    assert not DOC.exists(), 'Fresh immutable diagnostic required'
    selected = read(SOURCE/'selection.json.gz')
    assert not selected['missing']
    by_uid = {r['uid']:r for r in selected['rows']}
    uids = ['landsd/266062:0','landsd/75697:0']
    assert set(by_uid) == set(uids)
    paths = [ROOT/by_uid[u]['candidate']['path'] for u in uids]
    for u,p in zip(uids,paths):
        assert digest(p.read_bytes()) == by_uid[u]['sourceSHA256']
    tri = [decode_original_world_triangles(p.read_bytes()) for p in paths]
    assert [len(t) for t in tri] == [10661,2160]
    topology = [components(t) for t in tri]
    contacts = exact_component_contacts(tri[0],range(len(tri[0])),tri[1],range(len(tri[1])))
    assert contacts['allPairsExamined']
    context = read(CONTEXT/'diagnostic.json.gz')
    assert context['sourceSHA256'] == by_uid[uids[0]]['sourceSHA256']
    foreign = next(r for r in context['foreignActors'] if r['uid'] == uids[1])
    maps = [{face:ci for ci,c in enumerate(top['components']) for face in c['faceIndices']} for top in topology]
    for record in contacts['contacts']:
        record['componentA'] = maps[0][record['sourceFaceA']]
        record['componentB'] = maps[1][record['sourceFaceB']]
    refs = {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in
        [Path(__file__),SOURCE/'selection.json.gz',CONTEXT/'diagnostic.json.gz',*paths,
         HERE/'exact_original_component_contacts_20261009.py',HERE/'source_closed_components.py',
         HERE/'exact_packed_world_geometry_20261009.py']}
    save(DOC/'diagnostic.json.gz',dict(uids=uids, sourceSHA256s={u:by_uid[u]['sourceSHA256'] for u in uids},
        completeOriginalFaceCounts=[len(t) for t in tri], completeOriginalComponentCounts=[len(t['components']) for t in topology],
        completeOriginalWorldSHA256s=[digest(t.astype('<f8').tobytes()) for t in tri],
        completeOriginalTopologies=topology, completeOriginalContacts=contacts,
        all23ForeignOverlapOriginalFaceIds=foreign['allPositiveAreaOriginalFaceIds'],
        inputHashes=refs, identityAccepted=False, physicalAccepted=False,
        installationApproved=False, sourceGeometryChanges=0, scriptExternalAICalls=0,
        qualification='Exact original rational point, line and area contacts remain separate. Neither contact nor shared estate identity grants ownership or load-bearing credit. All original facets/parts remain; fresh primary and independent physical/runtime/browser checks remain mandatory.'))
    print(json.dumps(dict(uids=uids,components=[len(t['components']) for t in topology],
        contacts=len(contacts['contacts']),positiveDimensionalContacts=sum(r['dimension']>0 for r in contacts['contacts']),
        pairsTested=contacts['trianglePairsTested'],contactComponents=sorted({(r['componentA'],r['componentB']) for r in contacts['contacts']}))),flush=True)

if __name__ == '__main__':
    main()
