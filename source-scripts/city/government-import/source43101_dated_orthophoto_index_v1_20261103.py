"""Bounded official TDOP index lookup around both unchanged original roots.

Index metadata does not date the separate XYZ imagery or approve source identity.
"""
import argparse,sys,uuid,urllib.parse,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source43101-dated-orthophoto-index-v1-20261103';PARENT='government-xl-after-sha-tin-43101-provider-roots-v1-20261029';SELECT='government-xl-source43101-current-selection-v1-20261029';SERVICE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1701762716904_4826/MapServer';UID='landsd/43101:0'

def owned():
    out=BASE/BATCH;local=HERE/'local'/BATCH;lease=read(local/'reservation.json');assert reservations.owns(lease)and shutil.disk_usage(local.parent).free>4_000_000;refs=[Path(__file__),HERE.parent/'landmark-acquisition/acquire.py'];values={}
    for batch,name in [(PARENT,'summary.json'),(SELECT,'selection.json.gz')]:
        _,pins=authenticate(BASE/batch);p=BASE/batch/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];values[batch]=read(p);refs.extend([BASE/batch/'result.json',p])
    proof=values[PARENT];source=values[SELECT]['rows'][0];assert source['uid']==UID and source['sourceSHA256']==proof['sourceSHA256']and proof['allProviderAndPackedWorldArraysEqual'];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==proof['sourceSHA256'];refs.append(asset);roots=proof['roots'];assert len(roots)==2 and sum(r['completeFaces']for r in roots)==24308
    envelope=[min(r['sourceWorldBounds'][0][0]for r in roots)+834500-1,816500-max(r['sourceWorldBounds'][1][2]for r in roots)-1,max(r['sourceWorldBounds'][1][0]for r in roots)+834500+1,816500-min(r['sourceWorldBounds'][0][2]for r in roots)+1]
    net=ac.Network(out/'transfer.json',cap=500_000);queries=[]
    def get(name,url,cap):
        raw,headers=net.get(url,cap);p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);refs.append(p);value=read(p);assert not value.get('error');queries.append(dict(url=url,path=str(p.relative_to(ROOT)),sha256=digest(raw),headers=headers));return value
    service=get('service.json',SERVICE+'?f=pjson',200_000);assert any(r['id']==0 and r['name']=='TDOP2025_GRID_INDEX'for r in service['layers'])
    layer=get('layer.json',SERVICE+'/0?f=pjson',100_000);assert layer['geometryType']=='esriGeometryPolygon'and'Query'in layer['capabilities']
    params=dict(f='json',where='1=1',geometry=','.join(map(str,envelope)),geometryType='esriGeometryEnvelope',inSR=2326,outSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',resultRecordCount=20)
    features=get('covering-grid-index.json',SERVICE+'/0/query?'+urllib.parse.urlencode(params),200_000);assert not features.get('exceededTransferLimit')and features['geometryType']=='esriGeometryPolygon'and features['spatialReference'].get('latestWkid',features['spatialReference'].get('wkid'))==2326
    result=dict(uids=[UID],sourceSHA256=proof['sourceSHA256'],bothOriginalRootsPreserved=True,allOriginalFaces=24308,queryEnvelopeHK1980=envelope,officialService=SERVICE,indexLayerName=layer['name'],coveringFeatures=features['features'],requests=queries,receivedBytes=net.data['receivedBytes'],capBytes=500000,indexOnly=True,rasterPayloadDownloaded=False,xyzAerialCaptureDateEstablished=False,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,permanentRejection=False,qualification='Current official TDOP grid metadata nominates dated primary raster sources. Its index year or tile attributes must not be transferred to the separate XYZ aerial acquired earlier. No raster pixels, source changes, missing-root/absence determination or installation acceptance.')
    save(out/'summary.json',result);refs.extend(p for p in out.iterdir()if p.is_file());assert reservations.owns(lease);module('source43101_dated_primary_index_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-current-official-dated-orthophoto-index-context',list(dict.fromkeys(refs)),result);print(dict(features=len(features['features']),fields=[f['name']for f in layer['fields']],receivedBytes=net.data['receivedBytes']),flush=True)
if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not(BASE/BATCH).exists()and not(HERE/'local'/BATCH).exists();c=reservations.claim('source43101-tdop-index-'+str(uuid.uuid4()),['building:'+UID,'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],'Source reservation unavailable';execute_reserved(c['reservation'],HERE/'local'/BATCH/'reservation.json',[sys.executable,__file__,'--owned'])
