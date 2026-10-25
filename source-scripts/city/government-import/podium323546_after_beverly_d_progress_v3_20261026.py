"""Checkpoint the private hierarchical terrain and exact original assembly work."""
from pathlib import Path
from run import ROOT, HERE, read, save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-podium323546-after-beverly-d-'
    batch = prefix + 'progress-v3-20261026'
    out = base / batch
    assert not out.exists()
    refs = [Path(__file__)]
    completed = []
    for folder in sorted(base.glob(prefix + '*')):
        if (folder / 'result.json').exists() and '-progress-' not in folder.name:
            receipt, _ = authenticate(folder)
            refs.append(folder / 'result.json')
            completed.append(dict(batch=folder.name, jobId=receipt['jobId']))
    for uid in [210501, 210742]:
        r = read(base / (prefix + f'three-{uid}-foundation-context-v1-20261026') / 'summary.json')
        assert r['establishedFoundationPolicyPassed']
    remaining = [
        'Use hierarchical-group-candidate-v2 and three-original-hierarchical-runtime-v1, not failed additive/narrow candidates. Candidate is a regular grid group, not root-nativeMesh. Explicitly attach the exact replaced old URL/SHA/21 retained targets from the receipt when constructing private staging. Do not expand terrain ownership to companions.',
        'Main strict identity still fails two maximum-extent tests (14.658229m; target coverage99.1745446%). Both companions pass strict identity. Fresh CSUID/BuildingID match, original graph/cell proofs and actually opened official basemap support bounded review, but no source identity approval yet. Fresh provider OBJECTIDs differ from viewer IDs; do not rewrite IDs or invent a common permit/building ownership.',
        'All four worlds preserve31 original transverse contacts with210501 and72 with210742; companions mutually disjoint. Need bounded authored-interface interpretation and close views, not collision-free claims. Original full/base-only diagnostic images and three-source official-map comparison actually opened by ROOT; these are not browser visual approval.',
        'Main foundation passes existing area-fraction policy (.0006444658;7 tiny buried wall triangles;0 upward). Five numerical coverage flags have exact rational closed-facet coverage. All63 affected main walls and4 companion210501 walls have clear-cap paths. Companion210742 has15 rendering negative walls with clear-cap paths plus exactly collinear original primitives311/312 in every mode; raw canonical cap failure preserved. Exact-degenerate receipt14cad590b4190b2c78714b7cfee23ff1326b03c85fdc99854f3544d603f5c200 grants no support/bridge/physical approval.',
        'Whole installed change-scope-v2 authenticates all6959 actual assets/entries and all10 registered BASICsupport footprints: none intersects either changed closed region plus0.5m margin in any mode. All5402 ordinary forms pass final replacement checks. Preserve13 old terrain children/153622 native faces and368131 old grid values. Exact separation is terrain non-effect proof, never reapproval of old models or holds.',
        'Prepare a distinct hierarchical-unaffected staging/admission profile with explicit whole-inventory/non-effect proof and recursive retained-target guards. Keep existing retained-support/publication guards and negativeflags. Guarded publication dry run must precede private browser. All3 new sources need desktop/mobile day/night, picking/collision/joint/failure/retry checks and fresh live exports/readback before installation. Do not grant automatic skip or installation credit.',
        'Counts unchanged382 installed/139 unfinished of fixed521,6959 actors; two null viewer UID source keys remain. No permanent rejection, no human decision needed, no AI geometry modelling/optimisation. Shared4176 stays down. Do not reinstall UniversityHall/D/A/F/E/K. Do not modify frozen producers. Private candidate assets only; no viewer data changes.'
    ]
    result = dict(uids=['landsd/323546:0', 'landsd/210501:0', 'landsd/210742:0'],
                  completed=completed, remainingWork=remaining,
                  supersedesProgressBatch=prefix+'progress-v2-20261026',
                  fullXLCounts=dict(total=521, installedVerified=382, remaining=139),
                  currentNativeActors=6959, newlyInstalled=0, installationApproved=False,
                  publication=False, permanentRejection=False, sourceGeometryChanges=0,
                  heldForHumanDecision=False, heldForAIProcessing=False,
                  heldForComputeAndCode=True, aiGeometryModelling=False, scriptExternalAICalls=0,
                  tests=dict(passed=21, command='python -m unittest test_expand_rendered_terrain_group_v1_20261026 test_hierarchical_original_terrain_binding_v1_20261026 test_hierarchical_group_changed_actor_scope_v1_20261026 test_original_four_world_degenerate_partition_v1_20261026'),
                  status='private-hierarchical-terrain-evidence-complete-source-contact-and-browser-review-pending')
    save(out / 'remaining-work.json', result)
    module('podium_checkpoint', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'explicit-original-source-compute-progress-and-revisit-obligations', refs, result)
    print(dict(completed=len(completed), installedXL=382, unfinishedXL=139, newlyInstalled=0), flush=True)


if __name__ == '__main__':
    main()
