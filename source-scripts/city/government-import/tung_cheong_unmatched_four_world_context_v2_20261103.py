"""Four-world diagnostics of an explicit existing-form nomination; native match stays unassigned."""
import sys,uuid,subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tung-cheong-unmatched-four-world-context-v2-20261103'
HIGH='government-xl-tung-cheong53799-post-inset-v1-20261103-runtime';ATTR='government-xl-tung-cheong53799-post-inset-v1-20261103-attributes';LOW='government-xl-tung-cheong-low223636-exact-original-recovery-v2-20261103'

def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    low_result,low_pins=authenticate(BASE/LOW);sk=low_result['nativeCacheKey']+'/'+low_result['model']['modelId'];source_id='native-source:'+sk
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('unmatched-two-original-four-world-'+str(uuid.uuid4()),['building:landsd/53799:0','building:landsd/223636:0',source_id,'terrain:city/data/terrain.json','terrain:city/data/government-native-tung-on-retained-original-20261026.json','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    low=take(LOW,BASE/LOW/'summary.json');assert not low['viewerIdentityAssigned']and not low['identityAccepted'];m=low['model'];asset=ROOT/low['sourceAsset']['path'];assert digest(asset.read_bytes())==low['sourceSHA256'];refs.append(asset)
    selected=take(HIGH,BASE/HIGH/'selection.json.gz');high=selected['rows'][0];assert high['uid']=='landsd/53799:0'
    attrs=take(ATTR,BASE/ATTR/'attributes.json.gz');ha=attrs['rows'][0];assert ha['sourceSHA256']==high['sourceSHA256']
    captured=take(HIGH,HERE/'local'/HIGH/'runtime-geometry.json.gz')['rows'][0];ground=np.asarray(captured['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    # The unchanged real loader requires the actual nominated form tuple.
    # This private test neither edits native matching nor accepts that association.
    renderer_id=low['currentForm']['uid'];assert renderer_id=='landsd/223636:0'
    entry=dict(m['asset'],uid=renderer_id,objectId=low['currentForm']['objectId'],recordedBaseHeight=low['currentForm']['baseHeightHKPD'],recordedTopHeight=low['currentForm']['topHeightHKPD'],modelId=m['modelId'],buildingCSUID=low['currentForm']['buildingCSUID'],triangles=m['triangles'],worldBounds=m['worldBounds'],rootTranslation=[-834500,0,816500],sourceTile='15-NW-3B',priority='unreviewed',sourceIdentityReviewed=False,identityReviewApproved=False,placementReviewed=False,publicationApproved=False,proceduralWindows=False)
    input_path=out/'raw-renderer-input.json.gz';save(input_path,dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in read(manifest)['officialModelCatalogues']],evidenceRefs=[ref(BASE/LOW/'result.json')],expectedSourceByUid={renderer_id:[low['sourceSHA256'],44]},rows=[dict(uid=renderer_id,entry=entry,building=low['currentForm'],path=str(asset.relative_to(ROOT)))]))
    tool=HERE/'selected_original_render_attributes_v1.mjs';output=out/'raw-renderer-attributes.json.gz';refs.append(tool)
    with(out/'renderer.log').open('w')as log:subprocess.run(['node',str(tool),str(input_path.relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    la=read(output);assert la['startEndAllInputsVerified'];la=la['rows'][0];assert la['uid']==renderer_id and la['sourceSHA256']==low['sourceSHA256']
    highasset=ROOT/high['candidate']['path'];assert digest(highasset.read_bytes())==high['sourceSHA256'];refs.append(highasset)
    worlds=[('original',None),('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]
    final=module('unmatched_four_world_foundation',HERE/'xl-final-script-pass.py');rows=[];pair_cache={};foundation_cache={};foot=Polygon(low['currentForm']['rings'][0],low['currentForm']['rings'][1:])
    for mode,field in worlds:
        assert reservations.owns(lease)
        if field is None:a=decode_original_world_triangles(highasset.read_bytes());b=decode_original_world_triangles(asset.read_bytes())
        else:a=np.asarray(ha[field],dtype='<f8').reshape(-1,3)[np.asarray(ha['completeOriginalIndex']).reshape(-1,3)];b=np.asarray(la[field],dtype='<f8').reshape(-1,3)[np.asarray(la['completeOriginalIndex']).reshape(-1,3)]
        assert a.shape==(12158,3,3)and b.shape==(44,3,3)
        key=(digest(a.tobytes()),digest(b.tobytes()))
        if key not in pair_cache:pair_cache[key]=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))))
        proof=pair_cache[key];assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0
        save(out/(mode+'-pair.json.gz'),proof)
        if key[1]not in foundation_cache:foundation_cache[key[1]]=final.foundation_context(b,ground,foot)
        foundation=foundation_cache[key[1]];save(out/(mode+'-low-foundation.json'),foundation)
        rows.append(dict(mode=mode,sourceWorldSHA256s=list(key),pairFiniteContacts=len(proof['contacts']),pairPositiveSurfaceContacts=sum(c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in proof['contacts']),pairAreaContacts=sum(c['dimension']==2 for c in proof['contacts']),lowFoundation={k:v for k,v in foundation.items()if k!='components'}));print(rows[-1],flush=True)
    for name,h in read(output)['inputHashes'].items():assert digest((ROOT/name).read_bytes())==h;refs.append(ROOT/name)
    result=dict(uids=['landsd/53799:0'],sourceKeys=[sk],unmatchedViewerUid=None,rendererDiagnosticSourceKey=source_id,rendererNominationViewerUid=renderer_id,viewerIdentityAssigned=False,sourceSHA256s=[high['sourceSHA256'],low['sourceSHA256']],completeSourceFaces=[12158,44],completeCapturedGroundFaces=len(ground),completeGroundSHA256=digest(ground.tobytes()),rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,scriptExternalAICalls=0,qualification='Complete original, actual literal and two explicit Float32 renderer streams. The unchanged production loader verifies the complete actual nominated current form tuple. Its use is explicitly a private proposed source-to-form test, not an accepted association; the native source retains its NULL viewer UID and rejected raw matching. No catalogue, native matching row, BASIC geometry or approval changed. Low ground is the exact authenticated actual renderer ground captured for the high source; coverage failures remain explicit. All pair contacts remain unapproved. Identical arrays reuse exact measurements only.')
    assert reservations.owns(lease)and digest(manifest.read_bytes())==selected['manifestSHA256'];save(out/'summary.json',result)
    refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'xl-final-script-pass.py'])
    module('unmatched_two_original_four_world_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-unmatched-original-four-world-pair-and-foundations-no-assignment',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
