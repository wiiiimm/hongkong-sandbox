"""Stage source-bound BASIC continuations; native original geometry stays untouched."""
import copy
import hashlib
import json
import math
import re
import struct
from array import array
import sys
from basic_podium_footings import value_sha

POLICY='native-source-basic-ground-v1'
RECIPE='original-source-basic-ground-v1'
SHA=re.compile(r'^[a-f0-9]{64}$')
REQUIRED=('completeBasicCoreAttributesUnchanged','surveyedElevationsAndRoofUnchanged',
          'sameFootprintLowerContinuationOnly','nativeOriginalGeometryUnchanged',
          'sourcePreservedAtOneScale','fullFootprintHeightFieldCoverage',
          'existingNumericalFallbackOnly','sourceGradeReviewed','collisionReviewApproved',
          'visualReviewApproved','actualAtomicLifecyclePassed')


def drawn_ground_sha(terrain):
    """Match actual native Float32 triangles expanded to little-endian Float64."""
    mesh=terrain['nativeMesh'];positions=mesh['position'];indices=mesh['index']
    assert positions and len(positions)%3==0 and indices and len(indices)%3==0
    assert all(type(v)in(int,float)and math.isfinite(v)for v in positions)
    assert all(type(i)is int and 0<=i<len(positions)//3 for i in indices)
    f32=[struct.unpack('<f',struct.pack('<f',v))[0]for v in positions]
    values=array('d',(f32[i*3+a]for i in indices for a in range(3)))
    if sys.byteorder!='little':values.byteswap()
    return hashlib.sha256(values.tobytes()).hexdigest()


OWNER_FIELDS=('uid','objectId','buildingCSUID','sha256','recordedBaseHeight','recordedTopHeight','worldBounds','activationGroup','supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids','retainsBasicForm','footprintScope','proceduralWindows','rootTranslation','verticalPlacementOffsetHKPD')

def owner_contract_sha(model):
    return value_sha({k:model.get(k)for k in OWNER_FIELDS})

def validate_hint(b,hint):
    assert set(hint)=={'recipe','uid','sourceSHA256','terrainSHA256','drawnGroundSHA256','originalBottom','sourceMinimumY','base'}
    assert hint['recipe']==RECIPE and hint['uid']==b['uid']
    assert re.fullmatch(r'landsd/\d+:\d+',b['uid'])
    assert all(type(hint[k])is str and SHA.fullmatch(hint[k])for k in ['sourceSHA256','terrainSHA256','drawnGroundSHA256'])
    assert b['structureType']in ['Tower','Podium']and b.get('kind')!='roof'
    assert not b.get('modelGeometry')and 'foundationBase'not in b and b.get('foundationPolicy')is None
    assert b['baseSource']==b['heightSource']=='landsd'
    assert all(type(b[k])in(int,float)and math.isfinite(b[k])for k in ['base','height','baseHeightHKPD','topHeightHKPD'])
    minimum=b.get('minimum',0)
    if minimum is None:minimum=0
    assert type(minimum)in(int,float)and math.isfinite(minimum)and minimum>=0
    assert b['base']==b['baseHeightHKPD']and abs(b['base']+b['height']-b['topHeightHKPD'])<=1e-9
    assert b['buildingCSUID']and b['height']>0 and b['rings']
    assert all(type(hint[k])in(int,float)and math.isfinite(hint[k])for k in ['originalBottom','sourceMinimumY','base'])
    assert hint['originalBottom']==b['base']+minimum
    assert 1.2<=hint['base']<hint['originalBottom']-.02 and hint['base']>=hint['sourceMinimumY']-.5


def stage_native_basic_fallback_ground(root,plan,manifest,edits,report,load,sha,encoded):
    updates=plan.get('nativeBasicFallbackGrounds',[])
    registry=copy.deepcopy(manifest.get('nativeBasicFallbackGrounds',[]))
    if not updates and not registry:return
    assert isinstance(updates,list)and isinstance(registry,list)
    staged=dict(edits);working=copy.deepcopy(manifest);root=root.resolve()
    def local(path,under=None):
        p=(root/path).resolve();assert p.is_relative_to((under or root).resolve()),'Fallback path escaped its allowed root';return p
    def effective(path):return json.loads(staged[path])if path in staged else load(path)
    def bytes_sha(path):return hashlib.sha256(staged[path]).hexdigest()if path in staged else sha(path)
    def bound(ref):
        p=local(ref['path']);assert sha(p)==ref['sha256'],'Fallback review bytes changed';return load(p)
    owners={};suppressed=set()
    for url in working.get('officialModelCatalogues',[]):
        cat=effective(local('3d-viewer/'+url,root/'3d-viewer/city/data/official-models'))
        assert cat['rootTranslation']==[-834500,0,816500]and cat['crs']=='EPSG:2326'and cat['verticalDatum']=='Hong Kong Principal Datum'
        for model in cat['models']:
            assert model['uid']not in owners,'Duplicate native owner';owners[model['uid']]=model
            suppressed.update(model.get('suppressesBuildingUids',[]))
    terrain={t['url']:t for t in working.get('terrainPatches',[])};ground_cache={}
    def check_ground(item):
        url=item['terrainURL'];assert url in terrain,'Fallback terrain owner removed'
        path=local('3d-viewer/'+url,root/'3d-viewer/city/data');rawsha=bytes_sha(path)
        assert rawsha==item['hint']['terrainSHA256'],'Fallback terrain revision changed'
        if url not in ground_cache:ground_cache[url]=drawn_ground_sha(effective(path))
        assert ground_cache[url]==item['hint']['drawnGroundSHA256'],'Fallback drawn surface changed'
    def check_owner(uid,hint,b):
        assert uid in owners and uid not in suppressed,'Fallback owner missing or suppressed'
        m=owners[uid];assert m['sha256']==hint['sourceSHA256'],'Native source revision changed'
        assert m['objectId']==b['objectId']and m['buildingCSUID']==b['buildingCSUID']
        assert m['recordedBaseHeight']==b['baseHeightHKPD']and m['recordedTopHeight']==b['topHeightHKPD']
        assert m.get('retainsBasicForm')is not True,'Native original must replace its own BASIC geometry'
        assert m.get('verticalPlacementOffsetHKPD',0)==0,'Original native pose required'
        assert abs(m['worldBounds'][0][1]-hint['sourceMinimumY'])<=.002,'Native minimum disagrees'
    seen={r['uid']for r in registry};assert len(seen)==len(registry),'Duplicate retained fallback metadata'
    applied=[]
    for update in updates:
        uid=update['uid'];assert uid not in seen,'Fallback already registered or duplicated';seen.add(uid)
        tile=update['tile'];matches=[t for t in working['tiles']if t['url']==tile];assert len(matches)==1
        path=local('3d-viewer/'+tile,root/'3d-viewer/city/data/tiles');assert sha(path)==update['tileSHA256'],'Fallback tile changed'
        data=copy.deepcopy(effective(path));found=[b for b in data['buildings']if b['uid']==uid];assert len(found)==1
        b=found[0];assert b==update['before']and 'nativeFallbackGround'not in b,'Fallback source form changed'
        hint=update['hint'];validate_hint(b,hint);check_owner(uid,hint,b);check_ground(update)
        review=bound(update['evidence']);assert review['status']=='approved-for-integration'and review['policy']==POLICY
        assert review['uid']==uid and review['buildingCSUID']==b['buildingCSUID']
        assert review['sourceFormSHA256']==value_sha(b)and review['tileSHA256']==update['tileSHA256']
        assert review['hint']==hint and review['terrainURL']==update['terrainURL']
        assert review['ownerPlacementAndAvailabilitySHA256']==owner_contract_sha(owners[uid])
        assert all(review[k]is True for k in REQUIRED),'Missing qualified BASIC fallback evidence'
        assert review['sourceGeometryChanges']==review['governmentGeometryChanges']==0 and review['aiGeometryModelling']is False
        lo,hi=review['groundRangeHKPD'];assert all(type(v)in(int,float)and math.isfinite(v)for v in [lo,hi]);assert hint['base']==lo<=hi<b['topHeightHKPD']-.1
        b['nativeFallbackGround']=copy.deepcopy(hint);staged[path]=encoded(data);matches[0]['bytes']=len(staged[path])
        registry.append(dict(uid=uid,tile=tile,buildingCSUID=b['buildingCSUID'],policy=POLICY,hint=copy.deepcopy(hint),terrainURL=update['terrainURL'],retainedFormSHA256=value_sha(b),ownerPlacementAndAvailabilitySHA256=owner_contract_sha(owners[uid]),evidence=update['evidence'],nativeDetailMustIgnoreContinuation=True,sourceOrTerrainChangeRequiresRevalidation=True))
        applied.append(dict(uid=uid,base=hint['base'],evidence=update['evidence']))
    checked=[]
    for item in registry:
        assert item['policy']==POLICY and item['nativeDetailMustIgnoreContinuation']is True and item['sourceOrTerrainChangeRequiresRevalidation']is True
        path=local('3d-viewer/'+item['tile'],root/'3d-viewer/city/data/tiles');found=[b for b in effective(path)['buildings']if b['uid']==item['uid']];assert len(found)==1
        b=found[0];assert value_sha(b)==item['retainedFormSHA256']and b['buildingCSUID']==item['buildingCSUID']and b['nativeFallbackGround']==item['hint']
        validate_hint(b,item['hint']);check_owner(item['uid'],item['hint'],b);assert owner_contract_sha(owners[item['uid']])==item['ownerPlacementAndAvailabilitySHA256'],'Native placement or availability contract changed';check_ground(item);bound(item['evidence']);checked.append(item['uid'])
    working['nativeBasicFallbackGrounds']=registry;manifest.clear();manifest.update(working);edits.update(staged)
    report['nativeBasicFallbackGrounds']=applied;report['retainedNativeBasicFallbackGroundChecks']=checked
