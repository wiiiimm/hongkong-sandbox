"""Persist current Fung Yip progress without granting installation credit."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-fung-yip-after-inone-'
BATCH = PREFIX + 'progress-checkpoint-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    names = sorted(p.name for p in BASE.glob(PREFIX + '*')
                   if p.is_dir() and (p / 'result.json').exists())
    names += ['government-xl-fung-yip-independent-permit-identity-review-v1-20261025']
    names += [f'government-xl-fung-yip-{uid}-after-inone-seam-foundations-v2-20261025'
              for uid in ['254815', '79883']]
    refs = [Path(__file__)]
    phases = []
    for name in names:
        receipt, pins = authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
        outputs = []
        for path, sha in pins.items():
            p = ROOT / path
            if p.is_relative_to(BASE / name):
                assert digest(p.read_bytes()) == sha
                refs.append(p)
                outputs.append(path)
        phases.append(dict(batch=name, jobId=receipt['jobId'],
                           frozenOwnOutputsRehashed=len(outputs)))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == 'f31c749ca4c2f3c55c29cc71d8eaacf956a5e80376afb6541801daa4167a6403'
    refs.append(manifest)
    result = dict(
        uids=['landsd/254815:0', 'landsd/79883:0'], completedPhases=phases,
        installedXL=369, unfinishedXL=152, fixedXLTotal=521,
        officialDetailedActors=6936, newlyInstalled=0,
        sourceGeometryChanges=0, sourcePoseChanges=0,
        aiGeometryModelling=False, installationApproved=False,
        currentManifestSHA256=digest(manifest.read_bytes()),
        humanStatus='In process',
        progress=[
            'Independent exact H234/75 two-structure identity accepted; the 4.927408mm boundary counterexample and raw overlap failures remain archived.',
            'Private derived terrain retains every prior 16351 triangle and adds 2067 bounded Float32 seam covers. Complete 10573-face exact coverage passes.',
            'Current 56-form and all three retained-native regressions pass. Complete four-world actual-ground checks pass for the tower; eight podium wall negatives have checked finite cap paths.',
            'Complete renderer attribute rows equal the earlier source-only contact proof. Its strict failure remains false; all 32 unresolved probes have finite original-source paths in all four streams.',
            'All 20 V3 private exports actually inspected. Near-overhead retained 79882 is assessable, but mobile source 79883 and retained 12728 remain foreground-occluded. V4 changes only those two camera directions; no visual acceptance is granted here.'
        ],
        remainingWork=[
            'Observe V4 browser worker completion and lease release; inspect its actual day/night desktop/mobile exports. Never infer approval from active/frustum metadata.',
            'Finish bounded physical/source-role interpretation, preserving the two tower returns under the higher original podium roof rather than claiming exposed highest vertices.',
            'Use an additive support-aware retained-terrain installation adapter that requires no installed metadata migration. Do not remove independent-source guards, fabricate a support migration or omit the real tower-to-podium dependency.',
            'Qualified dry-run, qualification commit/push, guarded installation, fresh live exports and independent full inventory/support readback remain necessary before any installation credit.'
        ])
    save(out / 'remaining-work.json', result)
    module('fung_current_checkpoint', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'current-original-model-progress-no-installation-credit',
        list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
