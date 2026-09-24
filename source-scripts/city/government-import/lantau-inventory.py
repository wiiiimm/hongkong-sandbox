"""Report Lantau building-form government detail coverage without creating work queues."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'source-scripts/city/shared-modelling'))
from db import connect

RUN_ID = 'e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec'
SECTION_IDS = tuple(f'10.{number}' for number in range(5, 12))
SIZE_ORDER = ('xxl', 'xl', 'large', 'medium', 'small', 'xs', 'unmeasured')
SIZE_LABELS = {'xxl': 'XXL', 'xl': 'XL', 'large': 'L', 'medium': 'M',
               'small': 'S', 'xs': 'XS', 'unmeasured': 'Unmeasured'}


def read(path):
    return json.loads(path.read_bytes())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_geometry(path):
    sections = read(path)['sections']
    selected = {}
    for section in sections:
        if section['id'] not in SECTION_IDS:
            continue
        selected[section['id']] = {
            'name': section['name'],
            'geometry': [Polygon(item['rings'][0], item['rings'][1:])
                         for item in section['polygons']],
        }
    assert tuple(sorted(selected, key=lambda value: int(value.split('.')[1]))) == SECTION_IDS
    return selected


def installed_models(manifest):
    official = {}
    for url in manifest['officialModelCatalogues']:
        catalogue = read(ROOT / '3d-viewer' / url)
        for model in catalogue['models']:
            previous = official.get(model['uid'])
            assert not previous or previous['sha256'] == model['sha256'], model['uid']
            official[model['uid']] = model
    return official


def collect_forms(manifest, sections):
    rows = []
    embedded = set()
    seen = set()
    total = 0
    for tile in manifest['tiles']:
        payload = read(ROOT / '3d-viewer' / tile['url'])
        for building in payload['buildings']:
            total += 1
            uid = building['uid']
            assert uid not in seen, uid
            seen.add(uid)
            if building.get('modelGeometry'):
                embedded.add(uid)
            footprint = Polygon(building['rings'][0], building['rings'][1:])
            centre = footprint.centroid
            matches = [section_id for section_id, section in sections.items()
                       if any(region.covers(centre) for region in section['geometry'])]
            if not matches:
                continue
            assert len(matches) == 1, (uid, matches)
            rows.append({'building': building, 'sectionId': matches[0],
                         'centre': [centre.x, centre.y], 'tile': tile['id']})
    assert total == manifest['counts']['buildings'] == len(seen)
    return rows, embedded, total


def size_records(uids):
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        rows = connection.execute('''
            SELECT viewer_uid,size_group,triangles,model_id,building_csuid,
                   source_state,source_hold_reason,compressed_bytes,geometry_bytes
            FROM astra_modelling.native_model_sizes
            WHERE run_id=%s AND viewer_uid=ANY(%s)
            ORDER BY viewer_uid,triangles DESC NULLS LAST,model_id
        ''', (RUN_ID, list(uids))).fetchall()
    result = {}
    for row in rows:
        uid = row[0]
        assert uid not in result, 'Size run has more than one matched model for '+uid
        result[uid] = {
            'sizeGroup': row[1], 'triangles': row[2], 'modelId': row[3],
            'buildingCSUID': row[4], 'sourceState': row[5],
            'sourceHoldReason': row[6], 'compressedBytes': row[7],
            'geometryBytes': row[8],
        }
    return result


def group_counts(rows, sizes, installed):
    available = Counter()
    ready = Counter()
    by_section = defaultdict(lambda: {'forms': 0, 'available': Counter(), 'installed': Counter()})
    for row in rows:
        uid = row['building']['uid']
        section = by_section[row['sectionId']]
        section['forms'] += 1
        size = sizes.get(uid)
        if not size:
            continue
        group = size['sizeGroup']
        available[group] += 1
        section['available'][group] += 1
        if uid in installed:
            ready[group] += 1
            section['installed'][group] += 1
    tiers = []
    for group in SIZE_ORDER:
        tiers.append({'sizeGroup': group, 'label': SIZE_LABELS[group],
                      'available': available[group], 'installed': ready[group],
                      'enhancementRequired': available[group] - ready[group]})
    return tiers, by_section


def write_readme(path, summary):
    lines = [
        '# Lantau government-model inventory — current manifest', '',
        'This report covers the project review sections 10.5–10.11. It includes Discovery Bay, '
        'Mui Wo, Pui O, south and southwest Lantau, Tai O and Ngong Ping. It excludes both Tung '
        'Chung sections, Chek Lap Kok airport and the other islands.', '',
        '| Measure | Building forms |', '| --- | ---: |',
        f"| All mapped Lantau forms | {summary['allForms']:,} |",
        f"| Matched government model available | {summary['governmentAvailable']:,} |",
        f"| Government detail installed | {summary['installed']:,} |",
        f"| Matched government enhancement remaining | {summary['enhancementRequired']:,} |",
        f"| No matched government source | {summary['noMatchedGovernmentSource']:,} |", '',
        '| Complexity | Available | Installed | Enhancement required |',
        '| --- | ---: | ---: | ---: |',
    ]
    for tier in summary['tiers']:
        lines.append(f"| {tier['label']} | {tier['available']:,} | {tier['installed']:,} | {tier['enhancementRequired']:,} |")
    lines += ['', '| Area | All forms | Gov available | Installed | Enhancement required | No gov match |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for section in summary['sections']:
        lines.append(f"| {section['id']} {section['name']} | {section['allForms']:,} | "
                     f"{section['governmentAvailable']:,} | {section['installed']:,} | "
                     f"{section['enhancementRequired']:,} | {section['noMatchedGovernmentSource']:,} |")
    lines += ['',
        '`buildings.csv` lists every included source form and its section, source identity, tier, '
        'installation path and actionable state. Complexity is the unchanged government model’s '
        'triangle bracket; forms without a matched government model are intentionally unmeasured.', '',
        '“Enhancement required” means that an exact viewer-to-government source match exists but '
        'that source is not currently present through either an embedded model or a manifest-listed '
        'progressive catalogue. It does not assert that the existing fallback looks poor. Forms with '
        'no matched government source remain a separate acquisition or non-government modelling '
        'population. No queue, reservation, database write, model download, geometry edit or AI '
        'modelling call was made by this report.', '',
    ]
    path.write_text('\n'.join(lines))


def run(output):
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    sections_path = ROOT / '3d-viewer/city/data/review-sections.json'
    manifest = read(manifest_path)
    sections = section_geometry(sections_path)
    forms, embedded, territory_total = collect_forms(manifest, sections)
    official = installed_models(manifest)
    installed = embedded | set(official)
    sizes = size_records(row['building']['uid'] for row in forms)
    tiers, by_section = group_counts(forms, sizes, installed)

    output.mkdir(parents=True, exist_ok=True)
    columns = ('uid', 'objectId', 'buildingCSUID', 'name', 'nameZh', 'sectionId',
               'sectionName', 'tile', 'centreX', 'centreZ', 'baseHeight', 'height',
               'heightSource', 'governmentAvailable', 'sizeGroup', 'sizeLabel',
               'triangles', 'modelId', 'sourceState', 'sourceHoldReason',
               'compressedBytes', 'geometryBytes', 'installation', 'actionableState')
    order = {group: index for index, group in enumerate(SIZE_ORDER)}
    csv_rows = []
    for item in forms:
        building = item['building']
        uid = building['uid']
        size = sizes.get(uid)
        installation = ('embedded' if uid in embedded else
                        'progressive' if uid in official else 'none')
        state = ('installed' if uid in installed else
                 'enhancement-required' if size else 'no-matched-government-source')
        group = size['sizeGroup'] if size else None
        csv_rows.append({
            'uid': uid, 'objectId': building.get('objectId'),
            'buildingCSUID': building.get('buildingCSUID') or (size or {}).get('buildingCSUID'),
            'name': building.get('name', ''), 'nameZh': building.get('zh', ''),
            'sectionId': item['sectionId'], 'sectionName': sections[item['sectionId']]['name'],
            'tile': item['tile'], 'centreX': round(item['centre'][0], 6),
            'centreZ': round(item['centre'][1], 6), 'baseHeight': building.get('base'),
            'height': building.get('height'), 'heightSource': building.get('heightSource'),
            'governmentAvailable': bool(size), 'sizeGroup': group,
            'sizeLabel': SIZE_LABELS.get(group), 'triangles': (size or {}).get('triangles'),
            'modelId': (size or {}).get('modelId'), 'sourceState': (size or {}).get('sourceState'),
            'sourceHoldReason': (size or {}).get('sourceHoldReason'),
            'compressedBytes': (size or {}).get('compressedBytes'),
            'geometryBytes': (size or {}).get('geometryBytes'),
            'installation': installation, 'actionableState': state,
        })
    csv_rows.sort(key=lambda row: (int(row['sectionId'].split('.')[1]),
                                   order.get(row['sizeGroup'], len(order)),
                                   row['actionableState'], row['uid']))
    csv_path = output / 'buildings.csv'
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
        writer.writeheader(); writer.writerows(csv_rows)

    sections_summary = []
    for section_id in SECTION_IDS:
        counts = by_section[section_id]
        available = sum(counts['available'].values())
        ready = sum(counts['installed'].values())
        sections_summary.append({
            'id': section_id, 'name': sections[section_id]['name'],
            'allForms': counts['forms'], 'governmentAvailable': available,
            'installed': ready, 'enhancementRequired': available - ready,
            'noMatchedGovernmentSource': counts['forms'] - available,
            'tiers': [{'sizeGroup': group, 'label': SIZE_LABELS[group],
                       'available': counts['available'][group],
                       'installed': counts['installed'][group],
                       'enhancementRequired': counts['available'][group] - counts['installed'][group]}
                      for group in SIZE_ORDER],
        })
    available = sum(tier['available'] for tier in tiers)
    ready = sum(tier['installed'] for tier in tiers)
    summary = {
        'schemaVersion': 1, 'scope': {'includedSectionIds': list(SECTION_IDS),
        'excluded': ['10.1 Tung Chung town centre and waterfront',
                     '10.2 Tung Chung valley, rural west and North Lantau coast',
                     '10.3 Chek Lap Kok airport', '10.4 Airport east / north',
                     '10.12–10.16 other islands']},
        'allForms': len(forms), 'governmentAvailable': available,
        'installed': ready, 'enhancementRequired': available - ready,
        'noMatchedGovernmentSource': len(forms) - available,
        'installedPercentOfAvailable': ready / available * 100,
        'remainingPercentOfAvailable': (available - ready) / available * 100,
        'territoryFormsVerified': territory_total, 'tiers': tiers,
        'sections': sections_summary, 'governmentSizeRun': RUN_ID,
        'inputs': {str(manifest_path.relative_to(ROOT)): sha256(manifest_path),
                   str(sections_path.relative_to(ROOT)): sha256(sections_path)},
        'installedDefinition': 'UID present in embedded modelGeometry or a manifest-listed official model catalogue',
        'enhancementRequiredDefinition': 'Matched government source UID exists and is not installed',
        'aiCalls': 0, 'databaseWrites': 0, 'queuesCreated': 0, 'geometryChanges': 0,
        'buildingList': 'buildings.csv', 'buildingListSHA256': sha256(csv_path),
    }
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    write_readme(output / 'README.md', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'docs/astra-city/lantau-government-model-inventory-20260914')
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))


if __name__ == '__main__':
    main()
