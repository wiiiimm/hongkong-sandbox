"""Compare complete original Woo Sung and Vancor sources without geometry edits."""
from collections import Counter
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_finite_contact_crossing_classification_20261011 import classify

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-woo-sung-vancor-original-interfaces-v1-20261015'
DOC = BASE / BATCH
INPUTS = [
    ('government-xl-woo-sung90825-original-recovery-v1-20261015', 'selection.json.gz', 'landsd/90825:0', 1010),
    ('government-xl-vancor-90824-untouched-original-recovery-v1-20261011', 'selection.json.gz', 'landsd/90824:0', 646),
    ('government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011', 'check-selection.json.gz', 'landsd/147956:0', 669),
]

def main():
    assert not DOC.exists()
    refs = [Path(__file__)]
    actors, worlds = [], []
    for batch, filename, uid, count in INPUTS:
        folder = BASE / batch
        receipt = read(folder / 'result.json')
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
        selected = folder / filename
        assert dict(path=str(selected.relative_to(ROOT)), sha256=digest(selected.read_bytes())) in receipt['evidenceRefs']
        row = next(r for r in read(selected)['rows'] if r['uid'] == uid)
        asset = ROOT / row['candidate']['path']
        raw = asset.read_bytes()
        assert digest(raw) == row['sourceSHA256']
        world = decode_original_world_triangles(raw)
        assert world.shape == (count, 3, 3)
        worlds.append(world)
        actors.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], modelId=row['modelId'], completeFaces=count, worldSHA256=digest(world.tobytes())))
        refs.extend([folder / 'result.json', selected, asset])
    DOC.mkdir()
    pairs = []
    for index in [1, 2]:
        a, b = worlds[0], worlds[index]
        contacts = exact_finite_contacts(a, list(range(len(a))), b, list(range(len(b))))
        assert contacts['allPairsExamined'] and not contacts['sourceFacesOmitted']
        classified = [dict(sourceFaceA=c['sourceFaceA'], sourceFaceB=c['sourceFaceB'], **classify(a[c['sourceFaceA']], b[c['sourceFaceB']], c)) for c in contacts['contacts']]
        counts = dict(Counter(c['classification'] for c in classified))
        pair = dict(uidA=actors[0]['uid'], uidB=actors[index]['uid'], contacts=contacts, classified=classified, classificationCounts=counts)
        pairs.append(pair)
        save(DOC / ('pair-' + str(index) + '.json.gz'), pair)
        print(dict(uidB=pair['uidB'], contacts=len(classified), counts=counts), flush=True)
    result = dict(uids=[a['uid'] for a in actors], actors=actors,
                  comparisons=[dict(uidA=p['uidA'], uidB=p['uidB'], contacts=len(p['classified']), classificationCounts=p['classificationCounts']) for p in pairs],
                  currentAcceptance=False, sourceOnly=True, volumetricCollisionProved=False,
                  qualification='Complete immutable original-source contacts only. Historical Vancor inputs are not current placement approvals. Crossings alone are not an installation hold; identity, support and actual runtime conflicts remain independent.')
    save(DOC / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'exact_original_finite_triangle_contacts_20261010.py', 'exact_finite_contact_crossing_classification_20261011.py', 'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py'])
    module('woo_sung_interface_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-original-neighbour-source-interface-comparison-v1', refs, result)

if __name__ == '__main__':
    main()
