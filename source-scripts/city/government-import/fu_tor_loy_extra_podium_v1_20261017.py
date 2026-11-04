"""Recover exact adjacent original podium and measure candidate contacts; no edits."""
import sys,uuid,zipfile,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import scan,acquire,_convert_one,canonical_bytes
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-fu-tor-loy-';BATCH=PREFIX+'extra-podium-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/265849:0'
def main():
 assert not DOC.exists()and not LOCAL.exists();prior=BASE/(PREFIX+'sheet-component-audit-v1-20261017');r=read(prior/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 m=read(prior/'gap-candidates.json.gz')['extraModels'][0];assert m['candidate']['uid']==UID
 claim=reservations.claim('fu-extra-podium-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  LOCAL.mkdir();DOC.mkdir();save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
  pinned=read(HERE/'local/government-xl-fu-tor-loy-supports-20261005/sheets/11-NW-19A/directory/result.json');folder=LOCAL/'sheets/11-NW-19A'
  current,_=scan(dict(SHEETNO='11-NW-19A',Format_glTF=pinned['sourceURL'],REVISIONDATE=pinned['revision']),folder/'directory')
  current['models']=[x for x in current['models']if x['modelId']==m['modelId']];assert len(current['models'])==1 and reservations.owns(lease)
  proof=acquire(current,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(parents=True)
  with zipfile.ZipFile(folder/'original/11-NW-19A.zip')as archive:
   converted=_convert_one(archive,archive.getinfo(m['sourceEntry']),folder/'decoded',packed,{},dict(modelId=m['modelId']))
  raw=canonical_bytes((packed/converted['asset']['asset']).read_bytes(),m['asset']['sha256']);assert len(raw)==m['asset']['bytes'];asset=LOCAL/m['asset']['asset'];asset.parent.mkdir(exist_ok=True);asset.write_bytes(raw)
  support=decode_original_world_triangles(raw);assert len(support)==m['triangles'];results=[]
  failures=BASE/(PREFIX+'nearest-interfaces-v1-20261017')/'nearest-surfaces.json.gz'
  for row in read(failures)['rows']:
   details=[]
   for f in row['rows']:
    if f['nearestDistanceM']<=.5:continue
    i,q,d=nearest(np.asarray(f['position']),support);details.append(dict(position=f['position'],priorPodiumDistanceM=f['nearestDistanceM'],extraPodiumFace=i,extraPodiumPoint=q.tolist(),extraPodiumDistanceM=d,withinHalfMetreNomination=d<=.5,exactSurfaceContact=d<=.001))
   results.append(dict(uid=row['uid'],rows=details,points=len(details),withinHalfMetre=sum(f['withinHalfMetreNomination']for f in details),exactContacts=sum(f['exactSurfaceContact']for f in details),minimumExtraDistanceM=min(f['extraPodiumDistanceM']for f in details)))
  save(DOC/'contacts.json.gz',dict(rows=results));summary=dict(sourceUid=UID,modelId=m['modelId'],sourceSHA256=digest(raw),sourceTriangles=len(support),sourcePreserved=True,rows=[{k:v for k,v in r.items()if k!='rows'}for r in results],receivedBytes=proof['newThisInvocationBytes'],fullAcceptance=False,qualification='Exact original support geometry compared with historical exact renderer failure positions. Nearest-distance nomination only; no current placement, support approval or installation claim.')
  save(DOC/'summary.json',summary);assert reservations.owns(lease)
  refs=[Path(__file__),prior/'result.json',prior/'gap-candidates.json.gz',failures,HERE/'exact_packed_world_geometry_20261009.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py',*[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json']]
  out=module('fu_extra_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-extra-podium-recovery-and-gap-contact-v1',refs,dict(uids=[UID]+[r['uid']for r in results],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
