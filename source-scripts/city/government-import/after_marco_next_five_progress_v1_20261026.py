"""Persist completed source checks and explicit remaining work; never acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-marco-next-five-'
    batch = prefix + 'progress-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, completed = [Path(__file__)], []
    for folder in sorted(base.glob(prefix+'*-20261026')):
        if not (folder/'neon-sync.json').exists() or not (folder/'result.json').exists():
            continue
        result, _ = authenticate(folder)
        refs.append(folder/'result.json')
        completed.append(dict(batch=folder.name, jobId=result['jobId']))
    installed = base/'government-xl-marco-polo-original-original-installed-v2-20261026'
    receipt, _ = authenticate(installed)
    counts = dict(total=521, installedVerified=385, remaining=136)
    assert receipt['fullXLCurrentCounts'] == counts and receipt['completeCurrentCatalogueModels'] == 6966
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == receipt['manifest']['sha256']
    refs.extend([installed/'result.json', manifest])
    actions = {
        'landsd/207957:0': 'Strict source identity passes. All36unresolved rim witnesses reach canonical strict support anchors inall4worlds with0endpoint rise. Complete compound proof retains15wall negatives/0nonwalls, raw cap paths remain false. Both private browser widths pass/released;8individual source/retained PNGs still need ROOT inspection. Complete exact wall/interface role review and availability/fallback scope before qualification; no installation credit.',
        'landsd/213579:0': 'All4foundations pass/0burial; complete native scope has0candidates. Full foreign before/after scan retains54positive source contacts with BASIC71329 and every other pair. Next complete4world continuous clearance, exact source identity/extent/overhang and existing BASIC interface review.',
        'landsd/265301:0': 'All10826original faces are covered and0buried against authentic adjacent government terrain, clearing current2757buried/1219upward failures. Private construction still rejects overlapping height surfaces; quantify source overlap before any repair.95current forms/full foreign contacts remain obligations. No existing native terrain candidates in conservative domain; final exact changed-domain regression still mandatory.',
        'landsd/296699:0': 'All4foundations pass established policy with118buried walls/0upward. Full foreign and scope scans complete; next whole-source continuous ground/grade-wall and source-specific identity/extent review. No original geometry edits or corruption claim.',
        'landsd/336667:0': 'All4foundations pass/0burial. Both installed-native pairs have0finite contacts inall4worlds; full external BASIC contacts retained, including322positive contacts with336671. Target coverage and wholeGeoRefcell warnings remain; investigate exact source graph/primary footprint and authentic missing companion coverage before qualification. No automatic partial replacement or permanent rejection.'}
    selection = read(base/(prefix+'ground-v1-20261026')/'selection.json.gz')
    assert {r['uid'] for r in selection['rows']} == set(actions)
    result = dict(uids=sorted(actions), completed=completed, fullXLCounts=counts,
        currentNativeActors=6966, currentManifestSHA256=digest(manifest.read_bytes()),
        priorInstalledCommit='b0adf0f33', priorInstalledJobId=receipt['jobId'],
        rows=[dict(uid=r['uid'], name=r['source']['building'].get('name'), sourceSHA256=r['sourceSHA256'],
                   completeSourceFaces=r['triangles'], status='In process', execution='queued',
                   nextAction=actions[r['uid']], permanentRejection=False, requiresHumanDecision=False,
                   requiresAIGeometryModelling=False, remainingWorkUsesComputeAndCode=True)
              for r in selection['rows']],
        workers=[], newlyInstalled=0, publication=False, installationApproved=False,
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
        scriptExternalAICalls=0,
        qualification='Every referenced worker is terminal with an authenticated completed receipt. Queued continuation is not a live worker claim or a final hold. All136unfinished source keys, including2null viewerUIDs, remain in scope. No new installation, source rejection, optimisation or geometry modelling credit.')
    save(out/'remaining-work.json', result)
    module('after_marco_progress_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'current-five-original-compute-progress-with-full-xl-scope-preserved', refs, result)


if __name__ == '__main__':
    main()
