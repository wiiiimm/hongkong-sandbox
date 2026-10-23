"""One exact four-original identity review; no physical/publication exemption."""
EXACT={
 'landsd/20270:0':('B348962051701063C0','3489620517T20050430','e316585684d178e790090952fb45d79cf9086e94e1794c9f78bcd3cde3cfe392',11166,'K28/80'),
 'landsd/159422:0':('B348962051702063C0','3489620517P20060311','c7136606802804b406b90d5ca533abff624eb23b17533af660731fa40211951f',537,'K28/80'),
 'landsd/269430:0':('B348842052602063C0','3488420526P20060311','e8691c307347bdb654345e3ab9ed87813130977d1c06ba8ab12b09d2336d7bd7',1785,'K42/90'),
 'landsd/274231:0':('B348872049701063C0','3488720497T20050430','32386380aa6ed4f923b6107a22d06d1a6d09cccd5a66595eddd7478ee65d60de',360,'K42/90'),
}
FOREIGN={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}


def validate_named_boundary_contract(boundary,family,coinstalled):
    wanted={uid:r[2]for uid,r in EXACT.items()}
    assert coinstalled==wanted and boundary['sourceSHA256ByUid']==wanted,'All four exact reviewed originals must be co-installed'
    assert boundary['all774CurrentFormsRetained']is True and family['all774CurrentFormsRetained']is True
    assert boundary['completeOriginalFaces']==13848
    assert {r['uid']for r in family['foreignExcessOverlaps']}=={'landsd/269430:0'},'No additional foreign form may be reclassified'
    assert 0<boundary['foreignOverlapM2']<=4.431318
    assert boundary['foreignFootprintBoundaryDistance']['upperM']<=.358082 and boundary['familyFootprintBoundaryDistance']['upperM']<=.413410
    assert family['familyProjectionQualified']is True and family['wholeFamilyCurrentTargetCoverage']>=.95 and family['maximumFullFamilyExtentM']<=10
    assert family['coInstallationRequired']=={u:wanted[u]for u in ['landsd/20270:0','landsd/159422:0']}
    assert all(p['exactProjectionCovered']for p in family['exactWholeGeoRefCellProofs'])and len(family['exactWholeGeoRefCellProofs'])==2
    assert {r['uid']for r in boundary['rows']}=={'landsd/20270:0','landsd/159422:0'}
    for r in boundary['rows']:assert r['otherUid']=='landsd/269430:0'and r['allExactPairsExamined']is True
