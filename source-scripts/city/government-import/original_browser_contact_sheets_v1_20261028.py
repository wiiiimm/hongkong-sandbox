"""Build labelled QA sheets from completed actual-viewer PNG exports.

No original image resizing/rewriting, model processing or review approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--width', type=int, choices=[1280, 390], required=True)
    a = p.parse_args()
    report_path = a.source/'staged-browser.json'
    report = json.loads(report_path.read_text())
    assert report['passed'] and not report['errors'], 'No successful viewport report'
    name = 'desktop' if a.width == 1280 else 'mobile'
    manifest_path = a.out/(name+'-contact-sheets.json')
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        assert manifest['sourceReportSHA256'] == sha(report_path)
        for r in manifest['originalImages']:
            assert sha(Path(r['path'])) == r['sha256']
        for r in manifest['sheets']:
            assert sha(Path(r['path'])) == r['sha256']
        print('Existing verified sheets retained; no repeated rendering')
        return
    a.out.mkdir(parents=True, exist_ok=True)
    files = sorted(a.source.glob('*.png'))
    assert files
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18 if a.width == 1280 else 12)
    rows, sheets, warnings = [], [], []
    for index in range(0, len(files), 4):
        group = files[index:index+4]
        sheet = Image.new('RGB', (a.width*2, 1848), '#20252e')
        draw = ImageDraw.Draw(sheet)
        for n, path in enumerate(group):
            image = Image.open(path).convert('RGB')
            assert image.size == (a.width, 900)
            x, y = n % 2*a.width, n//2*924
            sheet.paste(image, (x, y+24))
            draw.text((x+8, y+1), path.name, font=font, fill='white')
            extrema = image.getextrema()
            flat = not any(hi-lo > 20 for lo, hi in extrema)
            if flat:
                warnings.append(dict(path=str(path), reason='low-channel-variation-needs-image-review'))
            rows.append(dict(path=str(path), sha256=sha(path), width=a.width, height=900,
                             channelExtrema=extrema, flatSceneWarning=flat, sheet=index//4+1))
        dest = a.out/(name+'-sheet-'+str(index//4+1).zfill(2)+'.png')
        sheet.save(dest)
        sheets.append(dict(path=str(dest), sha256=sha(dest), sourcePaths=[str(p) for p in group]))
    manifest_path.write_text(json.dumps(dict(sourceReportSHA256=sha(report_path), originalImages=rows,
        sheets=sheets, originalPixelsResized=False, flatSceneWarnings=warnings,
        reviewPending=True), sort_keys=True)+'\n')
    print(dict(images=len(rows), sheets=len(sheets), imageWarnings=len(warnings), reviewPending=True))


if __name__ == '__main__':
    main()
