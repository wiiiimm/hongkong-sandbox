"""Persist exact completed batch work and the remaining compute actions after High Court."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-government-court-caribbean-after-airport-'
BATCH = P + 'progress-checkpoint-v1-20261025'


def main():
    out = BASE / BATCH; assert not out.exists()
    installed = BASE / 'government-xl-high-court-original-final-original-installed-v1-20261025'
    receipt, pins = authenticate(installed)
    assert receipt['fullXLCurrentCounts'] == dict(total=521, installedVerified=376, remaining=145)
    assert receipt['installedUids'] == ['landsd/263644:0']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[str(manifest.relative_to(ROOT))]
    refs, phases = [Path(__file__), installed / 'result.json', manifest], []
    for folder in sorted(BASE.glob(P + '*-20261025')):
        if not (folder / 'result.json').exists(): continue
        r, _ = authenticate(folder); refs.append(folder / 'result.json')
        phases.append(dict(batch=folder.name, jobId=r['jobId']))
    result = dict(uids=['landsd/263644:0', 'landsd/290803:0', 'landsd/290981:0'],
        currentFixedXL=receipt['fullXLCurrentCounts'], currentOfficialDetailedActors=6947,
        newlyInstalled=0, installationApproved=False, publication=False, permanentRejection=False,
        sourceGeometryChanges=0, aiGeometryModelling=False, phases=phases,
        currentManifestSHA256=digest(manifest.read_bytes()),
        priorGeometryContextManifestSHA256=read(BASE / (P + 'model-scope-v1-20261025') / 'summary.json')['currentManifestSHA256'],
        historicalSceneAcceptanceTransfers=False,
        recoveredOriginalCompanions=['landsd/196123:0', 'landsd/200057:0', 'landsd/200059:0', 'landsd/34417:0', 'landsd/95518:0'],
        cases=[
            dict(uid='landsd/263644:0', humanState='installed', installedJobId=receipt['jobId'],
                 reason='Exact unchanged original installed separately; no installation credit is created by this checkpoint.'),
            dict(uid='landsd/290803:0', humanState='held-for-compute',
                 completed=['6000face/33changedparent private original-TIN candidate validates.',
                            'Actual renderer has zero whole/upward burial; continuous upward minimum -.081494m.',
                            'All26current form checks completed;6gap regressions preserved.',
                            'Four affected neighbours recovered exactly. Library196123 and200057 strict support all4pass;200059 has7/7finite paths inall4.',
                            'Complete8original source coordinate/identity/pair/support contexts saved.'],
                 remaining=['Repair21approximate coverage residuals with exact residual analysis and bounded seam covers if justified.',
                            'Resolve34417 support/source role and290801/290804 prepared-source absence, or preserve their existing ground/support with a bounded alternative.',
                            'Check unchanged native229481 against any final terrain; no scope exemption.',
                            'Rebind to the post-HighCourt scene, recheck neighbours/source role/identity, preview, qualify and install.'],
                 missingPreparedPrefixes=['landsd/290801:0', 'landsd/290804:0'],
                 providerAbsenceProven=False, humanDecisionRequired=False, aiGeometryModellingRequired=False),
            dict(uid='landsd/290981:0', humanState='held-for-compute',
                 completed=['11712face/26changedparent private original-TIN candidate validates.',
                            'Actual renderer has1buried/0upwardwhole; existing foundation area policy passes.',
                            'All85current neighbour checks completed; only95518gap regression remains.',
                            '95518exact263face companion recovered;157/157finite original-parent paths verified inall4.'],
                 remaining=['Correct continuous upward minimum-.799601m to existing-.5mlimit using bounded original-surface terrain processing, without geometry changes.',
                            'Evaluate the exact95518co-import against corrected terrain and full affected neighbours.',
                            'Rebind post-HighCourt current scene and finish complete source-role/identity/browser/publication checks.'],
                 humanDecisionRequired=False, aiGeometryModellingRequired=False),
        ], observations=[
            'All proof phases listed here are complete immutable historical evidence. High Court installation changed the manifest: recompute or explicitly rebind current obligations before any further publication; do not transfer scene approval.',
            'Three residential OP structures belong only to Caribbean CSUID1281017034P20070123. No structure relation was returned for High Court/TuenMun. A mixed batch summary is not a per-model relationship.',
            'No model is deemed corrupt or permanently noninstallable. Source recovery and terrain processing used deterministic scripts, not AI geometry modelling. No human decision is currently required.'
        ])
    save(out / 'remaining-work.json', result)
    module('government_court_caribbean_checkpoint', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'completed-original-batch-actions-and-revisitable-compute-holds', refs, result)


if __name__ == '__main__': main()
