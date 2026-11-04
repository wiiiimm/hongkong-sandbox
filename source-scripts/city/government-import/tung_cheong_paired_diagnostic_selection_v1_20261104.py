"""Prepare an explicitly unapproved two-original nomination, retaining the unmatched source."""
import copy,gzip,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request,BASE as URL
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tung-cheong-paired-diagnostic-selection-v1-20261104'
HIGH='government-xl-tung-cheong53799-post-inset-v1-20261103-runtime';LOW='government-xl-tung-cheong-low223636-exact-original-recovery-v2-20261103';SCOPE='government-xl-tung-cheong53799-post-inset-v1-20261103-scope'
UIDS=['landsd/53799:0','landsd/223636:0']

def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json';assert not out.exists()
    _,scope_pins=authenticate(BASE/SCOPE);fp=BASE/SCOPE/'form-obligations.json.gz';assert digest(fp.read_bytes())==scope_pins[str(fp.relative_to(ROOT))];forms=read(fp)
    resources=sorted({('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms}|{'terrain:city/data/terrain.json','terrain:city/data/government-native-tung-on-retained-original-20261026.json','immutable-source-proof:'+BATCH})
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('tung-cheong-private-pair-selection-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__),BASE/SCOPE/'result.json',fp];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selected=take(HIGH,'selection.json.gz');high=copy.deepcopy(selected['rows'][0]);low=take(LOW,'summary.json');assert high['uid']==UIDS[0]and low['viewerIdentityAssigned']is False and low['identityAccepted']is False
    by_uid={f['uid']:f for f in forms};assert all(u in by_uid for u in UIDS)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selected['manifestSHA256']==scope_pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;assert not set(UIDS)&{m['uid']for m in read(p)['models']};refs.append(p)
    model=low['model'];form=by_uid[UIDS[1]];assert form==low['currentForm']and form['buildingCSUID']=='3390811442T20050430'
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');sha,body=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(low['nativeCacheKey'],)).fetchone()
        assert sha==low['nativeResultSHA256']and next(m for m in body['models']if m['modelId']==model['modelId'])==model
        states=db.execute('SELECT viewer_uid,source_state FROM astra_modelling.native_model_sizes WHERE cache_key=%s AND model_id=%s',(low['nativeCacheKey'],model['modelId'])).fetchall();assert states==[(None,'source-match-held')]
    # Query both complete active GeoRef groups: do not infer uniqueness from a CSUID-filtered request.
    raw,receipt=request(URL+'/0/query',dict(f='json',where="GeoRefNo IN ('3391111439','3390811442') AND Status='Active'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'),json_expected=False)
    decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw;out.mkdir();(out/'active-georef-records.json').write_bytes(decoded);save(out/'active-georef-request.json',dict(**receipt,decodedSHA256=digest(decoded)))
    primary=read(out/'active-georef-records.json');assert not primary.get('error')and not primary.get('exceededTransferLimit');features=primary['features'];expected={'3391111439':'3391111439T20050430','3390811442':'3390811442T20050430'}
    assert len(features)==2 and {f['attributes']['GeoRefNo']:f['attributes']['BuildingCSUID']for f in features}==expected
    # The nomination keeps the real current form tuple so the unchanged loader can test it.
    # Empty native matches, rejected spatial/cell evidence and every approval stay unchanged.
    entry=dict(model['asset'],uid=form['uid'],objectId=form['objectId'],buildingCSUID=form['buildingCSUID'],recordedBaseHeight=form['baseHeightHKPD'],recordedTopHeight=form['topHeightHKPD'],modelId=model['modelId'],triangles=model['triangles'],worldBounds=model['worldBounds'],sourceTile='15-NW-3B',rootTranslation=[-834500,0,816500],priority='unreviewed')
    asset=ROOT/low['sourceAsset']['path'];assert digest(asset.read_bytes())==low['sourceSHA256'];refs.append(asset)
    tile=ROOT/'3d-viewer/city/data/tiles/-1_2.json';assert next(f for f in read(tile)['buildings']if f['uid']==form['uid'])==form;refs.append(tile)
    proposed=dict(uid=form['uid'],name=form['name'],modelId=model['modelId'],sourceSHA256=low['sourceSHA256'],triangles=44,currentReview=None,source=dict(building=form,tile='city/data/tiles/-1_2.json',tileSHA256=digest(tile.read_bytes())),native=dict(cacheKey=low['nativeCacheKey'],resultSha=low['nativeResultSHA256'],sheet='15-NW-3B',model=model),candidate=dict(entry=entry,path=str(asset.relative_to(ROOT))),diagnosticNominationOnly=True,nativeViewerUid=None)
    rows=[high,proposed]
    for row in rows:
        e=row['candidate']['entry'];assert e['sha256']==row['sourceSHA256']and e['uid']==row['uid']
        assert not e.get('supportDependencies')and not e.get('suppressesBuildingUids')
        e.update(activationGroup=sorted(UIDS),priority='unreviewed',proceduralWindows=False,sourceIdentityReviewed=False,identityReviewApproved=False,placementReviewed=False,publicationApproved=False)
        p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p)
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=mh,diagnosticOnly=True,sourceAssociationAccepted=False,atomicActivationRequired=sorted(UIDS)))
    result=dict(uids=UIDS,preparedUids=UIDS,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},currentManifestSHA256=mh,nativeLowViewerUid=None,nativeLowState='source-match-held',nativeMatchingRowsChanged=0,diagnosticNominationOnly=True,sourceAssociationAccepted=False,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,scriptExternalAICalls=0,atomicActivationRequired=sorted(UIDS),freshActiveGeoRefRecords=[f['attributes']for f in features],leaseResources=resources,qualification='Private two-original test nomination only. The low original remains unmatched on Neon. Both exact original assets use their current nominated form tuples with all approvals false; raw spatial/cell mismatches are not waived. Both must activate as one pair; no standalone low-source replacement or common legal ownership is inferred. Full paired runtime/identity/interface/browser and guarded publication remain required.')
    assert digest(manifest.read_bytes())==mh and reservations.owns(lease);save(out/'summary.json',result)
    refs.extend([HERE.parent/'landsd-territory/source.py',HERE/'original_supported_catalogue_scope_v1_20261024.py'])
    module('tung_cheong_unapproved_pair_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-two-original-current-form-nomination-no-native-assignment',list(dict.fromkeys(refs)),result)
    print(dict(prepared=UIDS,identityAccepted=False,publication=False),flush=True)
if __name__=='__main__':main()
