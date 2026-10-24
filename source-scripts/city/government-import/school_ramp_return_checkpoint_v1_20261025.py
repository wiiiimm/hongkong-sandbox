"""Freeze completed private school work and explicit unapproved follow-up."""
from pathlib import Path
import subprocess
import shutil
from run import ROOT, HERE, read, save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-school-ramp-return-scripted-checkpoint-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'docs/astra-city/government-import/*school*20261025/result.json'], cwd=ROOT, text=True).splitlines()
    phases, refs = [], [Path(__file__)]
    for name in names:
        path = ROOT / name
        result, _ = authenticate(path.parent)
        phases.append(dict(batch=result['batch'], jobId=result['jobId'], status='complete'))
        refs.append(path)
    assert len(phases) == 31
    audit = read(BASE / 'government-xl-school-ramp-return-independent-readback-v1-20261025/summary.json')
    assert audit['passed'] and audit['newTerrainFaces'] == 4425
    out.mkdir()
    for filename in ['xl-ramp-return-tests-v1-20261025.log', 'xl-school-courtyard-panel-context-v1-20261025.log']:
        path = Path('/tmp') / filename
        if path.exists():
            shutil.copyfile(path, out / filename)
    sources = ['bounded_original_ramp_return_v1_20261025.py', 'test_bounded_original_ramp_return_v1_20261025.py', 'selected_original_compound_spatial_v1_20261025.py', 'school_original_courtyard_panel_context_v1_20261025.py', 'school_original_ramp_return_readback_v1_20261025.py', 'school_original_ramp_inset_readback_v1_20261025.py']
    sources += ['school_original_ramp_terrain_inset_v%d_20261025.py' % i for i in range(1, 5)]
    sources += ['school_original_ramp_terrain_return_v5_20261025.py']
    refs += [HERE / name for name in sources]
    notes = '''ROOT inspected exact-source-role-context.png and the operator's original campus photograph. The 64 extent-flagged facets are low curved courtyard features (88.186–88.860m HKPD), consistent with the photographed outdoor theatre. This supports further bounded source-role identity review; it does not yet approve identity or override the generic 10m extent policy. The eight uncapped original vertical faces 10594–10601 form a narrow four-sided vertical assembly. All four runtime streams prove each crosses actual drawn ground and has its highest vertex above every overlapping ground face. Raw missing-cap failures remain; no watertightness, engineering or installation approval is inferred.

The footprint-only ramp cut is a preserved negative: its eight upward ramp conflicts remain at closed edges. V5 extends only the derived terrain minimum ramp plane through a 1m core and 3m return. All eight now pass the unchanged clearance limit; 22 neighbouring forms pass. The independent complete per-parent audit proves 3237 old triangles literally unchanged, 174 changed parent partitions conserved, lowering bounded at 0.960358631m, and outer boundary parent residual below 1.1e-10m. All original model hashes and poses remain unchanged.

Remaining: bounded identity/physical source-role review; original wing-to-podium support context; actual-site terrain visual inspection; qualifying desktop/mobile day/night exports and recovery; guarded publication and independent full readback. The existing single-main-source unapproved preview is not those qualifying exports. Generic spatial result remains false at 11.3078154601m extent despite 99.1936% compound coverage and zero unrelated excess. This checkpoint grants no installation credit.
'''
    (out / 'SOURCE-ROLE-NOTES.md').write_text(notes)
    local = HERE / 'local/government-xl-school-primary-campus-page-v1-20261025'
    from run import digest
    provenance = dict(pageURL='https://www.icsc.org.hk/about-icqm', photographURL='https://static.wixstatic.com/media/880c86_abd7f017a2494061a38617ce3304c859~mv2.jpg', photoSHA256=digest((local / 'operator-school1.jpg').read_bytes()), photoCachePath=str((local / 'operator-school1.jpg').relative_to(ROOT)), actuallyViewed=True, photographDateUnknown=True, publicationOfPhoto=False, identityApproved=False)
    assert provenance['photoSHA256'] == '2ccd920bcdd7f4ea46437ad2281d66e260c46cbcfcd7ae1cd4398f70a6f3edc1'
    save(out / 'primary-photo-provenance.json', provenance)
    result = dict(uids=['landsd/244581:0', 'landsd/244789:0', 'landsd/231606:0'], completedPhases=phases, installedXL=362, unfinishedXL=159, fixedXLSourceKeys=521, officialDetailedActors=6926, privateRampTerrainAuditPassed=True, neighbourFormsPassed=22, sourceEvidenceInterpretationUsedAI=True, newModellingAICalls=0, identityAccepted=False, physicalAcceptance=False, installationApproved=False, remainingReason='Source-role/assembly review and actual qualifying browser acceptance remain; no permanent rejection.', nextStep='Review exact original courtyard extent and eight uncapped grade-crossing panels, preserve raw negatives, complete physical and actual browser evidence before any installation.')
    save(out / 'summary.json', result)
    module('school_return_checkpoint_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'school-original-ramp-return-scripted-progress-checkpoint', refs, result)


if __name__ == '__main__':
    main()
