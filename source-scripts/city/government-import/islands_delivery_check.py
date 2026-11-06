"""Make inspection sheets or independently read back an additive island install.

Sheet creation grants no visual acceptance. The inspect/readback operations are
explicit acknowledgements by the agent after actually viewing every sheet.
"""
import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from islands_direct_worker import solid_verified
from run import connect


def images(doc, phase):
    report = doc / ('solid-staged-browser.json' if phase == 'staged' else 'live-browser.json')
    rows = [v for v in read(report)['views'] if 'time' in v]
    return report, rows


def sheets(doc, phase):
    report, rows = images(doc, phase)
    paths = []
    for start in range(0, len(rows), 8):
        group = rows[start:start + 8]
        canvas = Image.new('RGB', (1440, math.ceil(len(group) / 2) * 350), '#dddddd')
        draw = ImageDraw.Draw(canvas)
        for i, row in enumerate(group):
            picture = Image.open(doc / row['file']).convert('RGB')
            picture.thumbnail((710, 320))
            x, y = (i % 2) * 720, (i // 2) * 350
            canvas.paste(picture, (x, y + 25))
            draw.text((x + 5, y + 5), f"{row['uid']} {row['width']} {row['time']}", fill='black')
        path = doc / f'{phase}-inspection-sheet-{start // 8 + 1:02d}.jpg'
        assert not path.exists()
        canvas.save(path, quality=94)
        paths.append({'path': rel(path), 'sha256': sha(path)})
    save(doc / f'{phase}-inspection-sheets.json', {
        'report': rel(report), 'reportSHA256': sha(report), 'sheets': paths,
        'images': [{'path': rel(doc / v['file']), 'sha256': sha(doc / v['file'])} for v in rows],
        'actuallyViewed': False,
    })
    print({'images': len(rows), 'sheets': [p['path'] for p in paths]}, flush=True)


def inspect(doc, batch, phase):
    metadata = read(doc / f'{phase}-inspection-sheets.json')
    for item in metadata['images'] + metadata['sheets']:
        assert sha(ROOT / item['path']) == item['sha256']
    assert sha(ROOT / metadata['report']) == metadata['reportSHA256']
    stage = HERE / 'accepted' / batch
    report, rows = images(doc, phase)
    solid_verified(read(report), read(stage / 'catalogue.json')['models'])
    result = {**metadata, 'actuallyViewed': True, 'renderingAccepted': True,
              'stagedBrowserSHA256' if phase == 'staged' else 'liveBrowserSHA256': sha(report),
              'limitations': 'Original source geometry and retained neighbours; no every-facet/as-built or physical-device performance claim.'}
    if phase == 'staged':
        assert not read(stage / 'browser-config.json').get('visibilitySupplementUids')
        save(doc / 'staged-inspection.json', result)
        return
    installed = read(doc / 'integration.json')
    assert installed['neonVerified'] and installed['liveBrowserSHA256'] == sha(report)
    pins = read(doc / 'retained-inputs.json')
    for path, digest in pins.items():
        assert sha(ROOT / path) == digest, path
    before = read(HERE / 'local' / batch / 'manifest-before.json')
    current = read(ROOT / '3d-viewer/city/data/manifest.json')
    assert sha(ROOT / '3d-viewer/city/data/manifest.json') == installed['manifestSHA256']
    destination = f'city/data/official-models/{batch}/catalogue.json'
    expected = {**before, 'officialModelCatalogues': before['officialModelCatalogues'] + [destination]}
    plan = read(stage / 'plan.json')
    additions = plan.get('topLevelTerrainPatches', [])
    assert len(current['terrainPatches']) == len(before['terrainPatches']) + len(additions)
    assert current['terrainPatches'][:len(before['terrainPatches'])] == before['terrainPatches']
    for addition, actual in zip(additions, current['terrainPatches'][len(before['terrainPatches']):]):
        assert actual['url'] == addition['destination']
        assert sha(ROOT / '3d-viewer' / actual['url']) == addition['sha256']
    expected['terrainPatches'] = current['terrainPatches']
    assert current == expected
    catalogue_path = ROOT / '3d-viewer' / destination
    models = read(catalogue_path)['models']
    assert set(installed['uids']) == {m['uid'] for m in models}
    for model in models:
        assert sha(catalogue_path.parent / model['asset']) == model['sha256']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        rows = dict(db.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',
                               (installed['snapshotId'], installed['uids'])))
    assert rows == {uid: 'installed-verified' for uid in installed['uids']}
    save(doc / 'independent-installed-readback.json', {
        **result, 'passed': True, 'installed': len(models), 'snapshotId': installed['snapshotId'],
        'allOldCatalogueAssetTerrainAndTileBytesPreserved': True, 'oldFilesVerified': len(pins),
        'onlyManifestChange': f'Append one catalogue and {len(additions)} exact terrain patches',
        'sourceGeometryChanges': 0, 'exactNeonRows': len(rows),
    })
    print({'installedReadback': len(models), 'oldFilesVerified': len(pins), 'terrainAdditions': len(additions)}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('sheets', 'inspect'))
    parser.add_argument('--batch', required=True)
    parser.add_argument('--phase', required=True, choices=('staged', 'live'))
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    assert args.batch.startswith('government-islands-') and '/' not in args.batch
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    if args.attempt != 1:
        doc = doc / f'attempt-{args.attempt}'
    if args.operation == 'sheets':
        sheets(doc, args.phase)
    else:
        inspect(doc, args.batch, args.phase)


if __name__ == '__main__':
    main()
