"""Only stale descriptive georef.W may change; full payload equality proves scope."""
import copy,hashlib,json
OLD_TERRAIN='f367dc82a617357da96ddeb004d4e6aa75329ca237a5f5033ce3f21daf1f7848'
def encoded(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def bare(x):
    y=copy.deepcopy(x);y['nativeMesh'].pop('sourceOverlap');return y

def correct(patch,audit):
    assert hashlib.sha256(encoded(bare(patch))).hexdigest()==audit['stagedGeometrySha256']
    assert (patch['w'],patch['h'],patch['cell'])==(43,29,5)
    g=patch['meta']['georef'];assert g==dict(W=29,H=29,aE=5,aN=-5,bE=832022.5,bN=816537.5)
    assert len(patch['elev'])==len(patch['vegetation'])==len(patch['renderedElev'])==43*29
    new=copy.deepcopy(patch);new['meta']['georef']['W']=43
    assert_equivalent(patch,new)
    return new,dict(oldGeoref=g,newGeoref=new['meta']['georef'],changedJSONPaths=['meta.georef.W'],oldValue=29,newValue=43,allOtherPayloadValuesExactlyEqual=True,nativePositionIndexProvenanceUnusedAndAllGridValuesUnchanged=True,affineGeorefAndParentDomainUnchanged=True,noModelGeometryChanges=True,noNumericThresholdChanges=True,oldBareCanonicalSHA256=audit['stagedGeometrySha256'],newBareCanonicalSHA256=hashlib.sha256(encoded(bare(new))).hexdigest())

def assert_equivalent(old,new):
    expected=copy.deepcopy(old);expected['meta']['georef']['W']=43
    a=copy.deepcopy(new);a['nativeMesh']['sourceOverlap']=copy.deepcopy(old['nativeMesh']['sourceOverlap'])
    assert encoded(a)==encoded(expected),'Only georef.W and the fresh overlap evidence binding may differ byte-for-byte'
    assert new['meta']['georef']['W']==new['w']==43 and new['meta']['georef']['H']==new['h']==29
    approval_old=old['nativeMesh']['sourceOverlap'];approval_new=new['nativeMesh']['sourceOverlap']
    assert encoded({k:v for k,v in approval_new.items()if k not in ['evidencePath','evidenceSHA256']})==encoded({k:v for k,v in approval_old.items()if k not in ['evidencePath','evidenceSHA256']})
