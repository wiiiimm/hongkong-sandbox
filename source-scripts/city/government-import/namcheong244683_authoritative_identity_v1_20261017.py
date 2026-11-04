"""Refresh exact government identity and whole-source proof; no publication."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import urllib.request,urllib.parse,json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-namcheong244683-authoritative-identity-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-namcheong244683-current-capture-v1-20261017'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),CAP/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==20645
 DOC.mkdir();LOCAL.mkdir();georef=row['modelId'][1:11];params=dict(f='json',where="GeoRefNo='"+georef+"'",outFields='*',returnGeometry='true',outSR='2326');url=URL+'?'+urllib.parse.urlencode(params);raw=urllib.request.urlopen(url,timeout=60).read();(DOC/'provider.json').write_bytes(raw);provider=json.loads(raw);assert not provider.get('error')and not provider.get('exceededTransferLimit');assert provider['spatialReference'].get('latestWkid',provider['spatialReference'].get('wkid'))==2326
 save(DOC/'provider.request.json',dict(url=URL,parameters=params,sha256=digest(raw),retrievedAt=datetime.now(timezone.utc).isoformat()))
 conv=module('nam_identity_converter',HERE.parent/'citywide-native/convert.py');byref=defaultdict(list)
 for feat in provider['features']:
  a=feat['attributes'];assert str(a['GeoRefNo'])==georef;byref[georef].append((feat,conv.official_shape(feat)))
 row['native']['model']['matching']=conv.match_source(tri.reshape(-1,3),row['modelId'],byref)
 helper=module('nam_authoritative_context',HERE/'xl-final-script-pass.py');lo=tri.min((0,1));hi=tri.max((0,1));forms=helper.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=helper.identity_context(row,tri,forms),neighbourTileHashes={url:digest((ROOT/'3d-viewer'/url).read_bytes())for _,_,url in forms});proof=verify_files(row,context,LOCAL/row['uid'].replace('/','-').replace(':','-'))
 save(DOC/'identity.json',dict(context=context,proof=proof));save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'summary.json',dict(passed=proof['passed'],reasons=proof['reasons'],fullAcceptance=False));print(proof['passed'],proof['reasons'],flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([*[ROOT/p for p in pins],*[ROOT/'3d-viewer'/url for _,_,url in forms],*[p for p in LOCAL.rglob('*')if p.is_file()],Path(conv.__file__),*[HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_georef_cell_identity_20261009.py','government_georef_cell_identity.py','original_source_ownership.py','component_type_resolution.py','routed_original_cell_identity.py']]])
 out=module('nam_auth_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong-fresh-authoritative-whole-source-identity-v1',refs,dict(uids=[row['uid']],identityPassed=proof['passed'],identityReasons=proof['reasons'],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
