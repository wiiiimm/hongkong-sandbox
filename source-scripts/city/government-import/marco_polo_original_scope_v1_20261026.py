"""Closed admission for one reviewed independent original; no global guard changes."""
SOURCES = {'landsd/215934:0': '2bafbc4db86031469ade9828d8f7701f9c8caa0d4d0975f522650d4b34c6166f'}
NATIVE_COUNTS = {'landsd/205767:0': 103, 'landsd/210032:0': 0, 'landsd/33396:0': 0, 'landsd/231484:0': 60}


def verify_entry(entry, sources):
    assert sources == SOURCES
    assert entry['uid'] in SOURCES and entry['sha256'] == SOURCES[entry['uid']]
    assert entry['triangles'] == 10432 and entry['rootTranslation'] == [-834500, 0, 816500]
    assert entry.get('verticalPlacementOffsetHKPD', 0) == 0 and entry['proceduralWindows'] is False
    for key in ['supportDependencies', 'retainedBasicSupportDependencies', 'suppressesBuildingUids']:
        assert key not in entry or entry[key] == []
    assert not any(entry.get(k) for k in ['footprintScope', 'embeddedGeometry', 'sourceWorldBounds',
        'partialSource', 'partialGeometry', 'embeddedModel', 'embeddedModels', 'renderGroups'])
    return True


def verify_review(review):
    assert review['sourceSHA256ByUid'] == SOURCES
    assert all(review[k] is True for k in ['identityAccepted', 'sourceSpecificPhysicalInterpretationAccepted',
        'completeNeighbourInterpretationAccepted', 'qualifiedFourWorldSourceClearance', 'visualAcceptance'])
    assert review['completeCurrentNeighbourChecks'] == 10
    assert review['supportByUid'] == review['runtimeAvailabilityDependenciesByUid'] == {}
    assert review['retainedBasicSupportDependencies'] == review['retainedCurrentBasicSupportUids'] == []
    assert review['terrainEdits'] is False and review['sourceGeometryChanges'] == review['sourcePoseChanges'] == 0
    assert all(review['identityProof'][k] is True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted'])
    assert len(review['imagesActuallyViewed']) == 4 and len(review['retainedImagesActuallyViewed']) == 16
    assert len({r['path'] for r in review['imagesActuallyViewed'] + review['retainedImagesActuallyViewed']}) == 20
    assert len(review['browserReports']) == 2 and len(set(review['leaseResources'])) == len(review['leaseResources']) == 10
    rows = review['rawNativeContacts']
    assert len(rows) == 4 and {r['nativeUid'] for r in rows} == set(NATIVE_COUNTS)
    assert set(review['retainedNativeEntries']) == set(NATIVE_COUNTS)
    for row in rows:
        assert row['uid'] in SOURCES and row['sourceSHA256'] == SOURCES[row['uid']]
        assert row['rawCurrentNativeEntry'] == review['retainedNativeEntries'][row['nativeUid']]
        assert len(row['modes']) == 4 and {m['mode'] for m in row['modes']} == {'original', 'literal', 'leftF32', 'balancedF32'}
        for mode in row['modes']:
            assert mode['finiteContactPairs'] == mode['positiveSurfaceContactPairs'] == NATIVE_COUNTS[row['nativeUid']]
            assert mode['areaContactPairs'] == 0
    return True
