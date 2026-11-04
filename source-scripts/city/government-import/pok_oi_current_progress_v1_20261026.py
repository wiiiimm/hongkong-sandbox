"""Archive completed source checks and exact remaining actions; no installation credit."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-after-ying-hoi-pok-oi-current-progress-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, jobs, checked = [Path(__file__)], [], {}
    for folder in sorted(base.glob('government-xl-after-ying-hoi-pok-oi-*')):
        if not (folder / 'result.json').exists():
            continue
        receipt, pins = authenticate(folder)
        for path, sha in pins.items():
            assert path not in checked or checked[path] == sha
            if path not in checked:
                assert digest((ROOT / path).read_bytes()) == sha, path
                checked[path] = sha
        refs.append(folder / 'result.json')
        jobs.append(dict(batch=folder.name, jobId=receipt['jobId'], verifiedFiles=len(pins)))
    count = base / 'government-xl-ying-hoi-native-floor-original-v2-original-installed-v1-20261026/full-xl-current-count.json'
    prior, pins = authenticate(count.parent)
    assert digest(count.read_bytes()) == pins[str(count.relative_to(ROOT))]
    counts = read(count)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == counts['manifestSHA256']
    assert counts['counts'] == dict(installedVerified=387, remaining=134, total=521)
    assert len(counts['rows']) == 521 and sum(r.get('uid') is None for r in counts['rows']) == 2
    refs.extend([count, count.parent / 'result.json', manifest])
    viewed = []
    preview = base / 'government-xl-after-ying-hoi-pok-oi-pair-private-preview-v1-20261026'
    for width in [1280, 390]:
        for uid in ['213579', '71329']:
            for time in [1500, 2200]:
                path = preview / str(width) / f'staged-landsd-{uid}-0-{width}-{time}-canvas.png'
                assert digest(path.read_bytes()) == checked[str(path.relative_to(ROOT))]
                refs.append(path); viewed.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    for folder, filename in [
        ('podium-wall-context-v3', 'remaining-cap-walls.png'),
        ('podium-wall-context-v3', 'unexposed-highest-vertex.png'),
        ('care-home-contact-views-v1', 'before-after-contact-context.png'),
        ('pair-interface-views-v1', 'all-original-pair-contacts.png')]:
        path = base / ('government-xl-after-ying-hoi-pok-oi-' + folder + '-20261026') / filename
        assert digest(path.read_bytes()) == checked[str(path.relative_to(ROOT))]
        refs.append(path); viewed.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    result = dict(uids=['landsd/213579:0', 'landsd/71329:0'], completedJobs=jobs,
                  verifiedEvidenceFiles=len(checked), fullXLCurrentCounts=counts['counts'],
                  nullViewerUIDSourceKeysRetained=2, officialDetailedActors=6968,
                  imagesActuallyOpenedByRoot=viewed, newlyInstalled=0,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
                  scriptExternalAICalls=0, sourceEvidenceInterpretationUsedAI=True,
                  observations=[
                      'Both original sources remain uninstalled. Main10794+podium2711=13505 unchanged faces; only main213579 belongs to fixed XL scope.',
                      'Podium exact stored-top metadata one-ULP binding repaired only in an unapproved selection; source bytes/pose/footprint unchanged. Four adversarial binding tests and four closed-bound native-scan branch tests pass.',
                      'Fresh scene checks bind all6968current native bounds. Zero native nominations legitimately omit the native scanner; all12 foreign BASIC pairs remain measured. Main-to-podium BASIC54positivepairs, podium-to-main BASIC154, podium-to-care-home56488 has14positivepairs in every source representation, not4.',
                      'Main20negative walls have clear-cap paths in all4worlds. Podium153negative walls include48withoutcap paths; recursive exact scans prove these are two24-facet separate column-like shells. Both have24direct positive finite current-ground contact pairs perworld; all48highestvertices exposed. RawcapFALSE remains. One separate thin facet2699 lacks an exposed highest vertex; it lies along a lower wall strip and has a clear-cap path. No bounded physical approval yet.',
                      'All238 original pair contacts perworld are transverse surface crossings, no area pairs; source diagram shows lower hospital/podium junctions. Positive geometric role alone does not establish acceptable architectural ownership.',
                      'ROOT actually opened all8day/night desktop/mobile private browser exports plus corrected2wall/ground panels, care-home before/after context and full238pair contact context. Night original is dark; private preview/failure/retry pass does not grant identity or physical approval.',
                      'Original failed native orchestration and pre-binding podium ground attempts remain preserved; completed successors must not be rerun. Wall-viewV1 exporter failed on ragged Matplotlib wire polygons. FrozenV2receipt has distorted second angle due mutated aspect vector; corrected producerV2/outputV3 uses copied aspect and both panels were opened.'
                  ], nextActions=[
                      'Complete exact-source identity and architectural interface review for hospital213579/podium71329 and care-home56488. Preserve raw14m extent proxy,57855projectedoverlap despite zero finitecontacts, and all238transverse source contacts.',
                      'If justified by source evidence, add a narrowly bound exposed-column/ground and thin-wall role review; do not pretend failed cap paths or failed140strict Main-on-podium support probes passed.',
                      'Validate required availability/fallback edge podium71329->hospital213579 separately from physical support. No invented Main->podium support or dependency cycle.',
                      'Only after qualification run canonical fenced installation, fresh staged/live desktop/mobile checks, actually inspect exports, compare all6968oldassets/entries and521rows/globalBASICguards, then commit/push actual installation.',
                      'Continue all134unfinished fixed XL source keys including2nullUIDs. TuenMun/carpark and other pending sources remain active; never reinstall UniversityHall or YingHoi.'
                  ])
    save(out / 'remaining-work.json', result)
    module('pok_oi_progress_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'completed-original-pair-checks-and-current-fixed-xl-continuation', refs, result)
    print(dict(completedJobs=len(jobs), verifiedFiles=len(checked), imagesActuallyOpened=len(viewed)), flush=True)


if __name__ == '__main__':
    main()
