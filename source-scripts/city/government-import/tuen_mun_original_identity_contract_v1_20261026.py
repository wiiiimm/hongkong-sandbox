"""Closed exact-original hospital compound identity only; no physical approval."""
from copy import deepcopy

SOURCES = {'landsd/336667:0': {'sourceSHA256': '7d65f623fafccf51590c7dab2c1cb7238560b53ea98510cf89d11aced7b93e66', 'modelId': 'B156072976701063C0', 'buildingCSUID': '1560729767T20080513', 'objectId': 336667, 'triangles': 10835}, 'landsd/193881:0': {'sourceSHA256': 'cdf55cb832a195f626d7268a884e5910740bb89087f2093414347638b2503c0d', 'modelId': 'B156162982801063C0', 'buildingCSUID': '1561629828T20060307', 'objectId': 193881, 'triangles': 332}, 'landsd/280350:0': {'sourceSHA256': '851ae2f02fe2499f10c8514b08be8bb9e2e73afa243488c5dc0e0c6ea7acb261', 'modelId': 'B156122977802063C0', 'buildingCSUID': '1561229778P20210726', 'objectId': 280350, 'triangles': 13121}, 'landsd/336668:0': {'sourceSHA256': '3343e6a5e89851f07e57406d66052c354f8302f3b85141fb22361c831f543d51', 'modelId': 'B155952981701063C0', 'buildingCSUID': '1559529817T20080515', 'objectId': 336668, 'triangles': 7306}, 'landsd/336669:0': {'sourceSHA256': '94541559f112cf9e8128b253d51fe76cd323232666a3a01c8086451bd454b4f7', 'modelId': 'B156332976101063C0', 'buildingCSUID': '1563329761T20080515', 'objectId': 336669, 'triangles': 6586}, 'landsd/336670:0': {'sourceSHA256': 'e0a5e5b0e9c4538a5955ca6ba79d11058104db720d333034392baf5dfed0161d', 'modelId': 'B155832977501063C0', 'buildingCSUID': '1558329775T20080515', 'objectId': 336670, 'triangles': 8033}, 'landsd/336671:0': {'sourceSHA256': '856ed756efff8258e923479f149708d9c6a5a3a41bcd86db38587c19134b18c0', 'modelId': 'B156452980301063C0', 'buildingCSUID': '1564529803T20080515', 'objectId': 336671, 'triangles': 6497}, 'landsd/336672:0': {'sourceSHA256': '996bc01f4444457c619e8725e2e2fa47c27c7f3e110613813e6d8488300e4b04', 'modelId': 'B155982972901063C0', 'buildingCSUID': '1559829729T20080515', 'objectId': 336672, 'triangles': 6272}, 'landsd/198266:0': {'sourceSHA256': 'c4595b2de8da26b6ec2eab840bc888b582ef70a7b4f911e2354425e60314d9ac', 'modelId': 'B155722969201063C0', 'buildingCSUID': '1557229692T20080513', 'objectId': 198266, 'triangles': 3186}, 'landsd/199375:0': {'sourceSHA256': '4a1adc1bcdbedefed3f8daf751d61858134c93be19d13857f227b97646cfbe70', 'modelId': 'B156012987501063C0', 'buildingCSUID': '1560129875T20080515', 'objectId': 199375, 'triangles': 82}, 'landsd/323118:0': {'sourceSHA256': 'd1802ce18f3a2bfeffa469d5521b913e61d961e94435b0b946db79fb27acaa57', 'modelId': 'B155692973501063C0', 'buildingCSUID': '1556929735T20210726', 'objectId': 323118, 'triangles': 4072}, 'landsd/6629:0': {'sourceSHA256': 'bdb8752d4daef2ba713d07846d291d000098fce3899ea5e654d2deeefa6f4f05', 'modelId': 'B155412978401062G0', 'buildingCSUID': '1554129784T20060106', 'objectId': 6629, 'triangles': 549}}
OWNER = {'official-site-plan-20150518.pdf': '2e116361db0aedfd829811f6d4978b5b9f6d4196957f23c8318012e3fa8d3fe7', 'official-hospital-about.html': '781a5a371ff67695977a8d44061834ed1268aa743b629363907522e66ebb3f52'}
MAIN='landsd/336667:0'
CELL_PROVIDER='landsd/336670:0'
RELATED_NATIVE='landsd/191896:0'
OVERRIDABLE={
    'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',
    'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM',
    'fresh-current-spatial-bound:targetCoveredBySourceProjection',
    'full-source-maximum-extent','full-source-target-coverage','full-source-unrelated-overlap',
    'original-source-does-not-cover-whole-georef-cell',
}


def verify(rows, identities, spatial, cell, dependency, owner_hashes):
    by={r['uid']:r for r in rows}
    assert len(by)==len(rows) and set(by)==set(SOURCES)==set(identities)
    assert owner_hashes==OWNER
    assert spatial['sourceSHA256ByUid']=={u:s['sourceSHA256']for u,s in SOURCES.items()}
    assert len(spatial['sources'])==len(SOURCES) and {r['uid']for r in spatial['sources']}==set(SOURCES)
    assert {r['uid']for r in spatial['outsideGroupIntersections']}=={RELATED_NATIVE}
    assert len(spatial['outsideGroupIntersections'])==1
    related=spatial['outsideGroupIntersections'][0]
    assert related['buildingCSUID']=='1566329899T20080513'
    assert related['name']=='Tuen Mun Hospital Special Block'
    assert abs(related['intersectionAreaM2']-2.7291219468237284)<1e-12
    assert cell['targetUid']==MAIN and cell['providerUid']==CELL_PROVIDER and cell['allFourWorldTargetCellsCovered']is True
    assert cell['sourceSHA256ByUid']=={u:SOURCES[u]['sourceSHA256']for u in [MAIN,CELL_PROVIDER]}
    assert dependency['sourceSHA256ByUid']==spatial['sourceSHA256ByUid'] and dependency['acyclic']is True
    coverage={r['uid']:r for r in dependency['rows']};assert len(dependency['rows'])==len(SOURCES) and set(coverage)==set(SOURCES)
    assert CELL_PROVIDER in coverage[MAIN]['completeDependencyClosure']
    proofs={};raw={}
    for uid,row in by.items():
        expected=SOURCES[uid];f=row['source']['building'];identity=identities[uid]
        assert row['sourceSHA256']==expected['sourceSHA256']==identity['sourceSHA256']
        assert row['modelId']==expected['modelId'] and row['triangles']==expected['triangles']
        assert (f['buildingCSUID'],f['objectId'])==(expected['buildingCSUID'],expected['objectId'])
        assert expected['modelId'][1:11]==expected['buildingCSUID'][:10]
        assert set(identity['reasons'])<=OVERRIDABLE,'Unreviewed identity failure'
        if uid!=MAIN:assert 'original-source-does-not-cover-whole-georef-cell'not in identity['reasons']
        route=identity['exactCurrentComponentRoute']
        assert route['qualified']is True and route['reasons']==[]
        assert route['uid']==uid and route['source']==row['source']
        assert (route['official']['objectId'],route['official']['buildingCSUID'])==(expected['objectId'],expected['buildingCSUID'])
        assert identity['freshCurrentIdentity']['exactObjectAndCSUID']is True
        assert identity['originalOwnership']['sourceGraphVerified']is True
        assert identity['geographicCell']['targetCoversWholeCell']is True
        if uid!=MAIN:assert identity['geographicCell']['originalProjectionCoversWholeCell']is True
        measured=next(r for r in spatial['sources']if r['uid']==uid)
        assert measured['combinedTargetCoverage']>=.95 and measured['maximumSourceExtentFromGroupM']<=10
        assert coverage[uid]['closureCoverageFraction']>=.95
        raw[uid]=deepcopy(identity['reasons'])
        proofs[uid]=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    return dict(uids=list(SOURCES),identityAccepted=True,identityProofByUid=proofs,
                sourceSHA256ByUid=spatial['sourceSHA256ByUid'],rawIndividualIdentityReasons=raw,
                exactRelatedCurrentFormUids=sorted([*SOURCES,RELATED_NATIVE]),
                mainWholeCellProvider=CELL_PROVIDER,requiredSourceAvailability=dependency['proposedDependencies'],
                policy='exact-tuen-mun-original-hospital-compound-identity-v1',
                physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Exact named government component routes, unmodified source graphs, complete hospital compound projection, exact Main cell coverage by Block D, proposed closure coverage and reviewed first-party hospital/site context. Individual raw failures retained; only these source bytes and explicit related forms. No name invented for193881. Identity only: not source-support, terrain, architectural-interface, BASIC/native collision, browser, dependency acceptance or installation approval.')
