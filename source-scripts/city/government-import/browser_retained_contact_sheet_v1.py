"""Compose hash-bound retained-browser exports for visual inspection; no asset edits."""
import argparse
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from run import ROOT, read, save, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--browser', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--width', type=int, choices=[390, 1280], required=True)
    p.add_argument('--mode', choices=['staged', 'live'], required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.browser, a.out])
    base = ROOT / 'docs/astra-city/government-import'
    folder = base / a.browser / (str(a.width) if a.mode == 'staged' else 'viewport-' + str(a.width))
    reportpath = folder / (a.mode + '-browser.json')
    report = read(reportpath)
    assert report['passed'] and not report['errors']
    rows = sorted(report['retainedNativeOwnViews'], key=lambda r: (r['uid'], r['time']))
    assert rows and len({(r['uid'], r['time']) for r in rows}) == len(rows)
    assert all(r['active'] and r['visible'] and r['fullyFramed'] and not r['fallbackFaces'] for r in rows)
    columns = 3 if a.width == 390 else 2
    count = math.ceil(len(rows) / columns)
    fig, axes = plt.subplots(count, columns, figsize=(columns * 4, count * (6 if a.width == 390 else 3)), squeeze=False)
    inputs = []
    for ax in axes.flat:
        ax.axis('off')
    for ax, row in zip(axes.flat, rows):
        path = folder / row['file']
        inputs.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
        ax.imshow(mpimg.imread(path))
        ax.set_title(row['uid'] + ' ' + row['time'], fontsize=9)
    fig.tight_layout(pad=.5)
    out = base / a.out
    out.mkdir(parents=True, exist_ok=True)
    path = out / f'{a.mode}-retained-{a.width}-contact.png'
    assert not path.exists()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    assert all(digest((ROOT / r['path']).read_bytes()) == r['sha256'] for r in inputs)
    save(out / f'{a.mode}-retained-{a.width}-contact-inputs.json', dict(report=dict(path=str(reportpath.relative_to(ROOT)), sha256=digest(reportpath.read_bytes())), inputs=inputs, output=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), qualification='Overview composed from exact complete exports; fit/resampling only. Original files untouched. No visual acceptance is granted by this script.'))
    print(path, flush=True)


if __name__ == '__main__':
    main()
