"""Authenticate the cached next XL source and locate its old constructor failure."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-passenger162768-cached-failure-context-v1-20261030'
UID = 'landsd/162768:0'


def main():
    out = BASE/BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, filename):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE/batch)
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take('government-xl-remaining-195-current-scene-batch-v1-20261022-chunk-01-selection','selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    asset = ROOT/row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == '8df09bfde9d69f09ccbec06f7c45cff3d0095d209616b49917465428f89a3c14'
    refs.append(asset)
    failed = 'government-xl-first-ten-recovered-current-followthrough-v1-20261022-candidates-162768-0-terrain'
    failure = take(failed,'failure.json')
    assert failure['message'] == 'native-terrain-near-water-clamp'
    assert 'baseline, [], parent_sha256' in failure['traceback']
    scope = take(failed,'scope.json')
    terrain = take('government-xl-remaining-adjacent-terrain-batch-v1-20261022-162768-0','summary.json')
    original = terrain['rows'][0]
    assert original['uid'] == UID and original['sourceSHA256'] == row['sourceSHA256']
    foundation = original['originalTerrainFoundation']
    assert foundation['completeTerrainTriangles'] == foundation['triangles'] == row['triangles'] == 32238
    assert foundation['fullyBuriedTriangles'] == foundation['fullyBuriedUpwardTriangles'] == 0
    result = dict(uids=[UID], sourceSHA256=row['sourceSHA256'], cachedAsset=str(asset.relative_to(ROOT)),
                  sourceName=row['source']['building']['name'], sourceModelId=row['modelId'], originalFaces=32238,
                  historicalScope=scope, cachedGovernmentTerrainPaths=original['sourceTerrainPaths'],
                  historicalOriginalTerrainFoundation=foundation, currentSceneAcceptanceTransferred=False,
                  existingParentTemplateClampFailure=True, permanentRejection=False, sourceGeometryChanges=0,
                  nextStep='After current civic installation/readback, refresh full native bounds and capture this exact cached source against the current scene. Use bounded retention of existing low coastal parent surfaces, not a global clamp exemption or new water fill.',
                  qualification='The authenticated old traceback fails while constructing the current-parent baseline template, before government TIN contributions. This is not evidence of corrupt source geometry. The historical native-terrain foundation and two cached terrain-sheet paths are provenance only; no current placement, identity, runtime or publication acceptance transfers.')
    save(out/'summary.json',result)
    module('passenger_cached_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'cached-passenger-source-and-parent-clamp-failure-location',refs,result)


if __name__ == '__main__':
    main()
