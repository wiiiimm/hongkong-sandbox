"""Recover three exact cached government companions and bind a fresh unapproved selection."""
from pathlib import Path, PurePosixPath
from copy import deepcopy
import os, sys, tarfile
import numpy as np
from dotenv import dotenv_values
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0, str(HERE.parent / 'landmark-resume'))
from r2_snapshot import R2Store, verify_object


def main():
    batch = 'government-xl-lamma-power-four-original-selection-v1-20261023'
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / batch, HERE / 'local' / batch
    assert not out.exists() and not local.exists()
    parent = 'government-xl-lamma-power-315414-current-selection-v1-20261023'
    _, pins = authenticate(base / parent)
    path = base / parent / 'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    selected = read(path)
    mainrow, = selected['rows']
    assert mainrow['uid'] == 'landsd/315414:0'
    refs = [Path(__file__), base / parent / 'result.json', path]
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == selected['manifestSHA256']
    refs.append(manifestpath)
    wanted = {'B291620883401063C0': 'landsd/79169:0', 'B292140884001063C0': 'landsd/197134:0', 'B292910884101063C0': 'landsd/199519:0'}
    records = {}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        rows = db.execute("SELECT i.cache_key,i.sheet,i.source_sha,r.result_sha,r.result->'artifacts',m FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m WHERE i.cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)", (['ba37beaf30dcb38c8c940e39c04145bbd9fa039fed5807190b0028eb9ed8458a', 'fb7255c57d5b7dea00ed9fb4d367f22fe90813fc0481b881f7703728a7797843'], sorted(wanted))).fetchall()
    assert len(rows) == len(wanted)
    for key, sheet, source, sha, artifacts, model in rows:
        assert model['modelId'] in wanted and model['modelId'] not in records
        assert model['state'] == 'packed-needs-placement-review'
        assert model['candidate']['uid'] == wanted[model['modelId']]
        artifacts = [a for a in artifacts if a['kind'] == 'original-and-prepared-sheet']
        assert len(artifacts) == 1
        records[model['modelId']] = dict(cacheKey=key, sheet=sheet, sourceSHA256=source, resultSHA256=sha, artifact=artifacts[0], model=model)
    forms = {}
    for e in read(manifestpath)['tiles']:
        tile = ROOT / '3d-viewer' / e['url']
        for f in read(tile)['buildings']:
            if f['uid'] in wanted.values():
                assert f['uid'] not in forms
                forms[f['uid']] = dict(building=f, tile=e['url'], tileSHA256=digest(tile.read_bytes()))
                refs.append(tile)
    assert set(forms) == set(wanted.values())
    for url in read(manifestpath)['officialModelCatalogues']:
        p = ROOT / '3d-viewer' / url
        assert not set(wanted.values()).intersection(m['uid'] for m in read(p)['models'])
        refs.append(p)
    for name, value in dotenv_values(ROOT / '.env.modelling').items():
        if name.startswith('R2_') and value:
            os.environ.setdefault(name, value)
    store = R2Store('hk-sandbox-assets')
    assets, bundles = {}, {}
    for modelid, record in sorted(records.items()):
        a = record['artifact']
        assert a['key'] == 'astra-modelling/objects/sha256/' + a['sha256'][:2] + '/' + a['sha256']
        assert 0 < a['bytes'] < 32_000_000
        if a['sha256'] not in bundles:
            p = local / 'bundles' / (a['sha256'] + '.tar.gz')
            p.parent.mkdir(parents=True, exist_ok=True)
            verify_object(store, a['key'], a['sha256'], a['bytes'], p)
            bundles[a['sha256']] = p
            refs.append(p)
        asset = record['model']['asset']
        membername = 'converted/' + asset['asset']
        safe = PurePosixPath(membername)
        assert not safe.is_absolute() and '..' not in safe.parts and '\\' not in membername
        with tarfile.open(bundles[a['sha256']], 'r:gz') as archive:
            matches = [m for m in archive.getmembers() if m.name == membername]
            assert len(matches) == 1 and matches[0].isfile() and matches[0].size == asset['bytes'] < 4_000_000
            with archive.extractfile(matches[0]) as stream:
                raw = stream.read()
        assert digest(raw) == asset['sha256']
        p = local / asset['asset']
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        tri = decode_original_world_triangles(raw)
        assert len(tri) == record['model']['triangles'] and np.isfinite(tri).all()
        assets[modelid] = p
        refs.append(p)
    rows = [deepcopy(mainrow)]
    for modelid, record in sorted(records.items()):
        uid, model = wanted[modelid], record['model']
        form = forms[uid]
        entry = deepcopy(model['candidate'])
        assert entry['modelId'] == modelid and entry['sha256'] == model['asset']['sha256']
        assert entry['buildingCSUID'] == form['building']['buildingCSUID'] and entry['objectId'] == form['building']['objectId']
        for key in ['sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed', 'publicationApproved']:
            assert not entry.get(key)
            entry[key] = False
        for key, field in [('recordedBaseHeight', 'baseHeightHKPD'), ('recordedTopHeight', 'topHeightHKPD')]:
            assert key not in entry or entry[key] == form['building'][field]
            entry[key] = form['building'][field]
        entry.update(rootTranslation=[-834500, 0, 816500], sourceTile=record['sheet'], priority='unreviewed', proceduralWindows=False)
        rows.append(dict(uid=uid, modelId=modelid, triangles=model['triangles'], sourceSHA256=model['asset']['sha256'], candidate=dict(path=str(assets[modelid].relative_to(ROOT)), entry=entry), source=form, native=dict(cacheKey=record['cacheKey'], resultSha=record['resultSHA256'], model=model), originalGeometryOnly=True))
    assert digest(manifestpath.read_bytes()) == selected['manifestSHA256']
    refs.append(ROOT / mainrow['candidate']['path'])
    assert digest(refs[-1].read_bytes()) == mainrow['sourceSHA256']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for r in records.values():
            assert db.execute('SELECT i.source_sha,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (r['cacheKey'],)).fetchone() == (r['sourceSHA256'], r['resultSHA256'])
    save(out / 'source-records.json', records)
    save(out / 'selection.json.gz', dict(rows=rows, manifestSHA256=selected['manifestSHA256']))
    result = dict(uids=[r['uid'] for r in rows], sourceSHA256ByUid={r['uid']:r['sourceSHA256'] for r in rows}, recoveredCompanionSources=3, originalFaces=sum(r['triangles'] for r in rows), sourceGeometryChanges=0, installationApproved=False, publication=False, qualification='Exact compact native records and immutable original-and-prepared source bundles verified against pinned Neon result/source identities. Cached prepared model bytes copied unchanged. Complete original ownership/identity, actual four-source geometry, contacts, terrain, all neighbours and browser/publication checks remain unapproved. No fitting, scaling, simplification, AI geometry modelling or current-stage approval transfer.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py', HERE.parent / 'landmark-resume/r2_snapshot.py'])
    module('lamma_companion_selection_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'exact-cached-original-companion-recovery-and-selection', refs, result)
    print(dict(models=len(rows), originalFaces=result['originalFaces'], recoveredCompanionSources=3), flush=True)


if __name__ == '__main__':
    main()
