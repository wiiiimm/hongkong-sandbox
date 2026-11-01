"""Keep existing live-export guards; record honest contact-sheet inspection.

Each sheet is regenerated from its four hashed original PNGs. The original
recorder still validates every source image, viewport, report, fallback, joint,
source hash and installed receipt. Only inspection-method/provenance metadata
differs; no model approval can be recorded without supplied manual observations.
"""
import argparse
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw
from run import ROOT, HERE, read, digest
from primrose_compound_foundation_v2_20261015 import module


def sheet(images):
    assert len(images) == 4 and len({i['uid'] for i in images}) == 1
    by_view = {(i['width'], i['time']): i for i in images}
    order = [(1280, '15:00'), (1280, '22:00'), (390, '15:00'), (390, '22:00')]
    assert len(by_view) == 4 and set(by_view) == set(order)
    result = Image.new('RGB', (1100, 880), '#eeeeee')
    draw = ImageDraw.Draw(result)
    for index, view in enumerate(order):
        item = by_view[view]
        path = ROOT / item['path']
        assert digest(path.read_bytes()) == item['sha256']
        image = Image.open(path).convert('RGB')
        image.thumbnail((545, 405))
        x, y = index % 2 * 550, index // 2 * 440
        draw.text((x + 4, y + 4), f"{item['uid']} {view[0]}px {view[1]}", fill='black')
        result.paste(image, (x + (550 - image.width) // 2, y + 28))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observation', required=True)
    args = parser.parse_args()
    path = (ROOT / args.observation).resolve()
    assert path.is_relative_to(ROOT / 'docs/astra-city/government-import')
    observation = read(path)
    assert observation['allDeclaredExportsActuallyInspected']
    groups = defaultdict(list)
    for image in observation['imagesActuallyViewed']:
        groups[image['uid']].append(image)
    sheets = observation['inspectionSheetsActuallyViewed']
    assert len(sheets) == len(groups) == len({s['uid'] for s in sheets})
    assert {s['uid'] for s in sheets} == set(groups)
    for item in sheets:
        image_path = (ROOT / item['path']).resolve()
        assert image_path.is_relative_to(ROOT / 'docs/astra-city/government-import')
        assert digest(image_path.read_bytes()) == item['sha256']
        expected = sheet(groups[item['uid']])
        actual = Image.open(image_path).convert('RGB')
        assert expected.size == actual.size and expected.tobytes() == actual.tobytes()
    recorder = module('unchanged_original_live_export_recorder',
                      HERE / 'original_supported_live_export_inspection_v1_20261101.py')
    original_save = recorder.save
    def write(target, value):
        assert target.name == 'ROOT-LIVE-EXPORT-INSPECTION.json'
        assert value['inspectionMethod'] == 'Every declared live PNG source canvas opened directly'
        value = {**value,
                 'inspectionMethod': 'All declared live source exports inspected via labelled four-view sheets, regenerated from every exact hashed original PNG',
                 'inspectionSheetsActuallyViewed': sheets,
                 'originalRecorder': value['producer'],
                 'producer': dict(path=str(Path(__file__).relative_to(ROOT)),
                                  sha256=digest(Path(__file__).read_bytes()))}
        return original_save(target, value)
    recorder.save = write
    recorder.main()


if __name__ == '__main__':
    main()
