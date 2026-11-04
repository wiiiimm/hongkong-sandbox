"""Preserve current original-model progress, failures and next actions in Neon."""
import gzip
import shutil
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    out = base / 'government-xl-oceanwalk-depot-recovery-checkpoint-v1-20261029'
    assert not out.exists()
    out.mkdir()
    prefixes = ['government-xl-after-unnamed265269-native-bounds-v1-20261029',
                'government-xl-oceanwalk', 'government-xl-depot120104',
                'government-xl-immutable-cache-storage-consolidation-v1-20261029']
    refs, receipts = [Path(__file__)], []
    for directory in sorted(base.iterdir()):
        if directory == out or '20261029' not in directory.name or not any(directory.name.startswith(p) for p in prefixes):
            continue
        path = directory / 'result.json'
        if path.exists():
            receipt, _ = authenticate(directory)
            receipts.append(dict(batch=directory.name, jobId=receipt['jobId'], path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
            refs.append(path)
    logs = ['astra-oceanwalk-conditional-lower-rims-20261029.log',
            'astra-oceanwalk-conditional-lower-rims-v2-20261029.log',
            'astra-oceanwalk-neighbour-cached-selection-20261029.log',
            'astra-oceanwalk-neighbour-restore-20261029.log',
            'astra-oceanwalk-neighbour-restore-retry-20261029.log',
            'astra-depot-land-inset-construction-20261029.log',
            'astra-depot-land-inset-construction-v2-20261029.log']
    for name in logs:
        source = Path('/tmp') / name
        assert source.is_file()
        destination = out / 'failed-attempts' / name
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, destination)
        refs.append(destination)
    archives = []
    raw = base / 'government-xl-oceanwalk81743-current-rims-v1-20261029'
    for name in ['result.json', 'summary.json']:
        source = raw / name
        target = out / (raw.name + '-' + name + '.gz')
        with source.open('rb') as stream, target.open('xb') as packed:
            with gzip.GzipFile(fileobj=packed, mode='wb', mtime=0) as compressed:
                shutil.copyfileobj(stream, compressed)
        assert digest(gzip.decompress(target.read_bytes())) == digest(source.read_bytes())
        archives.append(dict(sourcePath=str(source.relative_to(ROOT)), sourceSHA256=digest(source.read_bytes()), archivePath=str(target.relative_to(ROOT)), archiveSHA256=digest(target.read_bytes())))
        refs.append(target)
    result = dict(uids=['landsd/81743:0', 'landsd/120104:0', 'landsd/32653:0'],
                  installedXL=403, exactCurrentSourceTerminalXL=3, outstandingXL=115, fixedXLCohort=521,
                  uniqueDetailedActors=7018, newlyInstalledThisCheckpoint=0,
                  completedReceipts=receipts, losslessEvidenceArchives=archives,
                  heldReasons={
                      'landsd/81743:0': 'Conditional lower-rim accounting passes all four coordinate representations. Source-role interpretation, complete foreign-contact resolution and browser acceptance remain. An unrelated BASIC neighbour32653 needs exact native comparison; its prepared original is identified but asset bytes are absent locally.',
                      'landsd/32653:0': 'Exact60-face original and1523-byte prepared asset identified in pinned native result; immutable12.35MB R2 source bundle identified. Restore first failed on missing boto3 (now installed), then missing R2 configuration. No source corruption or identity rejection is inferred. Credential location requested; no secrets exposed.',
                      'landsd/120104:0': 'Original cached TIN covers all14623source facets. Three domains preserve19600m2 absent coastal water. Global7117-face private construction passes ordinary per-member coverage, both full finite rendered seams and four-world zero-buried-face diagnostics. Existing conservative low-parent precheck fails because nominal edit envelope touches14low facets; independent inspection shows all14remain byte-identical and none are changed parents. A strict actual-lineage proof, canonical native-patch validation, actual renderer, canopies/neighbours and browser checks remain.'},
                  failedAttemptsAreNotTerminalSourceRejections=True,
                  sourceGeometryChanges=0, aiGeometryModelling=False,
                  installationApproved=False, publication=False,
                  qualification='Original-model acquisition/acceptance remains separate from optimisation. Full521-source cohort and both NULL-UID keys remain in scope. Earlier local assumption/code/environment failures are preserved, not promoted to model corruption or acceptance. All production guards remain unchanged. UniversityHall93417 is already installed and must not be installed again.')
    save(out / 'summary.json', result)
    module('oceanwalk_depot_checkpoint_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name, 'original-model-recovery-progress-and-explicit-hold-reasons', refs, result)


if __name__ == '__main__':
    main()
