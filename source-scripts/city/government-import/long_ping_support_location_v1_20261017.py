"""Locate unresolved original contacts and current nearby support footprints."""
from pathlib import Path
import numpy as np
from shapely.geometry import Point
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-long-ping-support-location-v1-20261017';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-long-ping-original-contacts-v1-20261017'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 x=read(PRIOR/'contacts.json');pts=[Point(p['position'][0],p['position'][2])for p in x['failures']if p['reason']=='rim-above-support'];assert len(pts)==33
 final=module('long_ping_support_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([-13805,-17790,-13760,-17720]);near=[]
 for b,poly,tile in forms:
  d=min(poly.distance(p)for p in pts)
  if d<20:near.append(dict(uid=b['uid'],name=b.get('name'),distanceM=d,building=b,tile=tile))
 save(DOC/'nearby-forms.json',near)
 rt=HERE/'local/government-xl-long-ping-candidate-physical-v2-20261017/runtime-geometry.json.gz';g=read(rt)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 # Exact original face bounds around the two column bases; diagnostic nomination only.
 boxes=[[-13785,-17767,-13778,-17760],[-13785,-17747,-13778,-17740]];faces=[]
 for bounds in boxes:
  a,b,c,d=bounds;mask=(t[:,:,0].max(1)>=a)&(t[:,:,0].min(1)<=c)&(t[:,:,2].max(1)>=b)&(t[:,:,2].min(1)<=d)&(t[:,:,1].min(1)<5.05)
  faces.append(dict(bounds=bounds,faceIndices=np.flatnonzero(mask).tolist(),triangles=t[mask].tolist()))
 save(DOC/'column-base-original-faces.json',faces)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'contacts.json',rt,HERE/'xl-final-script-pass.py']+[ROOT/p for p in pins]+[ROOT/'3d-viewer'/tile for _,_,tile in forms]
 out=module('long_ping_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-original-column-base-current-support-search-v1',list(set(refs)),dict(uids=[g['uid']],floatingSamples=33,nearbyOtherBuildingForms=[p['uid']for p in near if p['uid']!=g['uid']],searchRadiusM=20,remainingReason='original-column-bottoms-above-authenticated-terrain-with-no-nearby-separate-building-form',nextStep='Seek an authoritative separate non-building support surface or source revision for the two column bases; do not repeat unchanged TIN conversion or move/extend source columns. Nine original embedded contacts and overlapping OSM access actor also remain unresolved.',fullAcceptance=False))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
