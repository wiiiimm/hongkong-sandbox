"""Compose authenticated completed mobile-group exports, without approval credit."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--group', action='append', required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, *a.group])
    assert len(a.group) == len(set(a.group))
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, groups, all_images = [Path(__file__)], [], []
    for n, batch in enumerate(a.group, 1):
        folder = base / batch
        _, pins = authenticate(folder)
        report_path = folder / 'staged-browser.json'
        assert digest(report_path.read_bytes()) == pins[str(report_path.relative_to(ROOT))]
        report = read(report_path)
        assert report['passed'] and not report['errors'] and report['retainedOnly']
        assert report['newSourceAcceptance'] is False and not report['views']
        refs.extend([folder / 'result.json', report_path])
        panels, records = [], []
        for row in report['retainedNativeOwnViews']:
            assert row['width'] == 390 and row['time'] in ['15:00', '22:00']
            assert row['active'] and row['visible'] and row['sourcePixelVisibility']['visiblePixels'] >= 32
            image = (folder / row['file']).resolve()
            assert image.is_relative_to(folder.resolve())
            assert digest(image.read_bytes()) == pins[str(image.relative_to(ROOT))]
            refs.append(image)
            with Image.open(image) as im:
                panels.append(im.convert('RGB'))
            records.append(dict(uid=row['uid'], time=row['time'], path=str(image.relative_to(ROOT)),
                                sha256=digest(image.read_bytes()), sourceSHA256=row['sourceSHA256'],
                                actualVisibleTargetPixels=row['sourcePixelVisibility']['visiblePixels']))
        assert panels and len(records) == len({(r['uid'], r['time']) for r in records})
        uids = {r['uid'] for r in records}
        assert {(r['uid'], r['time']) for r in records} == {(u, t) for u in uids for t in ['15:00', '22:00']}
        w, h = max(im.width for im in panels), max(im.height for im in panels) + 26
        sheet = Image.new('RGB', (w * 4, h * ((len(panels) + 3) // 4)), 'white')
        draw = ImageDraw.Draw(sheet)
        for i, (im, row) in enumerate(zip(panels, records)):
            x, y = i % 4 * w, i // 4 * h
            draw.text((x + 3, y + 5), row['uid'] + ' ' + row['time'], fill='black')
            sheet.paste(im, (x, y + 26))
        path = out / ('group-' + str(n).zfill(2) + '.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(path)
        groups.append(dict(batch=batch, sheet=str(path.relative_to(ROOT)), sheetSHA256=digest(path.read_bytes()),
                           images=records, scale=1, cropped=False))
        all_images.extend(records)
    result = dict(uids=sorted({r['uid'] for r in all_images}), groups=groups,
                  sourceImageCount=len(all_images), contactSheetCount=len(groups), imagesActuallyReviewed=False,
                  visualAcceptance=False, installationApproved=False, publication=False, sourceGeometryChanges=0,
                  qualification='Unscaled, uncropped, complete authenticated PNG exports with labels/padding. '
                  'Actual root inspection must be recorded separately; composition grants no approval.')
    save(out / 'summary.json', result)
    module('mobile_group_sheets_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'completed-mobile-group-pixel-preserving-inspection-sheets', refs, result)
    print(dict(images=len(all_images), sheets=len(groups)), flush=True)


if __name__ == '__main__':
    main()
