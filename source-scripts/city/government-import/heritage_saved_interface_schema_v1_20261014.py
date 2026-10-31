"""Exact saved packet metadata, without geometry arithmetic or role inference."""
MODES={'providerOriginal','literal','leftFloat32','balancedFloat32'}
ORIGINAL_PAIRS={(12150,10),(12150,11),(12151,10),(12346,10),(12347,6),(12347,10),(12348,6),(12349,6)}
def validate_saved_contacts(basic,original):
    assert basic['completeOriginalSourceFaces']==15140 and basic['fullBASICFaces']==24
    assert basic['independentForeignUID']=='landsd/57455:0' and basic['noOwnershipException']
    assert not basic['physicalAccepted']and not original['physicalAccepted']
    assert {r['arithmetic']for r in basic['fourViews']}==MODES and len(basic['fourViews'])==4
    assert {r['arithmetic']for r in original['allFourViews']}==MODES and len(original['allFourViews'])==4
    for row in basic['fourViews']:
        assert row['sourceFaces']==15140 and row['completeBASICFaces']==24
        hits=row['fullFiniteSurfaceContacts']['contacts'];assert len(hits)==14
        assert row['fullFiniteSurfaceContacts']['allPairsExamined']
        _hits(hits)
    for row in original['allFourViews']:
        assert row['completeMuseumFaces']==15140 and row['completeOriginalStarFaces']==91 and row['completeStarBASICFaces']==24
        hits=row['pairs']['Museum-vs-originalStar']['contacts']['contacts'];assert len(hits)==8
        assert {(r['sourceFaceA'],r['sourceFaceB'])for r in hits}==ORIGINAL_PAIRS
        assert row['pairs']['Museum-vs-originalStar']['contacts']['allPairsExamined']
        _hits(hits)
    return dict(savedCurrentBASICCrossingsPerView=14,savedOriginalStarCrossingsPerView=8,allFourModesRetained=True,roleAssigned=False,physicalAccepted=False)
def _hits(hits):
    for h in hits:
        assert h['dimension']==1 and len(h['exactPoints'])==2 and all(len(p)==3 and all(isinstance(v,str)for v in p)for p in h['exactPoints'])
        d=h['crossingDiagnostic'];assert d['classification']=='proper-noncoplanar-triangle-relative-interior-crossing'and d['properTriangleInteriorCrossing']and not d['volumetricCollisionProved']and not d['structuralSupportCredit']
