"""Paginate exact retained-browser exports for bounded overview review; no asset edits."""
import argparse
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
    out = base / a.out
    out.mkdir(parents=True, exist_ok=True)
    columns = 3 if a.width == 390 else 2
    reviewed_inputs, sheets = [], []
    for page, start in enumerate(range(0, len(rows), 12), 1):
        part = rows[start:start+12]
        count = (len(part)+columns-1)//columns
        fig, axes = plt.subplots(count, columns, figsize=(columns*4, count*(6 if a.width == 390 else 3)), squeeze=False)
        for ax in axes.flat: ax.axis('off')
        inputs = []
        for ax, row in zip(axes.flat, part):
            path = folder / row['file']
            inputs.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
            ax.imshow(mpimg.imread(path))
            ax.set_title(row['uid']+' '+row['time'], fontsize=9)
        fig.tight_layout(pad=.5)
        path = out / f'{a.mode}-retained-{a.width}-page-{page}.png'
        assert not path.exists()
        fig.savefig(path, dpi=100)
        plt.close(fig)
        assert all(digest((ROOT / r['path']).read_bytes()) == r['sha256'] for r in inputs)
        output = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
        binding = path.with_suffix('.json')
        assert not binding.exists()
        save(binding, dict(report=dict(path=str(reportpath.relative_to(ROOT)), sha256=digest(reportpath.read_bytes())), inputs=inputs, output=output, qualification='Overview of exact exports, resampled for fit only. Original bytes untouched. No visual acceptance or unobstructed-grade claim.'))
        reviewed_inputs.extend(inputs)
        sheets.append(dict(output=output, binding=dict(path=str(binding.relative_to(ROOT)), sha256=digest(binding.read_bytes()))))
    assert len(reviewed_inputs) == len(rows) == len({r['path'] for r in reviewed_inputs})
    save(out / f'{a.mode}-retained-{a.width}-index.json', dict(inputs=reviewed_inputs, sheets=sheets))
    print(dict(exports=len(rows), pages=len(sheets)), flush=True)


if __name__ == '__main__':
    main()
