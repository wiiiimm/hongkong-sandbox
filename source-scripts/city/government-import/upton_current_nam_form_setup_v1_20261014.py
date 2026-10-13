"""Exact metadata-only post-Nam form merge. No geometry/sampler/DB calls."""
NAM = 'landsd/79099:0'


def merge_current_forms(archived_forms, installed, delta_input, inventory, composition,
                        *, current_manifest, domain):
    old = {r['uid']: r for r in archived_forms}
    assert len(old) == len(archived_forms), 'Duplicate archived form UID'
    assert len(installed) == 6650
    assert set(installed) - set(old) == {NAM}, 'Unknown missing installed form'
    assert delta_input['completeNativeActors'] == composition['completeCurrentNativeActors'] == 6650
    assert composition['completeOldActorsExactlyRebound'] == 6649
    assert delta_input['currentManifest']['sha256'] == composition['currentManifest']['sha256'] == current_manifest
    assert composition['newUID'] == NAM and composition['uptonWholeParentDomain'] == domain
    assert composition['allFourBoundsStrictlyOutsideUptonDomain'] is True
    assert composition['perWorldStrictSeparation'] == [True] * 4
    assert composition['overlapRequiresFullActualStreams'] is False
    assert len(delta_input['rows']) == len(inventory['rows']) == 1
    saved = delta_input['rows'][0]; measured = inventory['rows'][0]
    assert saved['uid'] == measured['uid'] == NAM
    assert saved['rawCurrentEntry'] == installed[NAM], 'Current Nam catalogue entry changed'
    source = saved['source']['sha256']
    assert source == measured['sourceSHA256'] == installed[NAM]['sha256']
    assert saved['completeOriginalPOSITIONProof'] == measured['completeOriginalPOSITIONProof']
    proof = measured['completeOriginalPOSITIONProof']
    assert proof['sourceSHA256'] == source and proof['allOriginalPositionVerticesAccounted']
    assert proof['completeOriginalTriangles'] == installed[NAM]['triangles'] == measured['completeFaces']
    assert proof['completeOriginalPositionVertices'] == measured['completePositionVertices']
    assert measured['wholeUnusedPositionVerticesIncluded'] and measured['sourceFacesOmitted'] == 0
    bounds = [proof['originalWholeSourceBounds'], measured['completeLiteralBounds'],
              measured['completeLeftAssociatedF32Bounds'], measured['completeBalancedF32Bounds']]
    assert bounds == composition['allFourUnusedWorldBounds'], 'Saved complete world bounds changed'
    assert installed[NAM]['worldBounds'] == bounds[0]
    current = delta_input['currentAllNativeSourceForms']
    assert set(installed) <= set(current), 'Current native form census incomplete'
    form = saved['currentBuilding']
    assert form == current[NAM] and form['uid'] == NAM
    for key in ['objectId', 'buildingCSUID']:
        assert form[key] == installed[NAM][key]
    for uid in sorted(set(old) & set(current)):
        assert old[uid] == current[uid], ('Archived form changed', uid)
    result = dict(old); result[NAM] = form
    # This is the formerly failing complete installed UID scan. No missing form
    # is silently treated as a different parent or excluded by catalogue bounds.
    for uid in installed:
        assert result[uid] == current[uid], ('Installed form not exactly current', uid)
    assert len(result) == len(old) + 1
    return dict(currentForms=result, exactCurrentInstalledUIDs=sorted(installed),
                exactNamSource=saved['source'], savedFourWorldBounds=bounds,
                onlyMergedUID=NAM, allOldFormsUnchanged=True,
                namOutsideContextOnly=True, noNewNativeAcceptanceOrGeometryCredit=True)
