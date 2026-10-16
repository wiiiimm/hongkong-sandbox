"""Fetch exact government identity records and verify all three unchanged Opus originals."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import urllib.request,urllib.parse,json,copy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-current-identity-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-opus-actual-render-attributes-v2-20261017'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists() and not LOCAL.exists();r=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json'];pins={x['path']:x['sha256'] for x in r['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 inp=consume(CAP/'input.json.gz');count=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json';require_remaining(count,'landsd/322573:0','e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764');refs += [count,HERE/'require_remaining_xl.py'];manifestpath=ROOT/inp['currentManifest']['path'];assert digest(manifestpath.read_bytes())==inp['currentManifest']['sha256'];manifest=read(manifestpath);refs.append(manifestpath)
 refs += [ROOT/x['path'] for x in inp['evidenceRefs'] if (ROOT/x['path']).is_file()]
 for x in inp['evidenceRefs']:assert digest((ROOT/x['path']).read_bytes())==x['sha256']
 DOC.mkdir();LOCAL.mkdir();georefs=sorted({x['entry']['modelId'][1:11] for x in inp['rows']});params=dict(f='json',where='GeoRefNo IN ('+','.join("'"+x+"'" for x in georefs)+')',outFields='*',returnGeometry='true',outSR='2326')
 raw=urllib.request.urlopen(URL+'?'+urllib.parse.urlencode(params),timeout=60).read();(DOC/'provider.json').write_bytes(raw);provider=json.loads(raw);assert not provider.get('error') and not provider.get('exceededTransferLimit');assert provider['spatialReference'].get('latestWkid',provider['spatialReference'].get('wkid'))==2326
 save(DOC/'provider.request.json',dict(url=URL,parameters=params,method='GET',sha256=digest(raw),retrievedAt=datetime.now(timezone.utc).isoformat()))
 conv=module('opus_identity_converter',HERE.parent/'citywide-native/convert.py');byref=defaultdict(list)
 for feat in provider['features']:
  a=feat['attributes'];assert str(a['GeoRefNo']) in georefs;feat['viewerUids']=[x['building'] for x in inp['rows'] if x['building']['objectId']==a['OBJECTID'] and x['building']['buildingCSUID']==a['BuildingCSUID']];byref[str(a['GeoRefNo'])].append((feat,conv.official_shape(feat)))
 helper=module('opus_identity_current',HERE/'xl-final-script-pass.py');rows=[];results=[]
 for source in inp['rows']:
  e=source['entry'];asset=ROOT/source['path'];assert digest(asset.read_bytes())==e['sha256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());matching=conv.match_source(tri.reshape(-1,3),e['modelId'],byref);b=source['building'];tile=next(t['url'] for t in manifest['tiles'] if t['id']==b['tile']);path=ROOT/'3d-viewer'/tile;assert b in read(path)['buildings'];refs.append(path)
  row=dict(uid=source['uid'],name=b.get('name'),modelId=e['modelId'],sourceSHA256=e['sha256'],triangles=len(tri),source=dict(building=b,tile=tile,tileSHA256=digest(path.read_bytes())),candidate=dict(path=source['path'],entry=e),native=dict(sheet='11-SW-14D',model=dict(modelId=e['modelId'],asset={k:e[k] for k in ['sha256','asset']},candidate=e,matching=matching,triangles=len(tri),worldBounds=e['worldBounds'])))
  rows.append(row);lo=tri.min((0,1));hi=tri.max((0,1));forms=helper.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=helper.identity_context(row,tri,forms),neighbourTileHashes={url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms});proof=verify_files(row,context,LOCAL/row['uid'].replace('/','-').replace(':','-'));save(DOC/(row['uid'].replace('/','-').replace(':','-')+'.json'),dict(context=context,proof=proof));refs.extend(ROOT/'3d-viewer'/url for _,_,url in forms);results.append(dict(uid=row['uid'],passed=proof['passed'],reasons=proof['reasons']));print(results[-1],flush=True)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest(manifestpath.read_bytes())));save(DOC/'summary.json',dict(rows=results,fullAcceptance=False,newlyInstalled=0));assert digest(manifestpath.read_bytes())==inp['currentManifest']['sha256']
 refs += [p for p in LOCAL.rglob('*') if p.is_file()]+[HERE/n for n in ['xl-final-script-pass.py','routed_original_cell_identity.py','exact_original_georef_cell_identity_20261009.py','exact_packed_world_geometry_20261009.py','government_georef_cell_identity.py','original_source_ownership.py','component_type_resolution.py']]+[Path(conv.__file__)]
 result=module('opus_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-fresh-authoritative-three-part-identity-v1',refs,dict(uids=[x['uid'] for x in rows],rows=results,fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
