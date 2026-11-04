"""Read current government ZIP directory for the exact height-conflict source.

No model payload download, model conversion, DB writes or acceptance changes.
"""
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate

sys.path.insert(0, str(HERE.parent / 'citywide-source'))
from discover import scan

BASE = ROOT / 'docs/astra-city/government-import'
OUT = BASE / 'government-xl-elegant-garden-height-source-revision-probe-v1-20261028'


def main():
    assert not OUT.exists(), 'Use completed evidence rather than repeat the probe'
    folder = BASE / 'government-xl-elegant-garden-sixteen-original-updated-runtime-v1-20261028'
    receipt, pins = authenticate(folder)
    selection = folder / 'selection.json.gz'
    assert digest(selection.read_bytes()) == pins[str(selection.relative_to(ROOT))]
    row = next(r for r in read(selection)['rows'] if r['uid'] == 'landsd/224123:0')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        matches = db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',
                             (row['native']['cacheKey'],)).fetchall()
        assert len(matches) == 1
        sheet = matches[0][0]
        prior = db.execute('SELECT result FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1',
                           (sheet,)).fetchone()[0]
    save(OUT / 'prior-directory.json', prior)
    current, reused = scan(dict(SHEETNO=sheet, Format_glTF=prior['sourceURL'],
                                REVISIONDATE=prior['revision']), OUT / 'current-directory', refresh=True)
    # Check every revision of the exact georef/type prefix, retaining ambiguity.
    found = [m for m in current['models'] if m['modelId'][:-1] == row['modelId'][:-1]]
    exact = [m for m in found if m['modelId'] == row['modelId']]
    old = [m for m in prior['models'] if m['modelId'] == row['modelId']]
    assert len(old) == 1
    unchanged = len(exact) == 1 and exact[0]['members'] == old[0]['members']
    save(OUT / 'summary.json', dict(
        uid=row['uid'], sourceSHA256=row['sourceSHA256'], modelId=row['modelId'],
        sourceReceiptJob=receipt['jobId'], sheet=sheet, currentCandidates=found,
        priorExactModel=old[0], exactDirectoryMembersUnchanged=unchanged,
        sameArchiveETag=current['etag'] == prior['etag'], directoryReused=reused,
        receivedDirectoryBytes=current['receivedBytes'], nativeModelPayloadsDownloaded=0,
        sourceGraphRevalidated=False, sourceHeightConflictResolved=False,
        qualification='Current exact source-directory membership/CRC/size/offset comparison only. Unchanged ZIP metadata is not a fresh payload hash or an independent elevation survey. No missing/corrupt/new-revision conclusion is inferred from ambiguous candidates.',
        sourceGeometryChanges=0, neonWrites=0, installationApproved=False, publication=False))
    print(dict(sheet=sheet, candidates=len(found), exactDirectoryMembersUnchanged=unchanged,
               sameArchiveETag=current['etag'] == prior['etag'], payloadDownloads=0))


if __name__ == '__main__':
    main()
