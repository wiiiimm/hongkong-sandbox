"""Index and compose unmodified completed browser exports for ROOT inspection.

Desktop panels use50% scale; mobile panels retain their original390x900pixels.
This creates inspection sheets, never alters the source PNGs or grants approval.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from run import ROOT, read, save, digest

BASE = ROOT/'docs/astra-city/government-import'
SOURCE = BASE/'government-xl-silvercord-lippo-private-six-part-browser-v4-20261103'
OUT = BASE/'government-xl-silvercord-private-success-export-sheets-v1-20261103'


def main():
    assert not OUT.exists()
    OUT.mkdir()
    sheets, originals = [], []
    for width in [1280,390]:
        report = read(SOURCE/str(width)/'staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v] + report['retainedNativeOwnViews']
        assert len(views) == 18 and len({v['file'] for v in views}) == 18
        cell = (640,478) if width == 1280 else (390,928)
        columns, rows = (2,3) if width == 1280 else (3,2)
        for offset in range(0,len(views),6):
            canvas = Image.new('RGB',(cell[0]*columns,cell[1]*rows),'white')
            draw = ImageDraw.Draw(canvas)
            included = []
            for slot,v in enumerate(views[offset:offset+6]):
                path = SOURCE/str(width)/v['file']
                sha = digest(path.read_bytes())
                with Image.open(path) as image:
                    image.load()
                    assert image.size == (width,900) and image.format == 'PNG'
                    assert any(lo!=hi for lo,hi in image.convert('RGB').getextrema())
                    preview = ImageOps.contain(image.convert('RGB'),(cell[0],cell[1]-28))
                    x,y = (slot%columns)*cell[0],(slot//columns)*cell[1]
                    draw.text((x+5,y+5),v['uid']+' '+v['time']+' '+str(width),fill='black')
                    canvas.paste(preview,(x,y+28))
                item = dict(path=str(path.relative_to(ROOT)),sha256=sha,uid=v['uid'],time=v['time'],
                            originalDimensions=[width,900],sourceSHA256=v['sourceSHA256'])
                originals.append(item)
                included.append(item)
                assert digest(path.read_bytes()) == sha
            output = OUT/(str(width)+'-sheet-'+str(offset//6+1)+'.png')
            canvas.save(output)
            sheets.append(dict(path=str(output.relative_to(ROOT)),sha256=digest(output.read_bytes()),
                dimensions=list(canvas.size),desktopScale=.5 if width==1280 else 1,originals=included))
    save(OUT/'index.json',dict(sheets=sheets,originals=originals,originalPNGsUnchanged=True,
        actualSheetInspectionStillRequired=True,visualAcceptance=False,installationApproved=False,publication=False))
    print(dict(sheets=len(sheets),sourcePNGs=len(originals),approval=False))


if __name__ == '__main__':
    main()
