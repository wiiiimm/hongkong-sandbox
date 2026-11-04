"""Bounded current official footbridge polygons around the exact two-root source.

Location context only. No name-only identity, source acceptance, geometry edits
or conclusion of absence for privately maintained bridges.
"""
import argparse,sys,uuid,urllib.parse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from observed_reserved_runner_v2_20261103 import execute_reserved
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source43101-primary-footbridge-context-v1-20261103'
SELECT='government-xl-source43101-current-selection-v1-20261029';PROVIDER='government-xl-after-sha-tin-43101-provider-roots-v1-20261029'
SERVICE='https://portal.csdi.gov.hk/server/rest/services/common/hyd_rcd_1632360512481_74705/MapServer'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        c=reservations.claim('source43101-primary-footbridge-'+str(uuid.uuid4()),['building:landsd/43101:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__),HERE/'exact_packed_world_geometry_v2_20261103.py',HERE.parent/'landmark-acquisition/acquire.py'];values={}
    for batch,name in [(SELECT,'selection.json.gz'),(PROVIDER,'summary.json')]:
        _,pins=authenticate(BASE/batch);p=BASE/batch/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',p]);values[batch]=read(p)
    row=values[SELECT]['rows'][0];proof=values[PROVIDER];asset=ROOT/row['candidate']['path'];assert row['uid']=='landsd/43101:0'and digest(asset.read_bytes())==row['sourceSHA256']==proof['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));envelope=[lo[0]+834500-25,816500-hi[2]-25,hi[0]+834500+25,816500-lo[2]+25]
    net=ac.Network(out/'transfer.json',cap=1_000_000)
    def get(name,url,maximum):
        raw,_=net.get(url,maximum);p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);value=read(p);assert 'error'not in value,value;refs.append(p);return value
    service=get('service.json',SERVICE+'?f=pjson',200_000);layers=service['layers'];assert any(x['id']==0 and x['name']=='STR_FB'and x['geometryType']=='esriGeometryPolygon'for x in layers)
    layer=get('layer.json',SERVICE+'/0?f=pjson',200_000);assert layer['geometryType']=='esriGeometryPolygon'and'Query'in layer['capabilities']
    params=dict(f='json',where='1=1',geometry=','.join(map(str,envelope)),geometryType='esriGeometryEnvelope',inSR=2326,outSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',resultRecordCount=100)
    url=SERVICE+'/0/query?'+urllib.parse.urlencode(params);features=get('nearby-footbridges.json',url,500_000);assert not features.get('exceededTransferLimit')and features['geometryType']=='esriGeometryPolygon';assert features['spatialReference'].get('latestWkid',features['spatialReference'].get('wkid'))==2326
    counts=[r['completeFaces']for r in proof['roots']];assert sum(counts)==len(tri)and len(counts)==2;pieces=np.split(tri,[counts[0]])
    import shapely
    projections=[shapely.union_all(shapely.polygons(t[:,:,[0,2]]))for t in pieces];measurements=[]
    for feature in features['features']:
        rings=feature['geometry']['rings'];result=dict(attributes=feature['attributes'],ringCount=len(rings),rootProjectionMeasurements=None)
        if len(rings)==1:
            polygon=shapely.Polygon([[p[0]-834500,816500-p[1]]for p in rings[0]])
            if polygon.is_valid and polygon.area>0:
                result['rootProjectionMeasurements']=[dict(root=proof['roots'][i]['name'],sourceProjectionAreaM2=p.area,officialFootbridgePolygonAreaM2=polygon.area,overlapM2=p.intersection(polygon).area,sourceProjectionCoveredFraction=p.intersection(polygon).area/p.area)for i,p in enumerate(projections)]
        measurements.append(result)
    assert reservations.owns(lease)and digest(asset.read_bytes())==row['sourceSHA256']
    summary=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],officialDataset='hyd_rcd_1632360512481_74705',officialDatasetPage='https://portal.csdi.gov.hk/csdi-webpage/dataset/hyd_rcd_1632360512481_74705',queryURL=url,queryEnvelopeHK1980=envelope,officialNearbyFootbridgeFeatures=len(features['features']),measurements=measurements,receivedBytes=net.data['receivedBytes'],capBytes=1_000_000,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,identityAccepted=False,physicalAcceptance=False,publication=False,permanentRejection=False,qualification=__doc__)
    save(out/'summary.json',summary);refs.extend(p for p in out.rglob('*')if p.is_file())
    module('source43101_primary_bridge_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-official-footbridge-polygons-exact-source-context',refs,summary)
    print(dict(features=len(features['features']),measurements=measurements,receivedBytes=net.data['receivedBytes']),flush=True)

if __name__=='__main__':main()
