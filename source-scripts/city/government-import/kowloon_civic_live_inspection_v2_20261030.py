"""Prepare labelled real-live exports; --reviewed records ROOT's actual inspection."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
from run import ROOT, HERE, read, save, digest

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-kowloon-city-civic-five-after-fuying-'
CONFIG = BASE / (P + 'install-config-v1-20261030.json')
CFG = read(CONFIG)
INSTALL = CFG['prefix'] + '-original-installed-v5-' + CFG['date']
DOC = BASE / INSTALL
BATCH = 'government-xl-kowloon-city-civic-five-installed-root-readback-v2-20261030'
OUT = BASE / BATCH


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reviewed', action='store_true')
    args = parser.parse_args()
    specpath = OUT / 'spec.json'
    if args.reviewed:
        assert (DOC / 'result.json').exists()
        spec = read(specpath)
        assert spec['visualAcceptance'] is False
        for row in spec['imagesActuallyViewed'] + spec['inspectionSheetsActuallyViewed']:
            assert ref(ROOT / row['path']) == row
        spec['visualAcceptance'] = True
        spec['qualification'] = 'ROOT actually viewed all20 real-live source exports in four labelled sheets; independent installed-job/asset/old-actor/terrain/support/521-key audit follows separately.'
        save(specpath, spec)
        return
    assert not OUT.exists()
    stage = HERE / 'accepted' / (CFG['prefix'] + '-qualified-stage-v2-' + CFG['date'])
    models = read(stage / 'catalogue.json')['models']
    assert {m['uid']: m['sha256'] for m in models} == CFG['sources']
    images, sheets = [], []
    for width in [390, 1280]:
        folder = DOC / ('viewport-' + str(width))
        report = read(folder / 'live-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 10
        for time in [1500, 2200]:
            label = f'{time//100:02}:{time%100:02}'
            rows = sorted([v for v in views if v['time'] == label], key=lambda v: v['uid'])
            assert len(rows) == 5
            w, h = (195, 450) if width == 390 else (384, 270)
            sheet = Image.new('RGB', (w*5, h+36), 'white')
            draw = ImageDraw.Draw(sheet)
            for i, row in enumerate(rows):
                assert row['uid'] == row['pick'] == row['collision'] and row['sourceSHA256'] == CFG['sources'][row['uid']]
                assert row['fullyFramed'] and row['solidAppearance'] and not row['fallbackFaces']
                path = folder / row['file']
                images.append(ref(path))
                with Image.open(path) as image:
                    assert image.size == (width, 900)
                    image.thumbnail((w, h))
                    sheet.paste(image, (i*w+(w-image.width)//2, 36))
                draw.text((i*w+3, 3), row['uid']+' '+str(time), fill='black')
            target = OUT / (str(width)+'-'+str(time)+'.png')
            OUT.mkdir(parents=True, exist_ok=True)
            sheet.save(target)
            sheets.append(ref(target))
    terrain = read(stage / 'plan.json')['topLevelTerrainPatches'][0]
    n = CFG['previousInstalled'] + CFG['expectedFixedXLDelta']
    save(specpath, dict(readbackBatch=BATCH, installBatch=INSTALL, reviewer='ROOT', visualAcceptance=False,
                       imagesActuallyViewed=images, inspectionSheetsActuallyViewed=sheets, producer=ref(Path(__file__)),
                       phaseBatches=[P+'source-review-v1-20261030', stage.name, CFG['browser'], P+'atomic-lifecycle-v1-20261030'],
                       expectedCounts=dict(total=521, installedVerified=n, remaining=521-n),
                       expectedCatalogueActors=CFG['currentNativeActors']+len(models),
                       sourceTriangleCounts={m['uid']: m['triangles'] for m in models},
                       previousCountReport='docs/astra-city/government-import/'+CFG['previousCountReport'],
                       terrainAddition=dict(url=terrain['destination'], sha256=terrain['sha256']),
                       terrainTargetUids=['landsd/82290:0','landsd/82291:0','landsd/82292:0']))
    print('Prepared20actual live exports in4labelled sheets; visual acceptance remainsfalse.', flush=True)


if __name__ == '__main__':
    main()
