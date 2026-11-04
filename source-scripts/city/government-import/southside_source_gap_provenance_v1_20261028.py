"""Readonly compression/ZIP category audit; no source geometry or acceptance changes."""
from collections import Counter
import gzip
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent/'enhancement-screening'))
from shape_prepare import canonical_bytes

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-gap-provenance-v1-20261028'
DOC = BASE/BATCH
POSE = BASE/'government-xl-southside-raw-source-pose-parity-v1-20261028'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'
GROUND = BASE/'government-xl-la-marina-southside-original-terrain-v1-20261028'


def main():
    assert not DOC.exists()
    refs, pins = [Path(__file__), HERE.parent/'enhancement-screening/shape_prepare.py'], {}
    for batch in [POSE, CAP, GROUND]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    pose = take(POSE/'summary.json')
    assert pose['allRawWorldPosesMatchPacked']
    assets = {r['uid']: ROOT/r['candidate']['path'] for r in take(CAP/'selection.json.gz')['rows']}
    compression = []
    for row in pose['rows']:
        expected = assets[row['uid']]
        packed = HERE/'local'/POSE.name/'repacked'/(row['repackedSHA256']+'.glb.gz')
        assert digest(expected.read_bytes()) == pins[str(expected.relative_to(ROOT))] == row['indexedSourceSHA256']
        assert digest(packed.read_bytes()) == pins[str(packed.relative_to(ROOT))]
        a, b = expected.read_bytes(), packed.read_bytes()
        canonical = canonical_bytes(b, row['indexedSourceSHA256'])
        assert canonical == a and gzip.decompress(a) == gzip.decompress(b)
        compression.append(dict(uid=row['uid'], originalSHA256=digest(a), repackedSHA256=digest(b),
                                canonicalSHA256=digest(canonical), uncompressedGLBSHA256=digest(gzip.decompress(a)),
                                differingByteOffsets=[i for i, (x, y) in enumerate(zip(a, b)) if x != y],
                                originalGzipOSByte=a[9], repackedGzipOSByte=b[9],
                                uncompressedGLBByteIdentical=True, canonicalExactIndexedAssetMatch=True))
        refs.extend([expected, packed])
    inputs = take(GROUND/'source-inputs.json')['inputs']
    names = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', 'zip-directory.bin', 'source-scripts/city'], cwd=ROOT, text=True).splitlines()
    directories = {}
    for sheet, record in inputs.items():
        sha = record['directory']['directorySHA256']
        for name in names:
            path = ROOT/name
            if sheet in path.parts and digest(path.read_bytes()) == sha:
                directories[sheet] = path
                break
    assert set(directories) == set(inputs), 'Pinned full central directory unavailable; do not infer missing classes'
    acquisition = module('southside_source_gap_archive', HERE.parent/'citywide-native/download.py')
    refs.extend([Path(acquisition.__file__), Path(acquisition.ac.__file__)])
    records = []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for sheet, record in inputs.items():
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (record['cacheKey'],)).fetchone() == (record['resultSHA256'],)
            identifiers = db.execute("SELECT m->>'modelId' FROM astra_modelling.native_stage_results s CROSS JOIN LATERAL jsonb_array_elements(s.result->'models') m WHERE s.cache_key=%s", (record['cacheKey'],)).fetchall()
            ids = {r[0] for r in identifiers}
            path = directories[sheet]
            entries, _ = acquisition.ac.parse_directory(path.read_bytes())
            gltf = [e.filename for e in entries if e.filename.lower().endswith('.gltf')]
            classes = Counter(name.split('/')[0] for name in gltf)
            unindexed = [name for name in gltf if name.upper().startswith('BUILDING/') and Path(name).stem not in ids]
            other = [name for name in gltf if name.split('/')[0].upper() not in ['BUILDING', 'TERRAIN']]
            records.append(dict(sheet=sheet, directory=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())),
                                fullArchiveEntries=len(entries), glTFByTopLevelCategory=dict(classes),
                                nativeUnits=len(ids), unindexedBuildingGlTFEntries=unindexed,
                                otherGeometryEntries=other, nativeResultSHA256=record['resultSHA256']))
            refs.append(path)
    result = dict(uids=pose['uids'], compressionParity=compression, archiveCategoryCensus=records,
                  allFiveCanonicalAssetsMatch=True, allFiveRawWorldPosesMatch=True,
                  unindexedBuildingGeometryCount=sum(len(r['unindexedBuildingGlTFEntries']) for r in records),
                  otherGeometryEntryCount=sum(len(r['otherGeometryEntries']) for r in records),
                  sourceGeometryChanges=0, identityAccepted=False, physicalAccepted=False, installationApproved=False,
                  qualification='Forensic read-only audit. Earlier repacked SHA mismatch is retained in its original receipt and explained by the existing canonical gzip OS-byte rule; uncompressed GLBs and all decoded raw/packed world coordinates match. Full hash-pinned central directories checked for categories and BUILDING glTFs missing from native metadata. Category completeness does not prove structural completeness, approve source gaps, or authorize model translation/remodelling/installation.')
    save(DOC/'summary.json', result)
    module('southside_source_gap_provenance_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'raw-source-pose-compression-and-archive-category-provenance', list(dict.fromkeys(refs)), result)
    print(dict(allCanonicalAssetsMatch=True, unindexedBuildings=result['unindexedBuildingGeometryCount'], otherGeometry=result['otherGeometryEntryCount'],
               categories=[dict(sheet=r['sheet'], categories=r['glTFByTopLevelCategory']) for r in records]), flush=True)


if __name__ == '__main__':
    main()
