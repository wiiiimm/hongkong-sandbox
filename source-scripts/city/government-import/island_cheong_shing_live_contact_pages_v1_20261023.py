"""Create bounded hash-bound overview pages from complete live retained exports.

This script never grants review approval or changes original images.
"""
import argparse
import math
from PIL import Image, ImageDraw
from run import ROOT, read, save, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--browser', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--width', type=int, choices=[390, 1280], required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.browser, a.out])
    base = ROOT / 'docs/astra-city/government-import'
    folder = base / a.browser / ('viewport-' + str(a.width))
    reportpath = folder / 'live-browser.json'
    report = read(reportpath)
    assert report['passed'] and not report['errors']
    rows = sorted(report['retainedNativeOwnViews'], key=lambda r: (r['uid'], r['time']))
    assert rows and len(rows) == len({(r['uid'], r['time']) for r in rows})
    assert all(r['active'] and r['visible'] and r['fullyFramed'] and not r['fallbackFaces'] for r in rows)
    out = base / a.out
    out.mkdir(exist_ok=True)
    for start in range(0, len(rows), 12):
        page = rows[start:start + 12]
        w, h = (390, 900) if a.width == 390 else (640, 450)
        canvas = Image.new('RGB', (w * 3, (h + 24) * math.ceil(len(page) / 3)), '#202020')
        draw = ImageDraw.Draw(canvas)
        refs = []
        path = out / f'live-retained-{a.width}-page-{start // 12 + 1}.jpg'
        binding = path.with_name(path.stem + '-binding.json')
        assert not path.exists() and not binding.exists()
        for i, row in enumerate(page):
            source = folder / row['file']
            refs.append(dict(path=str(source.relative_to(ROOT)), sha256=digest(source.read_bytes())))
            with Image.open(source) as raw:
                assert raw.size == (a.width, 900)
                im = raw.convert('RGB')
            if a.width == 1280:
                im = im.resize((w, h), Image.Resampling.LANCZOS)
            x, y = (i % 3) * w, (i // 3) * (h + 24)
            canvas.paste(im, (x, y + 24))
            draw.text((x + 3, y + 4), row['uid'] + ' ' + row['time'], fill='white')
        canvas.save(path, quality=95)
        assert all(digest((ROOT / r['path']).read_bytes()) == r['sha256'] for r in refs)
        save(binding, dict(report=dict(path=str(reportpath.relative_to(ROOT)), sha256=digest(reportpath.read_bytes())), inputs=refs, output=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), originalExportsUnchanged=True, displayedScale=1 if a.width == 390 else .5, visualAcceptance=False))
        print(path, flush=True)


if __name__ == '__main__':
    main()
