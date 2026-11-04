"""Private-only exact Peninsula pair/roof experiment; no generic flag exceptions."""
from copy import deepcopy
import hashlib,json
OWNER='landsd/270876:0';TOWER='landsd/266543:0';ROOF='way/709674357:0'
SOURCES={OWNER:'3a40860e5302240d814f907d2f1edabc4b3c7becab1c90d37f406d2a4ce631f2',TOWER:'4c40dd7918c6677d6fa564bb28daac019a8cd8af8d713897678ad03be27e3521'}
def form_sha(f):return hashlib.sha256(json.dumps(f,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def apply(models,forms,review):
    assert review['privateExperimentApproved']is True and review['publication']is False and review['installationApproved']is False
    assert review['sourceSHA256ByUid']==SOURCES=={m['uid']:m['sha256']for m in models}
    assert review['ownerUid']==OWNER and review['roofUid']==ROOF and review['activationGroup']==sorted(SOURCES)
    roof=forms[ROOF];assert roof==review['exactRoofForm']and form_sha(roof)==review['roofFormSHA256']
    assert roof['part']is True and roof['heightSource']=='levels'and roof['levels']==1 and roof['base']==5 and roof['height']==3.2
    assert roof['rings']==[[[1237.8,-850.1],[1238.3,-843.5],[1250.5,-844.4],[1249.9,-851.1],[1237.8,-850.1]]]
    osm=review['primaryOSMWay'];assert osm['passed']is True and osm['id']=='709674357'and osm['version']=='4'and osm['tags']=={'building:levels':'1','building:part':'roof','layer':'1'}
    for uid in SOURCES:assert form_sha(forms[uid])==review['sourceFormSHA256ByUid'][uid]
    result=deepcopy(models)
    for m in result:
        assert not m.get('suppressesBuildingUids')and not m.get('activationGroup')
        assert all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        m['activationGroup']=sorted(SOURCES)
        if m['uid']==OWNER:m['suppressesBuildingUids']=[ROOF]
    return result
