"""Scoped one-parent/five-member terrain staging; never grants model acceptance.

The ordinary publisher retains asset, grid, overlap, budget, global support,
input-pinning, transaction and rollback checks. Only its one-to-one replacement
extent condition is replaced by the exact complete five-member union contract.
No production entry point installs this adapter yet.
"""
import copy
from pathlib import Path
from contextlib import contextmanager
import fuying_whole_parent_five_boundary_v1_20261029 as boundary
import three_member_native_boundary_v1_20261027 as three
OLD_URL='city/data/government-native-fu-wong-original-v1-20261023.json'
NEIGHBOURS={'landsd/262871:0','landsd/282088:0','landsd/51764:0','landsd/161931:0','landsd/120158:0','landsd/244683:0','landsd/147589:0','landsd/51275:0','landsd/50662:0'}

def verify_review(review, manifest_ref, proof_ref, entries):
    assert review['status']=='approved-for-five-member-terrain-staging'
    assert review['currentManifest']==manifest_ref and review['wholeParentContract']==proof_ref
    assert review['supersededURL']==OLD_URL and review['supersededSHA256']==boundary.OLD_SHA
    assert review['sourceGeometryChanges']==review['sourcePoseChanges']==0
    assert review['derivedTerrainConnectorFacetsAdded']==39 and review['allPriorTerrainPositionsAndIndicesPreserved']is True
    assert review['allSixFourWorldFoundationsPassed']is True
    assert review['all40FormsAnd9NativeRegressionsPassed']is True
    rows=review['retainedNativeRows'];assert len(rows)==9 and {r['uid']for r in rows}==NEIGHBOURS
    for row in rows:
        assert row['passed']is True
        assert row['terrain']['newlyWhollyBuried']==row['terrain']['newlyUpwardWhollyBuried']==0
    assert review['all40PrivateExportsActuallyViewed']is True
    expected=review['replacementSources'];assert len(expected)==5
    assert len(entries)==5 and len({e['source']for e in entries})==len({e['destination']for e in entries})==5
    assert {e['source']:e['sha256']for e in entries}==expected
    assert not any(e.get('replaces')or e.get('reviewedChanges')or e.get('nativeReview')for e in entries)
    # Terrain approval is deliberately insufficient to approve a building.
    assert review['modelInstallationApproved']is False

@contextmanager
def complete_boundary_validators():
    """Keep both previously installed chains and the new five-member group strict."""
    legacy=boundary.legacy
    old_boundary,old_effective=legacy.coordinated_boundary,legacy.validate_effective_coordinated_members
    assert old_boundary is boundary.BOUNDARY is three.PAIR_BOUNDARY
    assert old_effective is boundary.EFFECTIVE is three.PAIR_EFFECTIVE
    def dispatch(node,parent):
        own=boundary.marker(node)
        return boundary.coordinated_boundary(node,parent)if own and own.get('policy')==boundary.POLICY else three.coordinated_boundary(node,parent)
    def effective(nodes):
        # Each contract sees all ordinary terrain and all its own exact members.
        # Other-policy groups are checked by their original verifier, never ignored.
        three.validate_effective_coordinated_members([n for n in nodes if not boundary.marker(n)or boundary.marker(n).get('policy')!=boundary.POLICY])
        # The five-member old-parent identity check consumes native bodies only.
        # All grid patches still pass the unchanged canonical verifier above.
        boundary.validate_effective_coordinated_members([n for n in nodes if n.get('nativeMesh')and (not boundary.marker(n)or boundary.marker(n).get('policy')!=three.POLICY)])
    legacy.coordinated_boundary=dispatch;legacy.validate_effective_coordinated_members=effective
    try:yield
    finally:legacy.coordinated_boundary=old_boundary;legacy.validate_effective_coordinated_members=old_effective

@contextmanager
def publication_adapter(pub):
    ordinary=pub.stage_top_level_terrain
    def stage(plan,original,manifest,edits,report):
        group=plan.get('fuYingWholeNativeTerrainReplacement')
        if group is None:return ordinary(plan,original,manifest,edits,report)
        assert set(group)=={'proof','review'}
        def pinned(ref,parse=True):
            assert set(ref)=={'path','sha256'}
            path=(pub.ROOT/ref['path']).resolve();assert path.is_relative_to(pub.ROOT.resolve())
            assert pub.sha(path)==ref['sha256'];return pub.load(path)if parse else None
        proof=pinned(group['proof']);review=pinned(group['review'])
        # Pin every dependency before the existing publisher's verify_inputs.
        pinned(proof['parent']);pinned(proof['oldNative'])
        for item in proof['members'].values():pinned(item['candidate'])
        contract,members,_=boundary.load(group['proof'],pub.load(pub.ROOT/'3d-viewer/city/data/terrain.json'))
        assert contract==proof and proof['oldNative']==dict(path='3d-viewer/'+OLD_URL,sha256=boundary.OLD_SHA)
        manifest_ref=dict(path='3d-viewer/city/data/manifest.json',sha256=pub.sha(pub.ROOT/'3d-viewer/city/data/manifest.json'))
        verify_review(review,manifest_ref,group['proof'],plan['topLevelTerrainPatches'])
        for ref in review['evidenceFiles']:pinned(ref,parse=False)
        old_entries=[m for m in original['terrainPatches']if m['url']==OLD_URL];assert len(old_entries)==1
        old=pinned(proof['oldNative']);assert not old.get('hydro')
        assert set(old['meta']['targetUids'])<=set(proof['targetUids'])
        nodes=[pub.load(pub.ROOT/e['source'])for e in plan['topLevelTerrainPatches']]
        for node in nodes:
            own=boundary.marker(node);assert own and own['proof']==group['proof']and own['policy']==boundary.POLICY
            assert own['member']in members
            assert boundary.legacy.canonical_sha(node)==proof['members'][own['member']]['canonicalSHA256']
        boundary.validate_effective_coordinated_members(nodes)
        # Stage on copies: an exception cannot leave half a group in shared edits.
        logical_original=copy.deepcopy(original)
        logical_original['terrainPatches']=[m for m in original['terrainPatches']if m['url']!=OLD_URL]
        staged_manifest=copy.deepcopy(manifest)
        assert staged_manifest['terrainPatches']==original['terrainPatches']
        staged_manifest['terrainPatches']=copy.deepcopy(logical_original['terrainPatches'])
        staged_edits=edits.copy();staged_report=copy.deepcopy(report)
        ordinary(plan,logical_original,staged_manifest,staged_edits,staged_report)
        assert [m for m in staged_manifest['terrainPatches']if m['url']not in {e['destination']for e in plan['topLevelTerrainPatches']}]==logical_original['terrainPatches']
        staged_report['replacedTerrainPatches']=[dict(url=OLD_URL,sha256=boundary.OLD_SHA,oldAssetRetained=True,wholeNativeReplacementMembers=5)]
        manifest.clear();manifest.update(staged_manifest)
        edits.clear();edits.update(staged_edits)
        report.clear();report.update(staged_report)
    assert not hasattr(pub,'_fu_ying_group_adapter_active')
    pub._fu_ying_group_adapter_active=True;pub.stage_top_level_terrain=stage
    try:
        with complete_boundary_validators():yield
    finally:
        pub.stage_top_level_terrain=ordinary;del pub._fu_ying_group_adapter_active
