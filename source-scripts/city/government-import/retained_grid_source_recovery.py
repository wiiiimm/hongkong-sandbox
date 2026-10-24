"""Resolve legacy terrain references only to byte-identical original source files.

Published grid heights and model geometry are never reconstructed or changed.
An absent historical cache path can be replaced in diagnostic provenance only
when a complete original directory receipt proves the same filename and SHA.
"""
import hashlib
import json


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_files(patch, root, here):
    assert not patch.get('nativeMesh') and not patch.get('patches')
    assert patch.get('renderedElev'), 'Drawn legacy grid is required'
    refs, resolutions, derived = [], [], {}
    for source in patch['meta']['source']['nativeSources']:
        declared = source.get('sourceFiles', source.get('files'))
        assert declared and any(r['path'].endswith('.gltf') for r in declared)
        for original in declared:
            historical = root / original['path']
            candidates = []
            if historical.is_file() and sha(historical) == original['sha256']:
                candidates.append((historical, None))
            else:
                for folder in sorted((here / 'local').glob('*/sheets/' + source['sheet'])):
                    receipt_path = folder / 'original/download.json'
                    directory_path = folder / 'directory/result.json'
                    if not receipt_path.is_file() or not directory_path.is_file():
                        continue
                    receipt = json.loads(receipt_path.read_text())
                    directory = json.loads(directory_path.read_text())
                    if not (receipt.get('terrainGeometryIncluded')
                            and receipt['directorySHA256'] == directory['directorySHA256']
                            and receipt['sheet'] == directory['sheet'] == source['sheet']):
                        continue
                    entries = [e for e in receipt['entries'] if e['name'].startswith('TERRAIN')
                               and e['name'].endswith(('.gltf', '.bin'))]
                    if not entries or not all((folder / 'terrain' / e['name']).is_file()
                            and sha(folder / 'terrain' / e['name']) == e['sha256'] for e in entries):
                        continue
                    for entry in entries:
                        path = folder / 'terrain' / entry['name']
                        if path.name == historical.name and entry['sha256'] == original['sha256']:
                            candidates.append((path, [receipt_path, directory_path]))
                        elif path.suffix == '.gltf' and historical.name == path.stem + '-geometry.gltf':
                            # Reproduce the unchanged historic photo-free wrapper.
                            # Exact expected SHA is mandatory, including node poses,
                            # accessors, buffers, winding and retained material facts.
                            data = json.loads(path.read_text())
                            for key in ('images', 'textures', 'samplers'):
                                data.pop(key, None)
                            for material in data.get('materials', []):
                                material.get('pbrMetallicRoughness', {}).pop('baseColorTexture', None)
                                for key in ('normalTexture', 'occlusionTexture', 'emissiveTexture'):
                                    material.pop(key, None)
                            raw = json.dumps(data, separators=(',', ':')).encode()
                            if hashlib.sha256(raw).hexdigest() != original['sha256']:
                                continue
                            target = path.with_name(historical.name)
                            if target.exists():
                                assert target.read_bytes() == raw, 'Existing derived wrapper differs'
                            else:
                                target.write_bytes(raw)
                            derived[str(target)] = {'original': {'path': str(path.relative_to(root)),
                                'sha256': entry['sha256']}, 'method': 'historic-photo-free-json-wrapper',
                                'geometryChanges': 0, 'expectedDerivedSHA256': original['sha256']}
                            candidates.append((target, [receipt_path, directory_path]))
            assert candidates, ('Missing exact original legacy terrain file', original['path'])
            path, receipts = candidates[0]
            assert path.resolve().is_relative_to(root.resolve()) and sha(path) == original['sha256']
            current = {'path': str(path.relative_to(root)), 'sha256': original['sha256']}
            if current not in refs:
                refs.append(current)
            resolutions.append({'historical': original, 'resolved': current,
                'receiptRefs': [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in receipts or []],
                'byteIdentical': True, 'derivedWrapper': derived.get(str(path))})
    return refs, {'rows': resolutions, 'implementation': {'path': str(__import__('pathlib').Path(__file__).relative_to(root)), 'sha256': sha(__import__('pathlib').Path(__file__))}, 'publishedGridChanges': 0, 'modelGeometryChanges': 0,
                  'publication': False, 'qualification': 'Exact source-byte references only. '
                  'Retained drawn facets and all physical/neighbour checks remain mandatory.'}
